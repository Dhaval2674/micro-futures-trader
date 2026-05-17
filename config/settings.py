"""Global settings and configuration management."""

import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseSettings, validator

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation."""

    # ===== BROKER CONFIGURATION =====
    broker_type: str = os.getenv('BROKER_TYPE', 'interactive_brokers')
    
    # Interactive Brokers
    ib_host: str = os.getenv('IB_HOST', '127.0.0.1')
    ib_port: int = int(os.getenv('IB_PORT', 7497))
    ib_client_id: int = int(os.getenv('IB_CLIENT_ID', 1))
    ib_account: str = os.getenv('IB_ACCOUNT', '')
    
    # Alpaca
    alpaca_api_key: str = os.getenv('ALPACA_API_KEY', '')
    alpaca_secret_key: str = os.getenv('ALPACA_SECRET_KEY', '')
    alpaca_base_url: str = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # APIs
    newsapi_key: str = os.getenv('NEWSAPI_KEY', '')
    
    # ===== TRADING PARAMETERS =====
    trading_symbols: List[str] = ['MES', 'MNQ', 'MGC']
    timeframe: int = int(os.getenv('TIMEFRAME', 15))  # minutes
    risk_percent: float = float(os.getenv('RISK_PERCENT', 1.0))
    
    # ===== STRATEGY PARAMETERS =====
    # Momentum
    momentum_rsi_period: int = int(os.getenv('MOMENTUM_RSI_PERIOD', 14))
    momentum_rsi_overbought: int = int(os.getenv('MOMENTUM_RSI_OVERBOUGHT', 70))
    momentum_rsi_oversold: int = int(os.getenv('MOMENTUM_RSI_OVERSOLD', 30))
    momentum_macd_fast: int = int(os.getenv('MOMENTUM_MACD_FAST', 12))
    momentum_macd_slow: int = int(os.getenv('MOMENTUM_MACD_SLOW', 26))
    momentum_macd_signal: int = int(os.getenv('MOMENTUM_MACD_SIGNAL', 9))
    momentum_roc_period: int = int(os.getenv('MOMENTUM_ROC_PERIOD', 12))
    
    # Mean Reversion
    mean_reversion_bb_period: int = int(os.getenv('MEAN_REVERSION_BB_PERIOD', 20))
    mean_reversion_bb_std_dev: float = float(os.getenv('MEAN_REVERSION_BB_STD_DEV', 2.0))
    mean_reversion_stoch_k_period: int = int(os.getenv('MEAN_REVERSION_STOCH_K_PERIOD', 14))
    mean_reversion_stoch_d_period: int = int(os.getenv('MEAN_REVERSION_STOCH_D_PERIOD', 3))
    
    # Support/Resistance
    sr_lookback_period: int = int(os.getenv('SR_LOOKBACK_PERIOD', 50))
    sr_min_touches: int = int(os.getenv('SR_MIN_TOUCHES', 2))
    sr_proximity_percent: float = float(os.getenv('SR_PROXIMITY_PERCENT', 0.5))
    
    # ===== RISK MANAGEMENT =====
    stop_loss_percent: float = float(os.getenv('STOP_LOSS_PERCENT', 0.5))
    take_profit_percent: float = float(os.getenv('TAKE_PROFIT_PERCENT', 1.5))
    min_risk_reward_ratio: float = float(os.getenv('MIN_RISK_REWARD_RATIO', 1.5))
    max_concurrent_positions: int = int(os.getenv('MAX_CONCURRENT_POSITIONS', 3))
    
    # Trading Hours
    trading_start_hour: int = int(os.getenv('TRADING_START_HOUR', 8))
    trading_end_hour: int = int(os.getenv('TRADING_END_HOUR', 21))
    
    # ===== SENTIMENT =====
    sentiment_news_lookback_hours: int = int(os.getenv('SENTIMENT_NEWS_LOOKBACK_HOURS', 24))
    sentiment_min_articles: int = int(os.getenv('SENTIMENT_MIN_ARTICLES', 5))
    sentiment_weight: float = float(os.getenv('SENTIMENT_WEIGHT', 30))
    
    # ===== LOGGING =====
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_output: str = os.getenv('LOG_OUTPUT', 'both')
    debug_mode: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    dry_run: bool = os.getenv('DRY_RUN', 'true').lower() == 'true'
    
    # ===== NOTIFICATIONS =====
    send_email_alerts: bool = os.getenv('SEND_EMAIL_ALERTS', 'false').lower() == 'true'
    email_from: str = os.getenv('EMAIL_FROM', '')
    email_to: str = os.getenv('EMAIL_TO', '')
    webhook_enabled: bool = os.getenv('WEBHOOK_ENABLED', 'false').lower() == 'true'
    webhook_url: str = os.getenv('WEBHOOK_URL', '')
    
    @validator('trading_symbols', pre=True)
    def parse_symbols(cls, v):
        """Parse trading symbols from environment."""
        if isinstance(v, str):
            return [s.strip().upper() for s in v.split(',')]
        return v
    
    class Config:
        env_file = '.env'
        case_sensitive = False


# Create global settings instance
settings = Settings()
