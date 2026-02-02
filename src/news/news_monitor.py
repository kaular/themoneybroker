"""
News Monitoring Background Task
Überwacht kontinuierlich News und sendet Alerts bei wichtigen Ereignissen
"""

import asyncio
import logging
from datetime import datetime, UTC
from typing import Optional, List, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NewsMonitorConfig:
    """Konfiguration für News Monitor"""
    check_interval_seconds: int = 300  # 5 Minuten
    symbols: Optional[List[str]] = None  # None = alle verfügbaren
    min_confidence: float = 0.7  # Minimale Confidence für Alerts
    extreme_sentiment_threshold: float = 0.6  # |sentiment| > 0.6 = extrem
    enabled: bool = True


class NewsMonitor:
    """
    Background Task für kontinuierliches News-Monitoring
    
    Features:
    - Regelmäßige News-Abfrage
    - Alert bei wichtigen News
    - WebSocket Notifications
    - Performance-freundlich (cached article IDs)
    """
    
    def __init__(
        self,
        news_feed,
        config: NewsMonitorConfig = None,
        on_important_news: Optional[Callable] = None
    ):
        self.news_feed = news_feed
        self.config = config or NewsMonitorConfig()
        self.on_important_news = on_important_news
        
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.seen_article_ids = set()
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def start(self):
        """Startet den Background Monitor"""
        if self.is_running:
            self.logger.warning("News Monitor already running")
            return
        
        if not self.config.enabled:
            self.logger.info("News Monitor disabled in config")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._monitor_loop())
        self.logger.info(
            f"News Monitor started - checking every {self.config.check_interval_seconds}s"
        )
    
    async def stop(self):
        """Stoppt den Background Monitor"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("News Monitor stopped")
    
    async def _monitor_loop(self):
        """Haupt-Loop für News-Überwachung"""
        self.logger.info("News Monitor loop started")
        
        while self.is_running:
            try:
                await self._check_news()
                await asyncio.sleep(self.config.check_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in news monitor loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _check_news(self):
        """Prüft auf neue wichtige News"""
        try:
            # Hole aktuelle News
            articles = await self.news_feed.get_news(
                symbols=self.config.symbols,
                limit=50,
                hours_back=1  # Nur letzte Stunde
            )
            
            if not articles:
                return
            
            # Filter neue Artikel (noch nicht gesehen)
            new_articles = [
                article for article in articles
                if article.id not in self.seen_article_ids
            ]
            
            if not new_articles:
                return
            
            self.logger.debug(f"Found {len(new_articles)} new articles")
            
            # Markiere als gesehen
            for article in new_articles:
                self.seen_article_ids.add(article.id)
            
            # Cleanup alte IDs (behalte nur letzte 1000)
            if len(self.seen_article_ids) > 1000:
                # Remove oldest 200
                self.seen_article_ids = set(list(self.seen_article_ids)[-800:])
            
            # Finde wichtige News
            important_articles = self._filter_important_news(new_articles)
            
            if important_articles:
                self.logger.info(f"Found {len(important_articles)} important news")
                await self._handle_important_news(important_articles)
            
        except Exception as e:
            self.logger.error(f"Error checking news: {e}", exc_info=True)
    
    def _filter_important_news(self, articles) -> list:
        """
        Filtert wichtige News nach Kriterien
        
        Kriterien:
        - Hohe Confidence (>= min_confidence)
        - Extremes Sentiment (sehr bullish oder bearish)
        - Multiple Symbole (breiter Impact)
        """
        important = []
        
        for article in articles:
            if not article.sentiment:
                continue
            
            sentiment = article.sentiment
            
            # Kriterium 1: Hohe Confidence
            if sentiment.confidence < self.config.min_confidence:
                continue
            
            # Kriterium 2: Extremes Sentiment
            if abs(sentiment.score) < self.config.extreme_sentiment_threshold:
                continue
            
            # Kriterium 3: Optional - Multiple Symbole = höhere Relevanz
            # (Ein Artikel über 5 Symbole ist wichtiger als über 1)
            symbol_count = len(article.symbols) if article.symbols else 0
            
            # Boost Score bei vielen Symbolen
            importance_score = (
                abs(sentiment.score) * 
                sentiment.confidence * 
                (1 + (symbol_count * 0.1))  # 10% Bonus pro Symbol
            )
            
            if importance_score >= 0.5:  # Threshold für "wichtig"
                important.append(article)
        
        # Sortiere nach Importance
        important.sort(
            key=lambda a: abs(a.sentiment.score) * a.sentiment.confidence,
            reverse=True
        )
        
        return important
    
    async def _handle_important_news(self, articles: list):
        """Verarbeitet wichtige News (Alerts, Callbacks)"""
        for article in articles:
            try:
                # Alert senden (via NewsFeed's _check_news_alerts)
                await self.news_feed._check_news_alerts([article])
                
                # Callback aufrufen (z.B. WebSocket notification)
                if self.on_important_news:
                    await self.on_important_news(article)
                
            except Exception as e:
                self.logger.error(f"Error handling important news: {e}")
    
    def update_config(self, config: NewsMonitorConfig):
        """Aktualisiert die Monitor-Konfiguration"""
        self.config = config
        self.logger.info(f"News Monitor config updated: {config}")
    
    def get_stats(self) -> dict:
        """Gibt Statistiken zurück"""
        return {
            "is_running": self.is_running,
            "check_interval": self.config.check_interval_seconds,
            "seen_articles": len(self.seen_article_ids),
            "monitoring_symbols": self.config.symbols or "all",
            "enabled": self.config.enabled
        }
