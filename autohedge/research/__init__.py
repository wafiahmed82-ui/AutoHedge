"""Research adapters and structured research-dashboard payloads."""

from autohedge.research.quiver import QuiverClient
from autohedge.research.quantum_etf import analyze_portfolio, weighted_overlap

__all__ = ["QuiverClient", "analyze_portfolio", "weighted_overlap"]
