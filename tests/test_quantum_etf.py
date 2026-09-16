import pytest

from autohedge.research.quantum_etf import analyze_portfolio, weighted_overlap


def test_ireland_ucits_coverage_and_normalization():
    result = analyze_portfolio([
        {"ticker": "WQTM", "weight": 2},
        {"ticker": "QANT", "weight": 1},
        {"ticker": "WTAI", "weight": 1},
    ])
    assert result["coverage"]["ucits_weight_pct"] == pytest.approx(100.0)
    assert result["coverage"]["ireland_domiciled_weight_pct"] == pytest.approx(100.0)
    assert sum(r["portfolio_weight"] for r in result["portfolio"]) == pytest.approx(100.0)


def test_overlap_is_bounded():
    overlap = weighted_overlap(
        {"NVDA": 50, "IBM": 50},
        {"NVDA": 25, "IONQ": 75},
    )
    assert overlap == pytest.approx(0.25)


def test_bad_weights_fail():
    with pytest.raises(ValueError):
        analyze_portfolio([])
