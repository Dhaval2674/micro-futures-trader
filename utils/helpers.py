"""Helper utility functions."""

from datetime import datetime
from config.settings import settings


def format_price(price: float, decimals: int = 2) -> str:
    """Format price for display.
    
    Args:
        price: Price value
        decimals: Number of decimal places
    
    Returns:
        Formatted price string
    """
    return f"${price:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage for display.
    
    Args:
        value: Percentage value (-100 to 100)
        decimals: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def calculate_position_size(
    account_balance: float,
    entry_price: float,
    stop_loss_price: float
) -> float:
    """Calculate position size based on risk management.
    
    Args:
        account_balance: Total account balance
        entry_price: Entry price
        stop_loss_price: Stop loss price
    
    Returns:
        Number of contracts to trade
    """
    risk_amount = account_balance * (settings.risk_percent / 100)
    price_risk = abs(entry_price - stop_loss_price)
    
    if price_risk == 0:
        return 0
    
    # Micro futures multipliers
    multipliers = {
        'MES': 50,   # E-mini S&P 500
        'MNQ': 20,   # E-mini Nasdaq
        'MGC': 10    # Micro Gold
    }
    
    # For simplification, using average multiplier
    avg_multiplier = sum(multipliers.values()) / len(multipliers)
    
    position_size = risk_amount / (price_risk * avg_multiplier)
    return max(1, int(position_size))


def is_market_open() -> bool:
    """Check if trading hours are within configured window.
    
    Returns:
        True if current time is within trading hours
    """
    now = datetime.now()
    current_hour = now.hour
    
    return settings.trading_start_hour <= current_hour < settings.trading_end_hour
