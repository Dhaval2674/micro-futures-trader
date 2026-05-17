"""Fetch market data from various sources."""

import pandas as pd
import yfinance as yf
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class DataFetcher:
    """Fetch OHLCV market data."""
    
    # Symbol mapping for Yahoo Finance
    SYMBOL_MAPPING = {
        'MES': 'ES=F',      # E-mini S&P 500
        'MNQ': 'NQ=F',      # E-mini Nasdaq
        'MGC': 'GC=F'       # Micro Gold
    }
    
    @staticmethod
    def fetch_ohlcv(
        symbol: str,
        interval: str = '15m',
        period: str = '5d'
    ) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for a symbol.
        
        Args:
            symbol: Trading symbol (MES, MNQ, MGC)
            interval: Candle interval (1m, 5m, 15m, 1h, 1d)
            period: Historical period (1d, 5d, 1mo, 3mo, 6mo, 1y, max)
        
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        try:
            # Map to Yahoo Finance symbol
            yf_symbol = DataFetcher.SYMBOL_MAPPING.get(symbol, symbol)
            
            logger.info(f"Fetching {symbol} ({yf_symbol}) data...")
            
            # Fetch data
            data = yf.download(
                yf_symbol,
                interval=interval,
                period=period,
                progress=False,
                prepost=False
            )
            
            if data.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Standardize column names
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Ensure required columns exist
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in data.columns:
                    logger.error(f"Missing column {col} in fetched data")
                    return None
            
            logger.info(f"Successfully fetched {len(data)} candles for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def fetch_multiple(
        symbols: list,
        interval: str = '15m',
        period: str = '5d'
    ) -> dict:
        """Fetch OHLCV data for multiple symbols.
        
        Args:
            symbols: List of symbols
            interval: Candle interval
            period: Historical period
        
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        data = {}
        for symbol in symbols:
            df = DataFetcher.fetch_ohlcv(symbol, interval, period)
            if df is not None:
                data[symbol] = df
        
        return data
