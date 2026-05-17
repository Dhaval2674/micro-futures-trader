"""Mean reversion strategy implementation."""

import pandas as pd
from typing import Dict
from config.settings import settings
from data.processor import DataProcessor
from strategies.base_strategy import BaseStrategy
from utils.logger import get_logger

logger = get_logger(__name__)


class MeanReversionStrategy(BaseStrategy):
    """Trading strategy based on mean reversion (Bollinger Bands, Stochastic)."""
    
    def __init__(self):
        """Initialize mean reversion strategy."""
        super().__init__('Mean Reversion')
    
    def analyze(self, data: pd.DataFrame) -> Dict:
        """Analyze data using mean reversion indicators.
        
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
            upper_bb, middle_bb, lower_bb = DataProcessor.add_bollinger_bands(
                data,
                period=settings.mean_reversion_bb_period,
                std_dev=settings.mean_reversion_bb_std_dev
            )
            
            k_percent, d_percent = DataProcessor.add_stochastic(
                data,
                k_period=settings.mean_reversion_stoch_k_period,
                d_period=settings.mean_reversion_stoch_d_period
            )
            
            # Get latest values
            latest_price = data['close'].iloc[-1]
            latest_upper_bb = upper_bb.iloc[-1]
            latest_middle_bb = middle_bb.iloc[-1]
            latest_lower_bb = lower_bb.iloc[-1]
            latest_k = k_percent.iloc[-1]
            prev_k = k_percent.iloc[-2]
            latest_d = d_percent.iloc[-1]
            
            # Calculate BB position (0 = lower band, 1 = upper band)
            bb_range = latest_upper_bb - latest_lower_bb
            bb_position = (latest_price - latest_lower_bb) / bb_range if bb_range > 0 else 0.5
            
            # Calculate BB score
            bb_score = self._calculate_bb_score(bb_position, latest_price, latest_lower_bb, latest_upper_bb, latest_middle_bb)
            
            # Calculate Stochastic score
            stoch_score = self._calculate_stoch_score(latest_k, prev_k, latest_d)
            
            # Combined score
            combined_score = (bb_score * 0.5) + (stoch_score * 0.5)
            
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
            bb_status = 'Upper' if bb_position > 0.7 else 'Lower' if bb_position < 0.3 else 'Mid'
            reason = f"Price in {bb_status} BB zone | Stoch K={latest_k:.1f} (D={latest_d:.1f})"
            
            return {
                'strategy': self.name,
                'score': round(combined_score, 2),
                'signal': signal,
                'bb_position': round(bb_position, 2),
                'stoch_k': round(latest_k, 2),
                'stoch_d': round(latest_d, 2),
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error in mean reversion strategy: {str(e)}")
            return {
                'strategy': self.name,
                'score': 0,
                'signal': 'ERROR',
                'reason': str(e)
            }
    
    @staticmethod
    def _calculate_bb_score(bb_position: float, price: float, lower: float, upper: float, middle: float) -> float:
        """Calculate Bollinger Bands score.
        
        Args:
            bb_position: Position between bands (0-1)
            price: Current price
            lower: Lower band
            upper: Upper band
            middle: Middle band (SMA)
        
        Returns:
            Score (-100 to +100)
        """
        if bb_position > 0.95:
            return -60  # Price at upper band - overbought
        elif bb_position > 0.7:
            return -30  # Price in upper zone
        elif bb_position < 0.05:
            return 60  # Price at lower band - oversold
        elif bb_position < 0.3:
            return 30  # Price in lower zone
        else:
            return 0  # Mid zone - neutral
    
    @staticmethod
    def _calculate_stoch_score(k: float, prev_k: float, d: float) -> float:
        """Calculate Stochastic Oscillator score.
        
        Args:
            k: Current K% value
            prev_k: Previous K% value
            d: D% value
        
        Returns:
            Score (-100 to +100)
        """
        # Crossover signals
        if k > d and prev_k <= d:
            return 40  # Bullish crossover
        elif k < d and prev_k >= d:
            return -40  # Bearish crossover
        
        # Overbought/Oversold
        if k > 80:
            return -70  # Overbought
        elif k > 50:
            return -30  # High
        elif k < 20:
            return 70  # Oversold
        elif k < 50:
            return 30  # Low
        else:
            return 0  # Neutral
