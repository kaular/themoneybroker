"""
News Feed - Real-time Finanznachrichten

Quellen:
- Alpaca News API (kostenlos mit Broker)
- NewsAPI.org (optional)
- RSS Feeds (optional)

Features:
- Real-time News Stream
- Sentiment Analysis
- Symbol-spezifische News
- News-basierte Alerts
- News-Score für Scanner Integration
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum

from .sentiment_analyzer import SentimentAnalyzer, SentimentResult

logger = logging.getLogger(__name__)


class NewsSentiment(Enum):
    """News sentiment classification"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class NewsArticle:
    """News article data"""
    id: str
    headline: str
    summary: str
    author: str
    created_at: datetime
    updated_at: datetime
    url: str
    symbols: List[str]
    source: str
    sentiment: Optional[SentimentResult] = None
    
    def __post_init__(self):
        """Analyze sentiment after initialization"""
        if self.sentiment is None and hasattr(self, '_analyzer'):
            self._analyze_sentiment()
    
    def _analyze_sentiment(self):
        """Analyze article sentiment"""
        if not hasattr(self, '_analyzer'):
            return
        
        # Analyze headline (more weight) and summary
        headline_sentiment = self._analyzer.analyze_headline(self.headline)
        summary_sentiment = self._analyzer.analyze(self.summary)
        
        # Weighted average (headline 60%, summary 40%)
        combined_score = (headline_sentiment.score * 0.6) + (summary_sentiment.score * 0.4)
        combined_confidence = (headline_sentiment.confidence * 0.6) + (summary_sentiment.confidence * 0.4)
        
        # Combine keywords
        all_keywords = list(set(headline_sentiment.keywords + summary_sentiment.keywords))
        
        # Determine label
        if combined_score > 0.2:
            label = 'bullish'
        elif combined_score < -0.2:
            label = 'bearish'
        else:
            label = 'neutral'
        
        self.sentiment = SentimentResult(
            score=combined_score,
            label=label,
            confidence=combined_confidence,
            keywords=all_keywords
        )
    
    def get_sentiment_emoji(self) -> str:
        """Get emoji for sentiment"""
        if not self.sentiment:
            return '📰'
        
        if self.sentiment.label == 'bullish':
            if self.sentiment.score > 0.6:
                return '🚀'
            return '📈'
        elif self.sentiment.label == 'bearish':
            if self.sentiment.score < -0.6:
                return '💥'
            return '📉'
        return '➡️'


