"""Application settings and configuration management."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    """Container for application configuration."""

    binance_api_key: str
    binance_api_secret: str
    base_url: str = "https://api.binance.com"
    testnet_url: str = "https://testnet.binance.vision"
    use_testnet: bool = False
    database_url: str = "sqlite:///quant_trader.db"
    symbols: tuple[str, ...] = ("BTCUSDT", "ETHUSDT")
    candles_interval: str = "1h"
    cache_dir: Path = Path(".cache")

    @property
    def active_base_url(self) -> str:
        return self.testnet_url if self.use_testnet else self.base_url


def load_settings(env_file: Optional[Path | str] = None) -> Settings:
    """Load settings from environment variables and optional .env file."""

    env_path = Path(env_file) if env_file else Path(".env")
    if env_path.exists():
        load_dotenv(env_path)

    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    if not api_key or not api_secret:
        raise ValueError(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be provided via environment variables or .env file"
        )

    symbols = tuple(
        sym.strip().upper()
        for sym in os.getenv("TRADING_SYMBOLS", "BTCUSDT,ETHUSDT").split(",")
        if sym.strip()
    )

    return Settings(
        binance_api_key=api_key,
        binance_api_secret=api_secret,
        base_url=os.getenv("BINANCE_BASE_URL", "https://api.binance.com"),
        testnet_url=os.getenv("BINANCE_TESTNET_URL", "https://testnet.binance.vision"),
        use_testnet=os.getenv("BINANCE_USE_TESTNET", "false").lower() in {"1", "true", "yes"},
        database_url=os.getenv("DATABASE_URL", "sqlite:///quant_trader.db"),
        symbols=symbols,
        candles_interval=os.getenv("CANDLES_INTERVAL", "1h"),
        cache_dir=Path(os.getenv("CACHE_DIR", ".cache")),
    )
