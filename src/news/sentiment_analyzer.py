"""
Sentiment Analyzer - NLP für Finanznachrichten

Analysiert Sentiment aus News-Texten:
- Positive News -> Bullish Signal
- Negative News -> Bearish Signal
- Neutral News -> Hold

Verwendet:
- Keyword-basierte Analyse
- Finanz-spezifische Begriffe
- Scoring -1.0 (sehr negativ) bis +1.0 (sehr positiv)
"""

import re
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    score: float  # -1.0 to +1.0
    label: str  # 'bullish', 'bearish', 'neutral'
    confidence: float  # 0.0 to 1.0
    keywords: List[str]


class SentimentAnalyzer:
    """
    Sentiment Analyzer für Finanznachrichten
    
    Verwendet Keyword-basierte Analyse mit Finanz-Vokabular
    """
    
    # Positive Keywords (Bullish)
    POSITIVE_KEYWORDS = {
        # Growth & Performance
        'surge', 'soar', 'rally', 'gain', 'jump', 'spike', 'climb', 'rise',
        'breakout', 'breakthrough', 'record', 'beat', 'exceed', 'outperform',
        'strong', 'robust', 'solid', 'impressive', 'stellar',
        
        # Financial
        'profit', 'revenue', 'earnings', 'growth', 'expansion', 'upgrade',
        'dividend', 'buyback', 'acquisition', 'merger', 'deal',
        
        # Innovation
        'innovation', 'revolutionary', 'breakthrough', 'disruptive', 'game-changer',
        'patent', 'technology', 'cutting-edge', 'advanced',
        
        # Sentiment
        'bullish', 'optimistic', 'confident', 'positive', 'promising',
        'excited', 'opportunity', 'potential', 'success'
    }
    
    # Negative Keywords (Bearish)
    NEGATIVE_KEYWORDS = {
        # Decline & Loss
        'plunge', 'crash', 'fall', 'drop', 'decline', 'tumble', 'slump',
        'collapse', 'sink', 'slide', 'dip', 'loss', 'losses',
        
        # Problems
        'miss', 'disappoint', 'warning', 'concern', 'issue', 'problem',
        'risk', 'threat', 'challenge', 'struggle', 'fail', 'failure',
        'weakness', 'vulnerable', 'exposed',
        
        # Legal & Regulatory
        'lawsuit', 'investigation', 'fraud', 'scandal', 'violation',
        'fine', 'penalty', 'regulation', 'ban', 'restriction',
        
        # Market
        'downgrade', 'cut', 'reduce', 'layoff', 'bankruptcy', 'default',
        'debt', 'deficit', 'shortfall',
        
        # Sentiment
        'bearish', 'pessimistic', 'negative', 'worried', 'fear', 'panic'
    }
    
    # Intensifiers (multiply sentiment)
    INTENSIFIERS = {
        'very': 1.5,
        'extremely': 2.0,
        'highly': 1.5,
        'significantly': 1.5,
        'substantially': 1.5,
        'massive': 2.0,
        'huge': 1.8,
        'major': 1.5,
        'minor': 0.5,
        'slight': 0.5,
        'somewhat': 0.7
    }
    
    # Negations (flip sentiment)
    NEGATIONS = {
        'not', 'no', 'never', 'none', 'nothing', 'neither', 'nor',
        'without', 'lack', 'lacking', 'fails', 'failed'
    }
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        self.positive_words = self.POSITIVE_KEYWORDS
        self.negative_words = self.NEGATIVE_KEYWORDS
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text
        
        Args:
            text: News article text or headline
        
        Returns:
            SentimentResult with score, label, confidence
        """
        if not text:
            return SentimentResult(
                score=0.0,
                label='neutral',
                confidence=0.0,
                keywords=[]
            )
        
        # Normalize text
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Calculate sentiment
        positive_score = 0.0
        negative_score = 0.0
        found_keywords = []
        
        for i, word in enumerate(words):
            # Check for negation before this word
            negated = False
            if i > 0 and words[i-1] in self.NEGATIONS:
                negated = True
            
            # Check for intensifier before this word
            intensifier = 1.0
            if i > 0 and words[i-1] in self.INTENSIFIERS:
                intensifier = self.INTENSIFIERS[words[i-1]]
            
            # Calculate sentiment
            if word in self.positive_words:
                score = 1.0 * intensifier
                if negated:
                    score = -score
                    negative_score += abs(score)
                else:
                    positive_score += score
                found_keywords.append(word)
            
            elif word in self.negative_words:
                score = -1.0 * intensifier
                if negated:
                    score = -score
                    positive_score += abs(score)
                else:
                    negative_score += abs(score)
                found_keywords.append(word)
        
        # Calculate final score
        total_keywords = len(found_keywords)
        if total_keywords == 0:
            return SentimentResult(
                score=0.0,
                label='neutral',
                confidence=0.0,
                keywords=[]
            )
        
        net_score = positive_score - negative_score
        # Normalize to -1.0 to +1.0
        normalized_score = max(-1.0, min(1.0, net_score / max(total_keywords, 1)))
        
        # Determine label
        if normalized_score > 0.2:
            label = 'bullish'
        elif normalized_score < -0.2:
            label = 'bearish'
        else:
            label = 'neutral'
        
        # Calculate confidence based on number of keywords
        confidence = min(1.0, total_keywords / 10.0)
        
        return SentimentResult(
            score=normalized_score,
            label=label,
            confidence=confidence,
            keywords=found_keywords[:10]  # Top 10 keywords
        )
    
    def analyze_headline(self, headline: str) -> SentimentResult:
        """
        Analyze sentiment of headline (typically shorter, weight more heavily)
        
        Args:
            headline: News headline
        
        Returns:
            SentimentResult
        """
        result = self.analyze(headline)
        # Headlines are more impactful, boost confidence
        result.confidence = min(1.0, result.confidence * 1.3)
        return result
    
    def batch_analyze(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze multiple texts
        
        Args:
            texts: List of text strings
        
        Returns:
            List of SentimentResult
        """
        return [self.analyze(text) for text in texts]
    
    def get_aggregate_sentiment(self, texts: List[str]) -> SentimentResult:
        """
        Get aggregate sentiment from multiple texts
        
        Args:
            texts: List of text strings (e.g., multiple news articles)
        
        Returns:
            Aggregated SentimentResult
        """
        if not texts:
            return SentimentResult(
                score=0.0,
                label='neutral',
                confidence=0.0,
                keywords=[]
            )
        
        results = self.batch_analyze(texts)
        
        # Weighted average by confidence
        total_weight = sum(r.confidence for r in results)
        if total_weight == 0:
            avg_score = 0.0
        else:
            avg_score = sum(r.score * r.confidence for r in results) / total_weight
        
        # Aggregate keywords
        all_keywords = []
        for r in results:
            all_keywords.extend(r.keywords)
        unique_keywords = list(set(all_keywords))
        
        # Determine label
        if avg_score > 0.2:
            label = 'bullish'
        elif avg_score < -0.2:
            label = 'bearish'
        else:
            label = 'neutral'
        
        # Average confidence
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        return SentimentResult(
            score=avg_score,
            label=label,
            confidence=avg_confidence,
            keywords=unique_keywords[:20]
        )
