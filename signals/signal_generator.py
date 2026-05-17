"""Generate trading signals by combining strategies and sentiment."""

from typing import Dict, List, Optional
import pandas as pd
from config.settings import settings
from data.processor import DataProcessor
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.support_resistance import SupportResistanceStrategy
from sentiment.analyzer import SentimentAnalyzer
from utils.logger import get_logger

logger = get_logger(__name__)


class SignalGenerator:
    """Generate comprehensive trading signals."""
    
    def __init__(self):
        """Initialize signal generator with strategies."""
        self.momentum_strategy = MomentumStrategy()
        self.mean_reversion_strategy = MeanReversionStrategy()
        self.sr_strategy = SupportResistanceStrategy()
    
    def generate_signal(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Generate trading signal for a symbol.
        
        Args:
            symbol: Trading symbol
            data: DataFrame with OHLCV data
        
        Returns:
            Dictionary with complete signal analysis
        """
        try:
            # Get strategy signals
            momentum_signal = self.momentum_strategy.analyze(data)
            mean_reversion_signal = self.mean_reversion_strategy.analyze(data)
            sr_signal = self.sr_strategy.analyze(data)
            
            # Get sentiment
            sentiment = SentimentAnalyzer.analyze_news(symbol)
            
            # Calculate combined strategy score
            strategy_scores = [
                momentum_signal.get('score', 0),
                mean_reversion_signal.get('score', 0),
                sr_signal.get('score', 0)
            ]
            strategy_score = sum(strategy_scores) / len(strategy_scores)
            
            # Calculate final score with sentiment
            sentiment_score = sentiment.get('sentiment_scaled', 0)
            final_score = (strategy_score * 0.7) + (sentiment_score * 0.3)
            
            # Determine final signal
            final_signal = self._determine_signal(final_score)
            confidence = self._calculate_confidence(final_score, momentum_signal, mean_reversion_signal, sr_signal)
            
            # Calculate price levels
            current_price = data['close'].iloc[-1]
            entry_price = current_price
            
            # Stop loss and take profit
            if final_score > 0:
                stop_loss = entry_price * (1 - settings.stop_loss_percent / 100)
                take_profit = entry_price * (1 + settings.take_profit_percent / 100)
            else:
                stop_loss = entry_price * (1 + settings.stop_loss_percent / 100)
                take_profit = entry_price * (1 - settings.take_profit_percent / 100)
            
            # Risk/reward ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0
            
            # Build complete signal
            signal = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'symbol': symbol,
                'final_signal': final_signal,
                'confidence': round(confidence, 2),
                'final_score': round(final_score, 2),
                
                'strategies': {
                    'momentum': momentum_signal,
                    'mean_reversion': mean_reversion_signal,
                    'support_resistance': sr_signal
                },
                
                'sentiment': sentiment,
                
                'price_levels': {
                    'current_price': round(current_price, 2),
                    'entry_price': round(entry_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'take_profit': round(take_profit, 2),
                    'risk_reward_ratio': round(rr_ratio, 2)
                },
                
                'recommendation': self._create_recommendation(
                    final_signal,
                    confidence,
                    entry_price,
                    stop_loss,
                    take_profit,
                    rr_ratio
                )
            }
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'final_signal': 'ERROR',
                'error': str(e)
            }
    
    @staticmethod
    def _determine_signal(score: float) -> str:
        """Determine signal from combined score.
        
        Args:
            score: Combined score (-100 to +100)
        
        Returns:
            Signal string
        """
        if score > 50:
            return 'STRONG_BUY'
        elif score > 15:
            return 'BUY'
        elif score > -15:
            return 'HOLD'
        elif score > -50:
            return 'SELL'
        else:
            return 'STRONG_SELL'
    
    @staticmethod
    def _calculate_confidence(final_score: float, *strategy_signals) -> float:
        """Calculate confidence level (0-100).
        
        Args:
            final_score: Final combined score
            *strategy_signals: Individual strategy signals
        
        Returns:
            Confidence percentage
        """
        # Base confidence from score magnitude
        base_confidence = min(abs(final_score) / 50 * 100, 100)
        
        # Agreement bonus: check if strategies agree
        signal_scores = [s.get('score', 0) for s in strategy_signals if isinstance(s, dict)]
        if signal_scores:
            # Check if all signals point in same direction
            positive_signals = sum(1 for s in signal_scores if s > 0)
            negative_signals = sum(1 for s in signal_scores if s < 0)
            
            if positive_signals == len(signal_scores) or negative_signals == len(signal_scores):
                base_confidence = min(base_confidence + 15, 100)
        
        return base_confidence
    
    @staticmethod
    def _create_recommendation(
        signal: str,
        confidence: float,
        entry: float,
        sl: float,
        tp: float,
        rr: float
    ) -> Dict:
        """Create actionable recommendation.
        
        Args:
            signal: Trading signal
            confidence: Confidence level
            entry: Entry price
            sl: Stop loss price
            tp: Take profit price
            rr: Risk/reward ratio
        
        Returns:
            Recommendation dictionary
        """
        action = 'PASS'  # Default action
        
        if confidence >= settings.min_risk_reward_ratio * 20:  # ~30% confidence as minimum
            if rr >= settings.min_risk_reward_ratio:
                if 'BUY' in signal:
                    action = 'BUY'
                elif 'SELL' in signal:
                    action = 'SELL'
        
        return {
            'action': action,
            'reason': f"{signal} signal with {confidence:.0f}% confidence. RR Ratio: {rr:.2f}",
            'position_type': 'LONG' if 'BUY' in signal else 'SHORT' if 'SELL' in signal else 'NEUTRAL'
        }
