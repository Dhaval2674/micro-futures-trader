"""Market sentiment analysis from news and data."""

from typing import Dict, Optional
from textblob import TextBlob
import requests
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """Analyze market sentiment from news articles."""
    
    SYMBOL_KEYWORDS = {
        'MES': ['S&P 500', 'SPY', 'ES', 'stock market', 'equities', 'stocks', 'bull', 'bear'],
        'MNQ': ['Nasdaq', 'tech stocks', 'NQ', 'technology', 'QQQ', 'FAANG', 'tech'],
        'MGC': ['gold', 'precious metals', 'inflation', 'safe haven', 'GC', 'XAU']
    }
    
    @staticmethod
    def analyze_news(symbol: str) -> Dict:
        """Analyze sentiment from news articles.
        
        Args:
            symbol: Trading symbol (MES, MNQ, MGC)
        
        Returns:
            Dictionary with sentiment analysis results
        """
        if not settings.newsapi_key:
            logger.warning("NewsAPI key not configured")
            return SentimentAnalyzer._create_neutral_response(symbol)
        
        try:
            # Get keywords for symbol
            keywords = SentimentAnalyzer.SYMBOL_KEYWORDS.get(symbol, [symbol])
            query = ' OR '.join(keywords[:3])  # Use first 3 keywords
            
            # Fetch news
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 50,
                'apiKey': settings.newsapi_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])
            
            if not articles:
                return SentimentAnalyzer._create_neutral_response(symbol)
            
            # Analyze sentiment
            sentiments = []
            for article in articles:
                text = article.get('title', '') + ' ' + article.get('description', '')
                sentiment_score = SentimentAnalyzer._calculate_sentiment(text)
                sentiments.append(sentiment_score)
            
            # Calculate aggregate sentiment
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            # Determine sentiment label
            if avg_sentiment > 0.1:
                sentiment_label = 'BULLISH'
            elif avg_sentiment < -0.1:
                sentiment_label = 'BEARISH'
            else:
                sentiment_label = 'NEUTRAL'
            
            # Count positive/negative
            positive = sum(1 for s in sentiments if s > 0.1)
            negative = sum(1 for s in sentiments if s < -0.1)
            neutral = len(sentiments) - positive - negative
            
            return {
                'symbol': symbol,
                'sentiment_score': round(avg_sentiment, 2),
                'sentiment_label': sentiment_label,
                'sentiment_scaled': round(avg_sentiment * 100, 1),  # Scale to -100 to +100
                'articles_analyzed': len(articles),
                'positive_articles': positive,
                'negative_articles': negative,
                'neutral_articles': neutral
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment for {symbol}: {str(e)}")
            return SentimentAnalyzer._create_neutral_response(symbol)
    
    @staticmethod
    def _calculate_sentiment(text: str) -> float:
        """Calculate sentiment score for text using TextBlob.
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment score (-1 to +1)
        """
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.warning(f"Error calculating sentiment: {str(e)}")
            return 0
    
    @staticmethod
    def _create_neutral_response(symbol: str) -> Dict:
        """Create neutral sentiment response.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Neutral sentiment dictionary
        """
        return {
            'symbol': symbol,
            'sentiment_score': 0,
            'sentiment_label': 'NEUTRAL',
            'sentiment_scaled': 0,
            'articles_analyzed': 0,
            'positive_articles': 0,
            'negative_articles': 0,
            'neutral_articles': 0
        }
