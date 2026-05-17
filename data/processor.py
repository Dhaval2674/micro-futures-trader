"""Process and analyze market data."""

import pandas as pd
import numpy as np
from typing import Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """Process OHLCV data and calculate indicators."""
    
    @staticmethod
    def add_sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average.
        
        Args:
            data: DataFrame with close prices
            period: SMA period
        
        Returns:
            Series with SMA values
        """
        return data['close'].rolling(window=period).mean()
    
    @staticmethod
    def add_ema(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average.
        
        Args:
            data: DataFrame with close prices
            period: EMA period
        
        Returns:
            Series with EMA values
        """
        return data['close'].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def add_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index.
        
        Args:
            data: DataFrame with close prices
            period: RSI period
        
        Returns:
            Series with RSI values (0-100)
        """
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def add_macd(
        data: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: DataFrame with close prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def add_bollinger_bands(
        data: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands.
        
        Args:
            data: DataFrame with close prices
            period: SMA period
            std_dev: Number of standard deviations
        
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        sma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def add_stochastic(
        data: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator.
        
        Args:
            data: DataFrame with OHLC prices
            k_period: K% period
            d_period: D% period
        
        Returns:
            Tuple of (K%, D%)
        """
        low_min = data['low'].rolling(window=k_period).min()
        high_max = data['high'].rolling(window=k_period).max()
        
        k_percent = 100 * (data['close'] - low_min) / (high_max - low_min)
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def add_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range.
        
        Args:
            data: DataFrame with OHLC prices
            period: ATR period
        
        Returns:
            Series with ATR values
        """
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def add_roc(data: pd.DataFrame, period: int = 12) -> pd.Series:
        """Calculate Rate of Change.
        
        Args:
            data: DataFrame with close prices
            period: ROC period
        
        Returns:
            Series with ROC values (percentage)
        """
        roc = ((data['close'] - data['close'].shift(period)) / data['close'].shift(period)) * 100
        return roc
