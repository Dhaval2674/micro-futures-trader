"""Base broker interface."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List


class BaseBroker(ABC):
    """Abstract base class for broker integrations."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to broker.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from broker.
        
        Returns:
            True if disconnect successful
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """Get account information.
        
        Returns:
            Dictionary with account details
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict:
        """Get current positions.
        
        Returns:
            Dictionary of positions
        """
        pass
    
    @abstractmethod
    def place_order(
        self,
        symbol: str,
        qty: int,
        action: str,
        order_type: str = 'MARKET',
        price: Optional[float] = None
    ) -> Dict:
        """Place an order.
        
        Args:
            symbol: Trading symbol
            qty: Quantity
            action: 'BUY' or 'SELL'
            order_type: 'MARKET' or 'LIMIT'
            price: Limit price (if LIMIT)
        
        Returns:
            Order confirmation dictionary
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order.
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            True if cancelled successfully
        """
        pass
