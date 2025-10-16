"""Trading engine orchestrating data collection, strategy evaluation, and execution."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable, List

import pandas as pd

from quant_trader.data.binance_client import BinanceClient
from quant_trader.data.market_data_service import MarketDataService
from quant_trader.execution.order_executor import ExecutionBackend
from quant_trader.strategies.base import Signal, Strategy

logger = logging.getLogger(__name__)


@dataclass
class TradingEngine:
    """High-level trading engine."""

    market_data: MarketDataService
    strategies: List[Strategy]
    execution_backend: ExecutionBackend
    client: BinanceClient

    def run(self) -> None:
        logger.info("Starting trading engine")
        self.market_data.fetch_latest_candles(self.client)
        for symbol in self.market_data.settings.symbols:
            data = self.market_data.load_candles(symbol, limit=500)
            data["symbol"] = symbol
            for strategy in self.strategies:
                signal = strategy.generate(data)
                if signal:
                    logger.info("Strategy %s generated signal %s", strategy.name, signal)
                    signal.symbol = symbol
                    self.execution_backend.execute(signal)
                else:
                    logger.debug("Strategy %s no signal for %s", strategy.name, symbol)
        logger.info("Trading engine run completed")
