#!/usr/bin/env python3
"""Main trading bot application."""

import time
from datetime import datetime
from colorama import Fore, Style
from config.settings import settings
from data.fetcher import DataFetcher
from signals.signal_generator import SignalGenerator
from utils.logger import get_logger
from utils.helpers import is_market_open, format_price, format_percentage

logger = get_logger(__name__)


def print_header():
    """Print application header."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"  🚀 MICRO FUTURES TRADING BOT")
    print(f"  Symbols: {', '.join(settings.trading_symbols)}")
    print(f"  Timeframe: {settings.timeframe}m")
    print(f"  Mode: {'DRY RUN' if settings.dry_run else 'LIVE TRADING'} | Debug: {settings.debug_mode}")
    print(f"{'='*70}{Style.RESET_ALL}\n")


def print_signal(signal: dict):
    """Print trading signal in formatted way.
    
    Args:
        signal: Signal dictionary from signal generator
    """
    if 'error' in signal:
        print(f"{Fore.RED}❌ Error: {signal['error']}{Style.RESET_ALL}")
        return
    
    symbol = signal['symbol']
    final_signal = signal['final_signal']
    confidence = signal['confidence']
    final_score = signal['final_score']
    
    # Color based on signal
    if 'BUY' in final_signal:
        color = Fore.GREEN
        emoji = '📈'
    elif 'SELL' in final_signal:
        color = Fore.RED
        emoji = '📉'
    else:
        color = Fore.YELLOW
        emoji = '⏸️'
    
    # Main signal line
    print(f"{color}{emoji} {symbol}: {final_signal} (Confidence: {confidence:.0f}%) | Score: {final_score:.2f}{Style.RESET_ALL}")
    
    # Price levels
    levels = signal['price_levels']
    print(f"  Current: {format_price(levels['current_price'])} | Entry: {format_price(levels['entry_price'])} | "
          f"SL: {format_price(levels['stop_loss'])} | TP: {format_price(levels['take_profit'])} | "
          f"RR: {levels['risk_reward_ratio']:.2f}x")
    
    # Individual strategies
    strategies = signal['strategies']
    strategy_line = "  Strategies: "
    for name, strat_signal in strategies.items():
        score = strat_signal.get('score', 0)
        score_color = Fore.GREEN if score > 0 else Fore.RED if score < 0 else Fore.WHITE
        strategy_line += f"{score_color}{name.upper()}: {score:.0f}{Style.RESET_ALL} | "
    print(strategy_line.rstrip(' | '))
    
    # Sentiment
    sentiment = signal['sentiment']
    sentiment_label = sentiment.get('sentiment_label', 'NEUTRAL')
    sentiment_score = sentiment.get('sentiment_scaled', 0)
    sentiment_color = Fore.GREEN if sentiment_label == 'BULLISH' else Fore.RED if sentiment_label == 'BEARISH' else Fore.WHITE
    print(f"  Sentiment: {sentiment_color}{sentiment_label} ({sentiment_score:.0f}){Style.RESET_ALL}")
    
    # Recommendation
    recommendation = signal['recommendation']
    rec_color = Fore.GREEN if 'BUY' in recommendation['action'] else Fore.RED if 'SELL' in recommendation['action'] else Fore.YELLOW
    print(f"  {rec_color}→ {recommendation['action']}: {recommendation['reason']}{Style.RESET_ALL}\n")


def analyze_market():
    """Main analysis loop."""
    print_header()
    
    # Check market hours
    if not is_market_open():
        logger.warning(f"Market is closed (trading hours: {settings.trading_start_hour}:00 - {settings.trading_end_hour}:00)")
        print(f"{Fore.YELLOW}⚠️  Market is currently closed. Waiting for trading hours...{Style.RESET_ALL}\n")
    
    logger.info("Starting market analysis...")
    
    # Initialize components
    signal_generator = SignalGenerator()
    
    # Fetch market data
    logger.info(f"Fetching market data for {', '.join(settings.trading_symbols)}...")
    market_data = DataFetcher.fetch_multiple(
        settings.trading_symbols,
        interval=f"{settings.timeframe}m",
        period='5d'
    )
    
    if not market_data:
        logger.error("Failed to fetch market data")
        print(f"{Fore.RED}❌ Failed to fetch market data{Style.RESET_ALL}")
        return
    
    # Generate signals for each symbol
    print(f"{Fore.CYAN}📊 SIGNAL ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}\n")
    
    signals = {}
    for symbol, data in market_data.items():
        logger.info(f"Analyzing {symbol}...")
        signal = signal_generator.generate_signal(symbol, data)
        signals[symbol] = signal
        print_signal(signal)
    
    # Summary
    buy_signals = sum(1 for s in signals.values() if 'BUY' in s.get('final_signal', ''))
    sell_signals = sum(1 for s in signals.values() if 'SELL' in s.get('final_signal', ''))
    hold_signals = sum(1 for s in signals.values() if 'HOLD' in s.get('final_signal', ''))
    
    print(f"{Fore.CYAN}{'='*70}")
    print(f"  📈 Summary: {Fore.GREEN}{buy_signals} BUY{Style.RESET_ALL} | "
          f"{Fore.RED}{sell_signals} SELL{Style.RESET_ALL} | "
          f"{Fore.YELLOW}{hold_signals} HOLD{Style.RESET_ALL}")
    print(f"  ⚙️  Dry Run Mode: {settings.dry_run}")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    logger.info(f"Analysis complete: {buy_signals} BUY, {sell_signals} SELL, {hold_signals} HOLD")


def main():
    """Main entry point."""
    try:
        analyze_market()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Bot interrupted by user{Style.RESET_ALL}")
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"{Fore.RED}❌ Fatal error: {str(e)}{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
