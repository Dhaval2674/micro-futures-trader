"""Momentum strategy implementation."""

import pandas as pd
from typing import Dict
from config.settings import settings
from data.processor import DataProcessor
from strategies.base_strategy import BaseStrategy
from utils.logger import get_logger

logger = get_logger(__name__)


class MomentumStrategy(BaseStrategy):
    """Trading strategy based on momentum indicators (RSI, MACD, ROC)."""
    
    def __init__(self):
        """Initialize momentum strategy."""
        super().__init__('Momentum')
    
    def analyze(self, data: pd.DataFrame) -> Dict:
        """Analyze data using momentum indicators.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            Dictionary with strategy signal and analysis
        """
        if not self._validate_data(data, min_rows=50):
            return {
                'strategy': self.name,
                'score': 0,
                'signal': 'HOLD',
                'reason': 'Insufficient data'
            }
        
        try:
            # Calculate indicators
            rsi = DataProcessor.add_rsi(data, settings.momentum_rsi_period)
            macd, signal, histogram = DataProcessor.add_macd(
                data,
                fast=settings.momentum_macd_fast,
                slow=settings.momentum_macd_slow,
                signal=settings.momentum_macd_signal
            )
            roc = DataProcessor.add_roc(data, settings.momentum_roc_period)
            
            # Get latest values
            latest_rsi = rsi.iloc[-1]
            latest_macd = macd.iloc[-1]
            latest_histogram = histogram.iloc[-1]
            prev_histogram = histogram.iloc[-2]
            latest_roc = roc.iloc[-1]
            
            # Calculate RSI score
            rsi_score = self._calculate_rsi_score(latest_rsi)
            
            # Calculate MACD score
            macd_score = self._calculate_macd_score(latest_histogram, prev_histogram)
            
            # Calculate ROC score
            roc_score = self._calculate_roc_score(latest_roc)
            
            # Combine scores (average)
            combined_score = (rsi_score + macd_score + roc_score) / 3
            
            # Determine signal
            if combined_score > 50:
                signal = 'BUY'
            elif combined_score < -50:
                signal = 'SELL'
            elif combined_score > 15:
                signal = 'BUY_WEAK'
            elif combined_score < -15:
                signal = 'SELL_WEAK'
            else:
                signal = 'HOLD'
            
            # Build reason string
            reason = f"RSI={latest_rsi:.1f} ({self._rsi_status(latest_rsi)}) | "
            reason += f"MACD={'↑' if latest_macd > 0 else '↓'} | ROC={latest_roc:.2f}%"
            
            return {
                'strategy': self.name,
                'score': round(combined_score, 2),
                'signal': signal,
                'rsi': round(latest_rsi, 2),
                'macd': round(latest_macd, 4),
                'histogram': round(latest_histogram, 4),
                'roc': round(latest_roc, 2),
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error in momentum strategy: {str(e)}")
            return {
                'strategy': self.name,
                'score': 0,
                'signal': 'ERROR',
                'reason': str(e)
            }
    
    @staticmethod
    def _calculate_rsi_score(rsi: float) -> float:
        """Calculate RSI-based score.
        
        Args:
            rsi: RSI value (0-100)
        
        Returns:
            Score (-100 to +100)
        """
        if rsi > settings.momentum_rsi_overbought:
            return 30  # Overbought, caution
        elif rsi > 60:
            return 60  # Strong bullish
        elif rsi > 50:
            return 30  # Moderately bullish
        elif rsi < settings.momentum_rsi_oversold:
            return -30  # Oversold, caution
        elif rsi < 40:
            return -60  # Strong bearish
        elif rsi < 50:
            return -30  # Moderately bearish
        else:
            return 0  # Neutral (50)
    
    @staticmethod
    def _calculate_macd_score(histogram: float, prev_histogram: float) -> float:
        """Calculate MACD-based score.
        
        Args:
            histogram: Current histogram value
            prev_histogram: Previous histogram value
        
        Returns:
            Score (-100 to +100)
        """
        if histogram > 0 and prev_histogram <= 0:
            return 70  # Bullish crossover
        elif histogram > 0:
            return 40  # Above signal line
        elif histogram < 0 and prev_histogram >= 0:
            return -70  # Bearish crossover
        elif histogram < 0:
            return -40  # Below signal line
        else:
            return 0  # Neutral
    
    @staticmethod
    def _calculate_roc_score(roc: float) -> float:
        """Calculate ROC-based score.
        
        Args:
            roc: Rate of change percentage
        
        Returns:
            Score (-100 to +100)
        """
        if roc > 1.0:
            return 50  # Strong positive momentum
        elif roc > 0:
            return 25  # Mild positive momentum
        elif roc < -1.0:
            return -50  # Strong negative momentum
        elif roc < 0:
            return -25  # Mild negative momentum
        else:
            return 0  # Neutral
    
    @staticmethod
    def _rsi_status(rsi: float) -> str:
        """Get RSI status description.
        
        Args:
            rsi: RSI value
        
        Returns:
            Status string
        """
        if rsi > 70:
            return 'Overbought'
        elif rsi > 60:
            return 'Strong Bullish'
        elif rsi > 50:
            return 'Bullish'
        elif rsi > 40:
            return 'Neutral'
        elif rsi > 30:
            return 'Bearish'
        elif rsi > 20:
            return 'Strong Bearish'
        else:
            return 'Oversold'
