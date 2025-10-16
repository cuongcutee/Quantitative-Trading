"""Backtesting utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd

from quant_trader.strategies.base import Signal, Strategy


@dataclass
class BacktestResult:
    signals: List[Signal]
    returns: float
    trades: int


@dataclass
class Backtester:
    strategy: Strategy

    def run(self, data: pd.DataFrame) -> BacktestResult:
        data = data.sort_values("open_time").copy()
        data["returns"] = data["close"].pct_change().fillna(0)
        signals: List[Signal] = []
        cumulative_return = 1.0
        position = 0

        for idx in range(len(data)):
            window = data.iloc[: idx + 1]
            signal = self.strategy.generate(window)
            if signal:
                signals.append(signal)
                position = 1 if signal.side.upper() == "BUY" else -1
            cumulative_return *= 1 + position * data.iloc[idx]["returns"]

        return BacktestResult(signals=signals, returns=cumulative_return - 1, trades=len(signals))