class NewsFeed:
    """
    News Feed Manager
    
    Fetches and processes financial news from multiple sources
    """
    
    def __init__(self, broker, alert_manager=None):
        """
        Initialize news feed
        
        Args:
            broker: Broker instance with news API access
            alert_manager: Optional AlertManager for news alerts
        """
        self.broker = broker
        self.alert_manager = alert_manager
        self.sentiment_analyzer = SentimentAnalyzer()
        self.news_cache: Dict[str, List[NewsArticle]] = {}
        self.last_fetch: Dict[str, datetime] = {}
    
    async def get_news(self, symbols: List[str] = None, 
                       limit: int = 50,
                       hours_back: int = 24) -> List[NewsArticle]:
        """
        Get latest news for symbols
        
        Args:
            symbols: List of symbols (None = general market news)
            limit: Max articles to return
            hours_back: How many hours back to fetch
        
        Returns:
            List of NewsArticle objects with sentiment
        """
        try:
            # Fetch from Alpaca News API
            start_time = datetime.now() - timedelta(hours=hours_back)
            
            if hasattr(self.broker, 'get_news'):
                # Alpaca has news API
                news_data = await self.broker.get_news(
                    symbols=symbols,
                    start=start_time.isoformat(),
                    limit=limit
                )
            else:
                logger.warning("Broker does not support news API")
                return []
            
            # Convert to NewsArticle objects
            articles = []
            for item in news_data:
                article = NewsArticle(
                    id=str(item.id),
                    headline=item.headline,
                    summary=item.summary,
                    author=item.author,
                    created_at=datetime.fromisoformat(item.created_at.replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(item.updated_at.replace('Z', '+00:00')),
                    url=item.url,
                    symbols=item.symbols if hasattr(item, 'symbols') else [],
                    source=item.source if hasattr(item, 'source') else 'Alpaca'
                )
                
                # Analyze sentiment
                article._analyzer = self.sentiment_analyzer
                article._analyze_sentiment()
                
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} news articles")
            
            # Cache results
            cache_key = ','.join(symbols) if symbols else 'general'
            self.news_cache[cache_key] = articles
            self.last_fetch[cache_key] = datetime.now()
            
            # Send alerts for high-impact news
            if self.alert_manager and symbols:
                await self._check_news_alerts(articles, symbols)
            
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    async def get_symbol_news(self, symbol: str, limit: int = 20) -> List[NewsArticle]:
        """
        Get news for specific symbol
        
        Args:
            symbol: Stock symbol
            limit: Max articles
        
        Returns:
            List of NewsArticle
        """
        return await self.get_news(symbols=[symbol], limit=limit)
    
    async def get_market_news(self, limit: int = 50) -> List[NewsArticle]:
        """
        Get general market news
        
        Args:
            limit: Max articles
        
        Returns:
            List of NewsArticle
        """
        # Fetch news for major indices
        return await self.get_news(symbols=['SPY', 'QQQ', 'DIA'], limit=limit)
    
    def get_sentiment_summary(self, articles: List[NewsArticle]) -> Dict:
        """
        Get aggregate sentiment from articles
        
        Args:
            articles: List of NewsArticle
        
        Returns:
            Dict with sentiment summary
        """
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
        
        bullish = [a for a in articles if a.sentiment and a.sentiment.label == 'bullish']
        bearish = [a for a in articles if a.sentiment and a.sentiment.label == 'bearish']
        neutral = [a for a in articles if a.sentiment and a.sentiment.label == 'neutral']
        
        # Weighted average sentiment
        total_weight = sum(a.sentiment.confidence for a in articles if a.sentiment)
        if total_weight == 0:
            avg_score = 0.0
        else:
            avg_score = sum(
                a.sentiment.score * a.sentiment.confidence 
                for a in articles if a.sentiment
            ) / total_weight
        
        # Determine overall sentiment
        if avg_score > 0.3:
            overall = 'bullish'
        elif avg_score < -0.3:
            overall = 'bearish'
        else:
            overall = 'neutral'
        
        return {
            'overall_sentiment': overall,
            'sentiment_score': avg_score,
            'confidence': total_weight / len(articles) if articles else 0.0,
            'bullish_count': len(bullish),
            'bearish_count': len(bearish),
            'neutral_count': len(neutral),
            'total_articles': len(articles),
            'bullish_pct': len(bullish) / len(articles) * 100 if articles else 0,
            'bearish_pct': len(bearish) / len(articles) * 100 if articles else 0
        }
    
    async def _check_news_alerts(self, articles: List[NewsArticle], symbols: List[str]):
        """Check for high-impact news and send alerts"""
        for article in articles:
            if not article.sentiment:
                continue
            
            # Alert on high confidence extreme sentiment
            if article.sentiment.confidence > 0.7:
                if article.sentiment.score > 0.6:
                    # Very bullish news
                    await self._send_news_alert(
                        article, 
                        "🚀 VERY BULLISH NEWS", 
                        'high'
                    )
                elif article.sentiment.score < -0.6:
                    # Very bearish news
                    await self._send_news_alert(
                        article, 
                        "💥 VERY BEARISH NEWS", 
                        'high'
                    )
    
    async def _send_news_alert(self, article: NewsArticle, title: str, priority: str):
        """Send news alert"""
        if not self.alert_manager:
            return
        
        from src.alerts import Alert, AlertType
        
        alert = Alert(
            type=AlertType.MOONSHOT_FOUND,  # Reuse moonshot type for news
            title=title,
            message=f"{article.get_sentiment_emoji()} {article.headline}",
            priority=priority,
            timestamp=datetime.now(),
            data={
                'Symbols': ', '.join(article.symbols),
                'Sentiment': f"{article.sentiment.label.upper()} ({article.sentiment.score:.2f})",
                'Confidence': f"{article.sentiment.confidence:.1%}",
                'Source': article.source,
                'URL': article.url
            }
        )
        
        await self.alert_manager.send_alert(alert)
    
    def calculate_news_score(self, symbol: str, articles: List[NewsArticle]) -> float:
        """
        Calculate news score for Growth Scanner integration
        
        Args:
            symbol: Stock symbol
            articles: News articles for the symbol
        
        Returns:
            Score 0-100 (positive news = higher score)
        """
        if not articles:
            return 50.0  # Neutral baseline
        
        # Filter to symbol-specific news
        symbol_articles = [
            a for a in articles 
            if symbol in a.symbols
        ]
        
        if not symbol_articles:
            return 50.0
        
        # Get sentiment summary
        summary = self.get_sentiment_summary(symbol_articles)
        
        # Convert sentiment score (-1 to +1) to 0-100 scale
        # -1.0 -> 0, 0.0 -> 50, +1.0 -> 100
        score = (summary['sentiment_score'] + 1.0) * 50.0
        
        # Adjust by confidence
        score = (score * summary['confidence']) + (50.0 * (1 - summary['confidence']))
        
        # Boost for high article count (more news = more attention)
        if len(symbol_articles) > 10:
            score *= 1.1
        elif len(symbol_articles) > 20:
            score *= 1.2
        
        # Cap at 0-100
        return max(0.0, min(100.0, score))
    
    async def monitor_news_stream(self, symbols: List[str], 
                                  callback=None, 
                                  interval_seconds: int = 300):
        """
        Monitor news stream in background
        
        Args:
            symbols: Symbols to monitor
            callback: Function to call with new articles
            interval_seconds: Check interval (default 5 minutes)
        """
        logger.info(f"Starting news monitor for {len(symbols)} symbols")
        
        while True:
            try:
                articles = await self.get_news(symbols=symbols, hours_back=1)
                
                if callback and articles:
                    await callback(articles)
                
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                logger.error(f"News monitor error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
