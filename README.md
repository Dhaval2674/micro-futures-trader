# Micro Futures Trading Bot 🚀

A comprehensive Python-based automated trading system for micro futures contracts (MES, MNQ, MGC) that combines multiple trading strategies, market sentiment analysis, and intelligent signal generation.

## Features

### 📊 Trading Strategies
- **Momentum Strategy**: RSI, MACD, ROC indicators for trend identification
- **Mean Reversion Strategy**: Bollinger Bands, Stochastic for overbought/oversold detection
- **Support/Resistance Strategy**: Key level identification and breakout detection

### 🧠 Sentiment Analysis
- Real-time news sentiment from NewsAPI
- TextBlob-based sentiment scoring
- Automated sentiment weighting in final signals

### 🎯 Supported Contracts
- **MES** - E-mini S&P 500 Futures
- **MNQ** - E-mini Nasdaq 100 Futures  
- **MGC** - Micro Gold Futures

### 🔧 Risk Management
- Configurable stop loss and take profit levels
- Risk/reward ratio calculation
- Position sizing based on account risk
- Maximum concurrent position limits

### 📱 Signal Generation
- Combined strategy scoring system
- Sentiment-weighted signals
- Confidence level calculation
- Actionable recommendations

## Quick Start

### Prerequisites
- Python 3.8+
- pip or poetry
- (Optional) Interactive Brokers TWS/Gateway running
- (Optional) NewsAPI key from https://newsapi.org

### Installation

```bash
# Clone repository
git clone https://github.com/Dhaval2674/micro-futures-trader.git
cd micro-futures-trader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
vim .env
```

Key configuration:
```env
# Broker
BROKER_TYPE=interactive_brokers
IB_HOST=127.0.0.1
IB_PORT=7497

# API Keys
NEWSAPI_KEY=your_key_here

# Trading Parameters
TRADING_SYMBOLS=MES,MNQ,MGC
TIMEFRAME=15

# Risk Management
STOP_LOSS_PERCENT=0.5
TAKE_PROFIT_PERCENT=1.5
RISK_PERCENT=1.0

# Mode
DRY_RUN=true  # Set to false for live trading
DEBUG_MODE=false
```

### Running the Bot

```bash
# Single analysis
python main.py

# Run in continuous mode (add to crontab or systemd)
python -c "from main import *; analyze_market()"
```

## Architecture

```
trading-bot/
├── config/              # Configuration management
├── data/                # Market data fetching & processing
├── strategies/          # Trading strategies
│   ├── momentum.py
│   ├── mean_reversion.py
│   └── support_resistance.py
├── sentiment/           # Sentiment analysis
├── signals/             # Signal generation engine
├── broker/              # Broker integrations
├── utils/               # Helper functions
└── main.py              # Main application
```

## Strategy Details

### Momentum Strategy
Identifies trending markets using:
- **RSI (14)**: Overbought (>70) / Oversold (<30)
- **MACD**: Trend changes and momentum shifts
- **ROC (12)**: Speed of price movement

**Signal Thresholds**:
- Score > 50: Strong BUY
- Score 15-50: BUY
- Score -15 to 15: HOLD
- Score -50 to -15: SELL
- Score < -50: Strong SELL

### Mean Reversion Strategy
Identifies overbought/oversold using:
- **Bollinger Bands (20, 2.0)**: Price deviation from mean
- **Stochastic (14,3)**: Momentum indicator crossovers

### Support/Resistance Strategy
Identifies key price levels:
- Local support and resistance detection
- Breakout and breakdown signals
- Level proximity analysis

## Signal Output

```
📈 MES: BUY (Confidence: 83%) | Score: 50.00
  Current: $5234.50 | Entry: $5234.50 | SL: $5228.00 | TP: $5244.00 | RR: 1.80
  Strategies: MOMENTUM: 65 | MEAN_REVERSION: 35 | SUPPORT_RESISTANCE: 50
  Sentiment: BULLISH (45)
  → BUY: STRONG_BUY signal with 83% confidence. RR Ratio: 1.80
```

## Risk Disclaimer

⚠️ **IMPORTANT**: This trading bot is for educational and research purposes only. Trading and investing involve substantial risk of loss. Past performance does not guarantee future results. Always:

1. Start with paper trading (dry run mode)
2. Test thoroughly before live trading
3. Use appropriate position sizing
4. Set stop losses on all trades
5. Never risk more than you can afford to lose
6. Consult a financial advisor before trading

## Configuration Profiles

### Conservative (Lower Risk)
```env
STOP_LOSS_PERCENT=1.0
TAKE_PROFIT_PERCENT=1.0
RISK_PERCENT=0.5
```

### Balanced (Recommended)
```env
STOP_LOSS_PERCENT=0.5
TAKE_PROFIT_PERCENT=1.5
RISK_PERCENT=1.0
```

### Aggressive (Higher Risk)
```env
STOP_LOSS_PERCENT=0.25
TAKE_PROFIT_PERCENT=2.0
RISK_PERCENT=2.0
```

## Backtesting

Performance metrics to track:
- Win Rate: % of profitable trades
- Profit Factor: Total Profit / Total Loss
- Average Risk/Reward: Average RR ratio
- Max Drawdown: Largest peak-to-trough decline

Targets:
- Win Rate: 55-65%
- Profit Factor: 1.5+
- Average RR: > 1.5

## Market Data Sources
- **OHLCV Data**: yfinance (Yahoo Finance)
- **News Sentiment**: NewsAPI.org
- **Live Trading**: Interactive Brokers (primary) / Alpaca (fallback)

## TODO / Roadmap

- [ ] Interactive Brokers integration
- [ ] Alpaca broker integration
- [ ] Email/Webhook alerts
- [ ] Trade logging and statistics
- [ ] Backtesting framework
- [ ] Parameter optimization
- [ ] Multi-timeframe analysis
- [ ] Machine learning enhancements
- [ ] Web dashboard
- [ ] Docker support

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
- Create a GitHub issue
- Check existing documentation
- Review STRATEGIES.md for detailed analysis

## Disclaimer

This software is provided "as is" without warranty. Users assume all responsibility for trades executed. The authors are not liable for financial losses. Always practice responsible risk management and never trade with funds you cannot afford to lose.

---

**Made with ❤️ for traders by traders**
