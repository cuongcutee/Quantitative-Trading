"""Strategy interfaces."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class Signal:
    """Represents a trading signal."""

    def __init__(self, symbol: str, side: str, confidence: float, price: float) -> None:
        self.symbol = symbol
        self.side = side
        self.confidence = confidence
        self.price = price

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Signal(symbol={self.symbol!r}, side={self.side!r}, confidence={self.confidence!r}, price={self.price!r})"


class Strategy(Protocol):
    """Protocol for strategies."""

    name: str

    def generate(self, data: pd.DataFrame) -> Signal | None:
        ...


@dataclass
class StrategyContext:
    symbol: str
    data: pd.DataFrame
