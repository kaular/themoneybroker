"""
Tests für News Feed System
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, UTC
from src.news.sentiment_analyzer import SentimentAnalyzer, SentimentResult
from src.news.news_feed import NewsFeed, NewsArticle, NewsSentiment
from src.news.news_monitor import NewsMonitor, NewsMonitorConfig


class TestSentimentAnalyzer:
    """Tests für Sentiment Analysis"""
    
    def setup_method(self):
        self.analyzer = SentimentAnalyzer()
    
    def test_bullish_sentiment(self):
        """Test: Bullish Sentiment Detection"""
        text = "Stock surges on breakthrough earnings, rally continues"
        result = self.analyzer.analyze(text)
        
        assert result.score > 0.5
        assert result.label == "bullish"
        assert result.confidence > 0
        assert len(result.keywords) > 0
    
    def test_bearish_sentiment(self):
        """Test: Bearish Sentiment Detection"""
        text = "Company stock plunges after lawsuit, losses mount"
        result = self.analyzer.analyze(text)
        
        assert result.score < -0.5
        assert result.label == "bearish"
        assert result.confidence > 0
    
    def test_neutral_sentiment(self):
        """Test: Neutral Sentiment"""
        text = "Company announces quarterly results"
        result = self.analyzer.analyze(text)
        
        assert abs(result.score) < 0.3
        assert result.label == "neutral"
    
    def test_negation_handling(self):
        """Test: Negation Handling"""
        text = "Not bullish, company fails to deliver"
        result = self.analyzer.analyze(text)
        
        assert result.score < 0  # Should be negative
    
    def test_intensifier_handling(self):
        """Test: Intensifiers boost sentiment"""
        text1 = "Stock rises on good earnings"
        text2 = "Stock surges dramatically on breakthrough earnings"
        
        result1 = self.analyzer.analyze(text1)
        result2 = self.analyzer.analyze(text2)
        
        # Both should be positive
        assert result1.score > 0
        assert result2.score > 0
        # Text2 should have more keywords or higher confidence
        assert len(result2.keywords) >= len(result1.keywords) or result2.confidence >= result1.confidence
    
    def test_headline_confidence_boost(self):
        """Test: Headlines get confidence boost"""
        text = "Stock surges on breakthrough"
        
        result_normal = self.analyzer.analyze(text)
        result_headline = self.analyzer.analyze_headline(text)
        
        # Both should detect sentiment
        assert result_normal.score > 0
        assert result_headline.score > 0
        # Headline should have higher confidence
        assert result_headline.confidence >= result_normal.confidence
    
    def test_batch_analysis(self):
        """Test: Batch Analysis"""
        texts = [
            "Stock surges on breakthrough",
            "Company plunges after lawsuit",
            "Quarterly results announced"
        ]
        
        results = self.analyzer.batch_analyze(texts)
        
        assert len(results) == 3
        assert results[0].label == "bullish"
        assert results[1].label == "bearish"
    
    def test_aggregate_sentiment(self):
        """Test: Aggregate Sentiment Calculation"""
        texts = [
            "Very bullish breakthrough",
            "Strong rally continues",
            "Stock declines"
        ]
        
        aggregate = self.analyzer.get_aggregate_sentiment(texts)
        
        assert aggregate.score > 0  # More bullish than bearish
        assert aggregate.label in ["bullish", "bearish", "neutral"]


@pytest.mark.asyncio
class TestNewsFeed:
    """Tests für News Feed"""
    
    def setup_method(self):
        self.broker = Mock()
        self.alert_manager = Mock()
        self.news_feed = NewsFeed(self.broker, self.alert_manager)
    
    async def test_news_feed_initialization(self):
        """Test: News Feed Initialization"""
        assert self.news_feed.broker is not None
        assert self.news_feed.sentiment_analyzer is not None
    
    async def test_calculate_news_score(self):
        """Test: News Score Calculation"""
        # Mock articles with sentiment
        articles = [
            Mock(
                sentiment=Mock(score=0.8, confidence=0.9, label="bullish"),
                symbols=['TSLA', 'NVDA']
            ),
            Mock(
                sentiment=Mock(score=0.6, confidence=0.8, label="bullish"),
                symbols=['TSLA']
            )
        ]
        
        score = self.news_feed.calculate_news_score("TSLA", articles)
        
        assert 0 <= score <= 100
        assert score > 50  # Should be bullish
    
    async def test_get_sentiment_summary(self):
        """Test: Sentiment Summary"""
        articles = [
            Mock(sentiment=Mock(score=0.7, label="bullish", confidence=0.8)),
            Mock(sentiment=Mock(score=0.5, label="bullish", confidence=0.7)),
            Mock(sentiment=Mock(score=-0.6, label="bearish", confidence=0.8)),
            Mock(sentiment=Mock(score=0.1, label="neutral", confidence=0.5))
        ]
        
        summary = self.news_feed.get_sentiment_summary(articles)
        
        assert summary['total_articles'] == 4
        assert summary['bullish_count'] == 2
        assert summary['bearish_count'] == 1
        assert summary['neutral_count'] == 1
        assert summary['overall_sentiment'] in ['bullish', 'bearish', 'neutral']


@pytest.mark.asyncio
class TestNewsMonitor:
    """Tests für News Monitor"""
    
    def setup_method(self):
        self.news_feed = Mock()
        self.config = NewsMonitorConfig(
            check_interval_seconds=60,
            symbols=['TSLA', 'NVDA'],
            min_confidence=0.7
        )
        self.monitor = NewsMonitor(self.news_feed, self.config)
    
    async def test_monitor_initialization(self):
        """Test: Monitor Initialization"""
        assert self.monitor.config.check_interval_seconds == 60
        assert self.monitor.config.symbols == ['TSLA', 'NVDA']
        assert not self.monitor.is_running
    
    async def test_monitor_start_stop(self):
        """Test: Monitor Start/Stop"""
        await self.monitor.start()
        assert self.monitor.is_running
        
        await self.monitor.stop()
        assert not self.monitor.is_running
    
    async def test_filter_important_news(self):
        """Test: Important News Filtering"""
        # High confidence, extreme sentiment = important
        important = Mock(
            sentiment=Mock(score=0.8, confidence=0.9, label="bullish"),
            symbols=['TSLA']
        )
        
        # Low confidence = not important
        not_important = Mock(
            sentiment=Mock(score=0.5, confidence=0.3, label="bullish"),
            symbols=['NVDA']
        )
        
        articles = [important, not_important]
        filtered = self.monitor._filter_important_news(articles)
        
        assert len(filtered) == 1
        assert filtered[0] == important
    
    def test_get_stats(self):
        """Test: Monitor Statistics"""
        stats = self.monitor.get_stats()
        
        assert 'is_running' in stats
        assert 'check_interval' in stats
        assert 'monitoring_symbols' in stats
        assert stats['monitoring_symbols'] == ['TSLA', 'NVDA']
