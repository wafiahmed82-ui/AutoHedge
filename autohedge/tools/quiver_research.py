"""Read-only Quiver research tool for agent workflows."""

from __future__ import annotations

import json

from autohedge.research.quiver import QuiverClient


def quiver_research(ticker: str) -> str:
    """Fetch alternative-data evidence for a ticker.

    The output is research evidence only. It is not an order or an execution
    instruction and should be combined with price/fundamental/risk analysis.
    """
    client = QuiverClient()
    snapshot = client.research_snapshot(ticker)
    return json.dumps(snapshot, default=str)
