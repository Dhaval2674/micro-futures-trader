"""Base strategy class."""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str):
        """Initialize strategy.
        
        Args:
            name: Strategy name
        """
        self.name = name
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict:
        """Analyze data and generate signal.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            Dictionary with signal analysis results
        """
        pass
    
    def _validate_data(self, data: pd.DataFrame, min_rows: int = 30) -> bool:
        """Validate that data has sufficient rows.
        
        Args:
            data: DataFrame to validate
            min_rows: Minimum required rows
        
        Returns:
            True if data is valid
        """
        return len(data) >= min_rows
