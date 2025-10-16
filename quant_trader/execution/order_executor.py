"""Order execution utilities."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from quant_trader.data.binance_client import BinanceClient
from quant_trader.strategies.base import Signal

logger = logging.getLogger(__name__)


class ExecutionBackend(Protocol):
    def execute(self, signal: Signal) -> None:
        ...


@dataclass
class PaperTradingBackend:
    """Paper trading backend that simply logs signals."""

    balance: float = 10000.0

    def execute(self, signal: Signal) -> None:  # pragma: no cover - logging heavy
        direction = 1 if signal.side.upper() == "BUY" else -1
        notional = self.balance * 0.01 * direction
        logger.info(
            "Paper trade %s %s with confidence %.2f at price %.2f (notional %.2f)",
            signal.side,
            signal.symbol,
            signal.confidence,
            signal.price,
            notional,
        )


@dataclass
class BinanceExecutionBackend:
    """Live trading backend using Binance API."""

    client: BinanceClient
    trade_size: float

    def execute(self, signal: Signal) -> None:
        side = signal.side.upper()
        order = self.client.create_order(
            symbol=signal.symbol,
            side=side,
            type_="MARKET",
            quantity=self.trade_size,
        )
        logger.info("Executed order on Binance: %s", order)
