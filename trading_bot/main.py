#!/usr/bin/env python3
"""
Binance Futures Trading Bot — Main entry point

Usage:
  python main.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python main.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000
  python main.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 75000
  python main.py interactive
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.cli import main

if __name__ == "__main__":
    main()
