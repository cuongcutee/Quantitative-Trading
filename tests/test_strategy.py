import pandas as pd

from quant_trader.strategies.moving_average import MovingAverageCrossStrategy


def test_moving_average_cross_strategy_generates_signals():
    data = pd.DataFrame(
        {
            "open_time": pd.date_range("2023-01-01", periods=40, freq="H"),
            "close": [float(i) for i in range(40)],
        }
    )
    strategy = MovingAverageCrossStrategy(short_window=5, long_window=10)
    signal = strategy.generate(data)
    assert signal is not None
    assert signal.side == "BUY"
