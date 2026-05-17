"""Support and resistance strategy implementation."""

import pandas as pd
from typing import Dict, List, Tuple
from config.settings import settings
from strategies.base_strategy import BaseStrategy
from utils.logger import get_logger

logger = get_logger(__name__)


class SupportResistanceStrategy(BaseStrategy):
    """Trading strategy based on support/resistance levels."""
    
    def __init__(self):
        """Initialize support/resistance strategy."""
        super().__init__('Support/Resistance')
    
    def analyze(self, data: pd.DataFrame) -> Dict:
        """Analyze data using support/resistance levels.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            Dictionary with strategy signal and analysis
        """
        if not self._validate_data(data, min_rows=settings.sr_lookback_period):
            return {
                'strategy': self.name,
                'score': 0,
                'signal': 'HOLD',
                'reason': 'Insufficient data'
            }
        
        try:
            # Identify levels
            support_levels = self._identify_support(data)
            resistance_levels = self._identify_resistance(data)
            
            # Current price
            current_price = data['close'].iloc[-1]
            prev_close = data['close'].iloc[-2] if len(data) > 1 else current_price
            
            # Detect breakouts/breakdowns
            breakout = self._detect_breakout(current_price, prev_close, resistance_levels)
            breakdown = self._detect_breakdown(current_price, prev_close, support_levels)
            
            # Calculate position within range
            if support_levels and resistance_levels:
                lowest_support = support_levels[0]
                highest_resistance = resistance_levels[0]
                price_range = highest_resistance - lowest_support
                price_position = (current_price - lowest_support) / price_range if price_range > 0 else 0.5
            else:
                price_position = 0.5
            
            # Calculate score
            score = 0
            
            if breakout:
                score += 70  # Strong bullish
            elif breakdown:
                score -= 70  # Strong bearish
            else:
                # Position-based scoring
                if price_position > 0.7:
                    score -= 50  # Near resistance
                elif price_position < 0.3:
                    score += 50  # Near support
                else:
                    score = 0  # Mid range
            
            # Determine signal
            if score > 50:
                signal = 'BUY'
            elif score < -50:
                signal = 'SELL'
            elif score > 15:
                signal = 'BUY_WEAK'
            elif score < -15:
                signal = 'SELL_WEAK'
            else:
                signal = 'HOLD'
            
            # Build reason
            reason = f"Price: {current_price:.2f} | "
            if support_levels:
                reason += f"Support: {support_levels[0]:.2f} | "
            if resistance_levels:
                reason += f"Resistance: {resistance_levels[0]:.2f}"
            
            if breakout:
                reason = f"Resistance breakout at {resistance_levels[0]:.2f}!"
            elif breakdown:
                reason = f"Support breakdown at {support_levels[0]:.2f}!"
            
            return {
                'strategy': self.name,
                'score': round(score, 2),
                'signal': signal,
                'current_price': round(current_price, 2),
                'support_levels': [round(s, 2) for s in support_levels[:3]],
                'resistance_levels': [round(r, 2) for r in resistance_levels[:3]],
                'breakout': breakout,
                'breakdown': breakdown,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error in support/resistance strategy: {str(e)}")
            return {
                'strategy': self.name,
                'score': 0,
                'signal': 'ERROR',
                'reason': str(e)
            }
    
    def _identify_support(self, data: pd.DataFrame) -> List[float]:
        """Identify support levels.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            List of support levels (descending)
        """
        lookback = min(settings.sr_lookback_period, len(data))
        recent_data = data.iloc[-lookback:]
        
        support_levels = []
        
        for i in range(1, len(recent_data) - 1):
            if (recent_data['low'].iloc[i] < recent_data['low'].iloc[i-1] and
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i+1]):
                support_levels.append(recent_data['low'].iloc[i])
        
        # Remove duplicates (within proximity)
        filtered = []
        for level in sorted(support_levels, reverse=True):
            is_duplicate = False
            for existing in filtered:
                if abs(level - existing) / existing < (settings.sr_proximity_percent / 100):
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered.append(level)
        
        return sorted(filtered, reverse=True)
    
    def _identify_resistance(self, data: pd.DataFrame) -> List[float]:
        """Identify resistance levels.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            List of resistance levels (descending)
        """
        lookback = min(settings.sr_lookback_period, len(data))
        recent_data = data.iloc[-lookback:]
        
        resistance_levels = []
        
        for i in range(1, len(recent_data) - 1):
            if (recent_data['high'].iloc[i] > recent_data['high'].iloc[i-1] and
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i+1]):
                resistance_levels.append(recent_data['high'].iloc[i])
        
        # Remove duplicates (within proximity)
        filtered = []
        for level in sorted(resistance_levels, reverse=True):
            is_duplicate = False
            for existing in filtered:
                if abs(level - existing) / existing < (settings.sr_proximity_percent / 100):
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered.append(level)
        
        return sorted(filtered, reverse=True)
    
    @staticmethod
    def _detect_breakout(
        current_price: float,
        prev_close: float,
        resistance_levels: List[float]
    ) -> bool:
        """Detect resistance breakout.
        
        Args:
            current_price: Current price
            prev_close: Previous close
            resistance_levels: List of resistance levels
        
        Returns:
            True if breakout detected
        """
        if not resistance_levels:
            return False
        
        highest_resistance = resistance_levels[0]
        return prev_close <= highest_resistance and current_price > highest_resistance
    
    @staticmethod
    def _detect_breakdown(
        current_price: float,
        prev_close: float,
        support_levels: List[float]
    ) -> bool:
        """Detect support breakdown.
        
        Args:
            current_price: Current price
            prev_close: Previous close
            support_levels: List of support levels
        
        Returns:
            True if breakdown detected
        """
        if not support_levels:
            return False
        
        lowest_support = support_levels[0]
        return prev_close >= lowest_support and current_price < lowest_support
