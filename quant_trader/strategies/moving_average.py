"""Moving average crossover strategy."""
from __future__ import annotations

import pandas as pd

from .base import Signal


class MovingAverageCrossStrategy:
    """Simple moving average crossover strategy."""

    name = "moving_average_cross"

    def __init__(self, short_window: int = 10, long_window: int = 30, min_confidence: float = 0.55) -> None:
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")
        self.short_window = short_window
        self.long_window = long_window
        self.min_confidence = min_confidence

    def generate(self, data: pd.DataFrame) -> Signal | None:
        if len(data) < self.long_window:
            return None

        closes = data.sort_values("open_time")["close"]
        short_ma = closes.rolling(window=self.short_window).mean().iloc[-1]
        long_ma = closes.rolling(window=self.long_window).mean().iloc[-1]

        previous_short = closes.rolling(window=self.short_window).mean().iloc[-2]
        previous_long = closes.rolling(window=self.long_window).mean().iloc[-2]

        price = float(closes.iloc[-1])

        if pd.isna(short_ma) or pd.isna(long_ma):
            return None

        if previous_short < previous_long and short_ma > long_ma:
            return Signal(symbol=data["symbol"].iloc[-1] if "symbol" in data else "", side="BUY", confidence=self.min_confidence, price=price)
        if previous_short > previous_long and short_ma < long_ma:
            return Signal(symbol=data["symbol"].iloc[-1] if "symbol" in data else "", side="SELL", confidence=self.min_confidence, price=price)
        return None
