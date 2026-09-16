# Trade Suggestion Control

## Separation of research and execution

The dashboard should expose a dedicated **Trade Suggestion** control beside the research results. It is a sizing/review control, not an execution control.

Recommended flow:

`Research Dashboard → Risk Assessment → Trade Suggestion → Human Review → Separate Execute action`

Quiver and other alternative-data findings stay in the research layer. They can inform the thesis and risk discussion, but they do not authorize a trade.

## Button behavior

**Trade Suggestion** should open a small sizing panel using the latest research result:

- Available funds: preferably populated from the connected broker/wallet account balance.
- Protected reserve: capital the user has explicitly marked as unavailable for trading.
- Entry price and stop price: taken from the current thesis/order plan and editable.
- AI suggested amount: calculated deterministically from the capital and risk limits.
- Custom amount: user may enter any amount they choose; the system recalculates the exposure and stop-loss loss estimate and flags breaches instead of silently changing the amount.

The panel should always show:

`Available funds → Protected reserve → Investable funds → Proposed amount → % of investable funds → Loss at stop → Remaining funds`

## Capital safety rules

The sizing engine currently uses two explicit limits:

1. `max_trade_pct_of_investable`: maximum capital allocation for one position.
2. `max_loss_pct_per_trade`: maximum planned stop-loss loss as a percentage of investable funds.

The protected reserve is excluded from investable funds.

The AI suggestion is the smaller of:

- the capital-allocation cap; and
- the quantity affordable under the stop-loss risk budget.

A manual amount is never silently reduced. It is marked `review_required` when it exceeds the allocation cap, exceeds the stop-loss risk budget, or would consume protected funds.

## What "vulnerable to my funds" means in the dashboard

Do not present a vague safety score as if it were a guarantee. Show concrete exposure instead:

- amount committed;
- percentage of available funds;
- percentage of investable funds;
- dollar loss if the stop is hit;
- percentage loss of investable funds at the stop;
- remaining cash after entry;
- whether the protected reserve remains intact;
- data-quality or missing-price warnings.

The dashboard may also display scenario losses such as 1x, 2x, and 3x the planned stop distance as stress cases, clearly labeled as scenarios rather than predictions.

## Account-balance integration

The system can only "know" current available funds when a trusted account/broker/wallet balance is connected. Until that connector exists, the UI must require the user to enter or confirm available funds and should display the balance timestamp/source.

Never infer available cash from a stale chart, a prior message, or a previous trade amount.

## Execution boundary

The suggestion tool returns `execution_requested: false` and does not create, sign, submit, or route orders. Any future execution action must be a separate, explicit user action with a final pre-trade check against the latest balance and risk limits.
