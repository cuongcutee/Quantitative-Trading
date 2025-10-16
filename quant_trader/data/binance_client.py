"""Lightweight Binance REST client."""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict, Mapping, MutableMapping, Optional

import requests

from quant_trader.config import Settings


class BinanceClient:
    """Thin wrapper around Binance REST endpoints."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.settings.binance_api_key})

    @property
    def base_url(self) -> str:
        return self.settings.active_base_url

    def _sign_params(self, params: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        params["timestamp"] = int(time.time() * 1000)
        query_string = "&".join(f"{key}={params[key]}" for key in sorted(params))
        signature = hmac.new(
            self.settings.binance_api_secret.encode(),
            query_string.encode(),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        request_params: MutableMapping[str, Any] = dict(params or {})
        if signed:
            request_params = self._sign_params(request_params)

        response = self.session.request(method, url, params=request_params, timeout=10)
        response.raise_for_status()
        return response.json()

    def ping(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v3/ping")

    def get_exchange_info(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v3/exchangeInfo")

    def get_klines(
        self,
        symbol: str,
        interval: str,
        *,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> list[Dict[str, Any]]:
        params: Dict[str, Any] = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return self._request("GET", "/api/v3/klines", params=params)

    def get_account(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v3/account", signed=True)

    def create_order(
        self,
        *,
        symbol: str,
        side: str,
        type_: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": type_.upper(),
            "quantity": quantity,
        }
        if price is not None:
            params["price"] = price
        if time_in_force is not None:
            params["timeInForce"] = time_in_force

        return self._request("POST", "/api/v3/order", params=params, signed=True)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "BinanceClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
