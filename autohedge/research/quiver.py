"""Quiver Quantitative research adapter.

Research-only integration: this module retrieves alternative-data signals and
normalizes them for the Investment AI research dashboard. It intentionally has
no order-execution capability.

Set QUIVER_API_KEY in the server environment. Endpoint paths can be overridden
with QUIVER_API_BASE and QUIVER_*_PATH variables because Quiver's API catalog
and plan entitlements can change.
"""

from __future__ import annotations

import os
from typing import Any

import httpx


class QuiverClient:
    """Small, read-only client for Quiver alternative-data research."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("QUIVER_API_KEY")
        self.base_url = (base_url or os.getenv("QUIVER_API_BASE", "https://api.quiverquant.com")).rstrip("/")
        self.timeout = float(os.getenv("QUIVER_TIMEOUT_SECONDS", "20"))

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if not self.api_key:
            raise RuntimeError("QUIVER_API_KEY is not configured")
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        response = httpx.get(url, headers=headers, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _path(self, env_name: str, default: str) -> str:
        return os.getenv(env_name, default)

    def research_snapshot(self, ticker: str) -> dict[str, Any]:
        """Return a normalized research snapshot for a ticker.

        Each dataset is independently optional. A missing/unsupported endpoint
        is reported rather than silently treated as zero or as a trading signal.
        """
        ticker = ticker.upper().strip()
        datasets: dict[str, Any] = {}
        errors: dict[str, str] = {}
        endpoint_map = {
            "congressional_trading": ("QUIVER_CONGRESSIONAL_PATH", "/beta/live/congresstrading"),
            "insider_trading": ("QUIVER_INSIDER_PATH", "/beta/live/insiders"),
            "government_contracts": ("QUIVER_CONTRACTS_PATH", "/beta/live/government-contracts"),
            "sentiment": ("QUIVER_SENTIMENT_PATH", "/beta/live/sentiment"),
        }
        for name, (env_name, default_path) in endpoint_map.items():
            try:
                datasets[name] = self._get(self._path(env_name, default_path), {"ticker": ticker})
            except Exception as exc:  # endpoint availability varies by plan/catalog
                errors[name] = str(exc)

        return {
            "provider": "Quiver Quantitative",
            "ticker": ticker,
            "research_only": True,
            "datasets": datasets,
            "errors": errors,
            "source_timestamp": None,
            "interpretation": {
                "use": "alternative-data evidence for research and cross-checking",
                "do_not_use_as": "standalone buy/sell decision or automatic order trigger",
            },
        }
