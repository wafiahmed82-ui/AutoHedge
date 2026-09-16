"""Structured quantum / AI ETF portfolio analysis for research use only.

The analyzer keeps product facts separate from investor decisions. It covers
both US-listed examples and Ireland-domiciled UCITS examples, records source
metadata, and measures portfolio overlap when holdings are supplied.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class QuantumETF:
    ticker: str
    name: str
    theme: str
    domicile: str
    ucits: bool
    accumulating: bool | None
    ter: float | None
    isin: str | None
    listing_hint: str | None = None


ETF_CATALOG: Dict[str, QuantumETF] = {
    "WQTM": QuantumETF(
        "WQTM", "WisdomTree Quantum Computing UCITS ETF", "quantum",
        "Ireland", True, True, 0.50, "IE000W8WMSL2", "LSE/Xetra/Borsa/SIX"
    ),
    "QANT": QuantumETF(
        "QANT", "iShares Quantum Computing UCITS ETF", "quantum",
        "Ireland", True, True, 0.50, "IE000C6ITGC8", "LSE/Euronext/Xetra/SIX"
    ),
    "QNTM": QuantumETF(
        "QNTM", "VanEck Quantum Computing UCITS ETF", "quantum",
        "Ireland", True, True, 0.55, "IE0007Y8Y157", "LSE/Euronext/Xetra"
    ),
    "WTAI": QuantumETF(
        "WTAI", "WisdomTree Artificial Intelligence UCITS ETF", "ai",
        "Ireland", True, True, 0.40, "IE00BDVPNG13", "LSE/Xetra/Borsa/SIX"
    ),
    # US-listed products are retained for research comparison; do not assume
    # they are UCITS or Ireland-domiciled merely because a similar theme exists.
    "ARTY": QuantumETF(
        "ARTY", "iShares Future AI & Tech ETF", "ai", "United States",
        False, False, 0.47, "46435U556", "NYSE Arca"
    ),
    "QTUM": QuantumETF(
        "QTUM", "Defiance Quantum ETF", "quantum+ai", "United States",
        False, False, 0.40, None, "US listing"
    ),
    "DRAM": QuantumETF(
        "DRAM", "Memory ETF / Memory UCITS variant", "ai-infrastructure",
        "mixed", False, None, None, None,
        "Requires listing/ISIN selection before order routing"
    ),
}


def normalize_weights(holdings: Dict[str, float]) -> Dict[str, float]:
    total = sum(float(v) for v in holdings.values())
    if total <= 0:
        return {}
    return {k.upper(): float(v) / total for k, v in holdings.items()}


def weighted_overlap(left: Dict[str, float], right: Dict[str, float]) -> float:
    """Minimum-overlap measure based on shared normalized holding weights."""
    a = normalize_weights(left)
    b = normalize_weights(right)
    return round(sum(min(a.get(k, 0.0), b.get(k, 0.0)) for k in set(a) | set(b)), 6)


def analyze_portfolio(
    positions: Iterable[dict],
    holdings_by_ticker: Dict[str, Dict[str, float]] | None = None,
) -> dict:
    """Return research metrics for a candidate quantum/AI ETF portfolio.

    positions: iterable of {"ticker": str, "weight": float}.
    holdings_by_ticker: optional ETF -> holding -> weight mapping.
    """
    rows: List[dict] = []
    total = sum(float(p.get("weight", 0.0)) for p in positions)
    if total <= 0:
        raise ValueError("portfolio weights must sum to > 0")

    # Materialize because callers may provide a generator.
    materialized = list(positions)
    total = sum(float(p.get("weight", 0.0)) for p in materialized)

    for p in materialized:
        ticker = str(p["ticker"]).upper()
        weight = float(p["weight"]) / total
        product = ETF_CATALOG.get(ticker)
        rows.append({
            "ticker": ticker,
            "portfolio_weight": round(weight * 100.0, 4),
            "product": asdict(product) if product else None,
        })

    ucits_weight = sum(r["portfolio_weight"] for r in rows if r["product"] and r["product"]["ucits"])
    ireland_weight = sum(r["portfolio_weight"] for r in rows if r["product"] and r["product"]["domicile"] == "Ireland")

    overlap = {}
    if holdings_by_ticker:
        tickers = [r["ticker"] for r in rows]
        for i, left in enumerate(tickers):
            for right in tickers[i + 1 :]:
                if left in holdings_by_ticker and right in holdings_by_ticker:
                    overlap[f"{left}:{right}"] = weighted_overlap(
                        holdings_by_ticker[left], holdings_by_ticker[right]
                    )

    return {
        "research_only": True,
        "portfolio": rows,
        "coverage": {
            "ucits_weight_pct": round(ucits_weight, 4),
            "ireland_domiciled_weight_pct": round(ireland_weight, 4),
        },
        "overlap": overlap,
        "tax_note": (
            "Ireland domicile/UCITS status is a product-structure fact, not a "
            "guarantee of lower personal tax for an investor in Bangladesh/UAE. "
            "Personal tax, withholding, estate tax, broker treatment and treaty "
            "effects must be checked separately before investing."
        ),
        "warnings": [
            "Newer thematic ETFs may have short live histories.",
            "Theme labels do not establish risk, expected return, or suitability.",
            "US-listed and Ireland-domiciled variants must be distinguished by ISIN/listing before order routing.",
        ],
        "status": "research_ready",
    }
