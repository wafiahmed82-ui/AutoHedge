from autohedge.risk.trade_sizing import TradeSizingInput, calculate_trade_suggestion


def test_ai_suggestion_respects_allocation_and_risk_budget():
    result = calculate_trade_suggestion(
        TradeSizingInput(
            available_funds=10000,
            protected_reserve=4000,
            max_trade_pct_of_investable=10,
            max_loss_pct_per_trade=1,
            entry_price=100,
            stop_price=95,
        )
    )

    assert result["capital"]["investable_funds"] == 6000
    assert result["capital"]["allocation_cap"] == 600
    assert result["risk"]["max_loss_budget"] == 60
    assert result["suggestion"]["selected_amount"] <= 600
    assert result["risk"]["stop_loss_amount_at_selected_size"] <= 60
    assert result["status"] == "within_limits"


def test_manual_amount_is_not_silently_changed_and_is_flagged():
    result = calculate_trade_suggestion(
        TradeSizingInput(
            available_funds=10000,
            protected_reserve=4000,
            max_trade_pct_of_investable=10,
            max_loss_pct_per_trade=1,
            entry_price=100,
            stop_price=95,
            manual_amount=2000,
        )
    )

    assert result["mode"] == "manual"
    assert result["suggestion"]["selected_amount"] == 2000
    assert "amount_above_trade_allocation_limit" in result["warnings"]
    assert result["status"] == "review_required"
