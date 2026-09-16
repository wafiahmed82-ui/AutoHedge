"""Deterministic capital-aware trade sizing for the research dashboard.

This module never places orders. It turns available capital, protected reserves,
and an entry/stop plan into a proposed amount and exposes the downside before
an execution step. A user-entered amount is treated as an explicit override and
is checked against the same risk limits, rather than being silently changed.
"""

from dataclasses import dataclass, asdict
from math import floor
from typing import Literal, Optional


Direction = Literal["long", "short"]


@dataclass(frozen=True)
class TradeSizingInput:
    available_funds: float
    protected_reserve: float = 0.0
    max_trade_pct_of_investable: float = 10.0
    max_loss_pct_per_trade: float = 1.0
    entry_price: float = 0.0
    stop_price: float = 0.0
    direction: Direction = "long"
    manual_amount: Optional[float] = None


def _money(value: float) -> float:
    return round(max(0.0, value), 2)


def calculate_trade_suggestion(data: TradeSizingInput) -> dict:
    """Return a capital/risk-aware suggestion without executing a trade."""
    values = asdict(data)
    if data.available_funds < 0:
        raise ValueError("available_funds must be >= 0")
    if data.protected_reserve < 0:
        raise ValueError("protected_reserve must be >= 0")
    if data.protected_reserve > data.available_funds:
        raise ValueError("protected_reserve cannot exceed available_funds")
    if not 0 < data.max_trade_pct_of_investable <= 100:
        raise ValueError("max_trade_pct_of_investable must be > 0 and <= 100")
    if not 0 < data.max_loss_pct_per_trade <= 100:
        raise ValueError("max_loss_pct_per_trade must be > 0 and <= 100")
    if data.entry_price <= 0 or data.stop_price <= 0:
        raise ValueError("entry_price and stop_price must be > 0")
    if data.direction == "long" and data.stop_price >= data.entry_price:
        raise ValueError("long trades require stop_price < entry_price")
    if data.direction == "short" and data.stop_price <= data.entry_price:
        raise ValueError("short trades require stop_price > entry_price")
    if data.manual_amount is not None and data.manual_amount < 0:
        raise ValueError("manual_amount must be >= 0")

    investable = _money(data.available_funds - data.protected_reserve)
    allocation_cap = _money(investable * data.max_trade_pct_of_investable / 100.0)
    risk_budget = _money(investable * data.max_loss_pct_per_trade / 100.0)
    per_unit_stop_loss = abs(data.entry_price - data.stop_price)

    risk_qty = floor(risk_budget / per_unit_stop_loss) if per_unit_stop_loss else 0
    risk_based_amount = _money(risk_qty * data.entry_price)
    suggested_amount = _money(min(allocation_cap, risk_based_amount))

    if data.manual_amount is None:
        selected_amount = suggested_amount
        mode = "ai_suggested"
    else:
        selected_amount = _money(data.manual_amount)
        mode = "manual"

    selected_qty = floor(selected_amount / data.entry_price)
    selected_amount = _money(selected_qty * data.entry_price)
    potential_stop_loss = _money(selected_qty * per_unit_stop_loss)
    selected_pct_of_investable = (
        (selected_amount / investable * 100.0) if investable else 0.0
    )
    selected_pct_of_available = (
        (selected_amount / data.available_funds * 100.0)
        if data.available_funds
        else 0.0
    )
    stop_loss_pct_of_investable = (
        (potential_stop_loss / investable * 100.0) if investable else 0.0
    )
    breaches = []
    if selected_amount > allocation_cap:
        breaches.append("amount_above_trade_allocation_limit")
    if potential_stop_loss > risk_budget:
        breaches.append("stop_loss_above_risk_budget")
    if selected_amount > investable:
        breaches.append("amount_above_investable_funds")

    remaining_after_entry = _money(data.available_funds - selected_amount)
    reserve_intact = remaining_after_entry >= data.protected_reserve

    return {
        "research_only": True,
        "execution_requested": False,
        "mode": mode,
        "inputs": values,
        "capital": {
            "available_funds": _money(data.available_funds),
            "protected_reserve": _money(data.protected_reserve),
            "investable_funds": investable,
            "allocation_cap": allocation_cap,
            "remaining_after_entry": remaining_after_entry,
            "reserve_intact": reserve_intact,
        },
        "risk": {
            "max_loss_budget": risk_budget,
            "stop_loss_distance_per_unit": round(per_unit_stop_loss, 8),
            "stop_loss_amount_at_selected_size": potential_stop_loss,
            "selected_loss_pct_of_investable": round(stop_loss_pct_of_investable, 4),
        },
        "suggestion": {
            "suggested_amount": suggested_amount,
            "selected_amount": selected_amount,
            "selected_quantity": selected_qty,
            "selected_pct_of_investable": round(selected_pct_of_investable, 4),
            "selected_pct_of_available": round(selected_pct_of_available, 4),
            "risk_based_amount": risk_based_amount,
            "risk_based_quantity": risk_qty,
        },
        "warnings": breaches,
        "status": "within_limits" if not breaches else "review_required",
    }
