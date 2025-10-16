"""Command line interface for Quant Trader."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from quant_trader.config import load_settings
from quant_trader.data.binance_client import BinanceClient
from quant_trader.data.market_data_service import MarketDataService, export_to_csv
from quant_trader.engine.trading_engine import TradingEngine
from quant_trader.execution.order_executor import BinanceExecutionBackend, PaperTradingBackend
from quant_trader.strategies.moving_average import MovingAverageCrossStrategy
from quant_trader.utils.logging import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quantitative trading automation for Binance")
    parser.add_argument("command", choices=["collect", "export", "trade"], help="Command to run")
    parser.add_argument("--env", dest="env_file", type=Path, default=None, help="Path to .env file")
    parser.add_argument("--limit", type=int, default=500, help="Number of candles to fetch/export")
    parser.add_argument("--output", type=Path, default=Path("data"), help="Output directory for exports")
    parser.add_argument("--paper", action="store_true", help="Run in paper trading mode")
    parser.add_argument("--trade-size", type=float, default=0.001, help="Trade size for live execution")
    parser.add_argument("--log-file", type=Path, default=None, help="Optional log file path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(getattr(logging, args.log_level.upper(), logging.INFO), args.log_file)

    settings = load_settings(args.env_file)
    market_data = MarketDataService(settings)
    strategy = MovingAverageCrossStrategy()

    with BinanceClient(settings) as client:
        if args.command == "collect":
            market_data.fetch_latest_candles(client, limit=args.limit)
        elif args.command == "export":
            export_to_csv(market_data, output_dir=args.output, symbols=settings.symbols, limit=args.limit)
        elif args.command == "trade":
            backend = PaperTradingBackend() if args.paper else BinanceExecutionBackend(client, args.trade_size)
            engine = TradingEngine(
                market_data=market_data,
                strategies=[strategy],
                execution_backend=backend,
                client=client,
            )
            engine.run()


if __name__ == "__main__":
    main()
