"""Dashboard tool for a user-controlled trade suggestion button."""

import json

from autohedge.risk.trade_sizing import TradeSizingInput, calculate_trade_suggestion


def trade_suggestion(
    available_funds: float,
    protected_reserve: float,
    entry_price: float,
    stop_price: float,
    direction: str = "long",
    max_trade_pct_of_investable: float = 10.0,
    max_loss_pct_per_trade: float = 1.0,
    manual_amount: float | None = None,
) -> str:
    """Calculate an AI-sized amount or evaluate a user-entered amount.

    The result is informational only. This function never creates, submits, or
    signs an order. The UI can bind it to a 'Trade Suggestion' button and keep
    the actual execution control separate.
    """
    payload = TradeSizingInput(
        available_funds=float(available_funds),
        protected_reserve=float(protected_reserve),
        max_trade_pct_of_investable=float(max_trade_pct_of_investable),
        max_loss_pct_per_trade=float(max_loss_pct_per_trade),
        entry_price=float(entry_price),
        stop_price=float(stop_price),
        direction=direction.lower(),
        manual_amount=None if manual_amount in (None, "") else float(manual_amount),
    )
    return json.dumps(calculate_trade_suggestion(payload), indent=2)
