"""Market data collection and persistence utilities."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import pandas as pd
from sqlalchemy import Column, DateTime, Float, Integer, MetaData, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from quant_trader.config import Settings
from quant_trader.data.binance_client import BinanceClient

logger = logging.getLogger(__name__)

metadata = MetaData()


def _create_candles_table(symbol: str) -> Table:
    name = f"candles_{symbol.lower()}"
    return Table(
        name,
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("open_time", DateTime, index=True, nullable=False),
        Column("open", Float, nullable=False),
        Column("high", Float, nullable=False),
        Column("low", Float, nullable=False),
        Column("close", Float, nullable=False),
        Column("volume", Float, nullable=False),
        Column("close_time", DateTime, nullable=False),
    )


@dataclass
class MarketDataService:
    """Service responsible for fetching and storing Binance candles."""

    settings: Settings
    engine: Engine

    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = create_engine(settings.database_url)
        for symbol in self.settings.symbols:
            table = _create_candles_table(symbol)
            metadata.create_all(self.engine, tables=[table])

    def fetch_latest_candles(self, client: BinanceClient, limit: int = 500) -> None:
        for symbol in self.settings.symbols:
            try:
                logger.info("Fetching %s candles for %s", limit, symbol)
                klines = client.get_klines(symbol, self.settings.candles_interval, limit=limit)
                candles = self._klines_to_dataframe(klines)
                self._persist_candles(symbol, candles)
            except Exception as exc:  # pragma: no cover - logging path
                logger.exception("Failed to fetch candles for %s: %s", symbol, exc)

    def _klines_to_dataframe(self, klines: Iterable[list]) -> pd.DataFrame:
        frame = pd.DataFrame(
            klines,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "trades",
                "taker_buy_base",
                "taker_buy_quote",
                "ignore",
            ],
        )
        frame["open_time"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True)
        frame["close_time"] = pd.to_datetime(frame["close_time"], unit="ms", utc=True)
        numeric_cols = ["open", "high", "low", "close", "volume"]
        frame[numeric_cols] = frame[numeric_cols].astype(float)
        return frame[["open_time", "open", "high", "low", "close", "volume", "close_time"]]

    def _persist_candles(self, symbol: str, candles: pd.DataFrame) -> None:
        table = _create_candles_table(symbol)
        with self.engine.begin() as connection:
            try:
                candles.to_sql(table.name, connection, if_exists="append", index=False)
            except SQLAlchemyError as exc:
                logger.error("Failed to persist candles for %s: %s", symbol, exc)
                raise

    def load_candles(self, symbol: str, limit: int = 1000) -> pd.DataFrame:
        table_name = f"candles_{symbol.lower()}"
        query = f"SELECT * FROM {table_name} ORDER BY open_time DESC LIMIT :limit"
        with self.engine.connect() as connection:
            return pd.read_sql(query, connection, params={"limit": limit})


def export_to_csv(
    service: MarketDataService,
    *,
    output_dir: Path,
    symbols: Iterable[str],
    limit: int = 1000,
) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: List[Path] = []
    for symbol in symbols:
        data = service.load_candles(symbol, limit)
        file_path = output_dir / f"{symbol.lower()}_{limit}.csv"
        data.sort_values("open_time").to_csv(file_path, index=False)
        exported.append(file_path)
    return exported
