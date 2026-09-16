# Quiver Research Dashboard Integration

## Purpose

Quiver Quantitative is added as a **read-only alternative-data evidence layer** for research. It is not an execution source.

The dashboard/research workflow should treat Quiver evidence as one input alongside market prices, fundamentals, sentiment, liquidity, and risk analysis.

## Evidence categories

The adapter is designed around datasets such as:

- Congressional trading
- Insider transactions
- Government contracts
- Sentiment / other available alternative datasets

Quiver also publishes institutional/hedge-fund activity, lobbying, patents, ETF holdings, analyst ratings and other datasets. Add new adapters only when the exact API endpoint and account entitlement have been verified.

## Research flow

```text
Ticker
  -> Quiver alternative-data fetch
  -> normalize evidence
  -> flag missing/unsupported datasets
  -> Quant + sentiment + fundamental research
  -> Risk manager
  -> human review / separate execution workflow
```

## Important design rules

1. Do not turn congressional or insider activity into an automatic buy/sell instruction.
2. Do not infer causation from an observed trade, contract, lobbying event, or sentiment change.
3. Preserve the raw source payload and retrieval time when persisted by the application.
4. Mark unavailable datasets explicitly; never replace missing data with zero.
5. Keep the Quiver API key server-side in `QUIVER_API_KEY`.
6. Backtests using Quiver data must respect filing/publication timing to avoid look-ahead bias.

## Current implementation

- `autohedge/research/quiver.py`: API client and normalized research snapshot.
- `autohedge/tools/quiver_research.py`: read-only agent tool.
- `autohedge/workers.py`: Alternative-Data-Researcher agent and Director handoff.
- `.env.example`: Quiver configuration.

Endpoint paths are environment-overridable because dataset availability and endpoint catalogs can change by Quiver plan.

## Dashboard fields

Recommended UI fields for each ticker:

| Field | Meaning |
|---|---|
| Provider | Data source (`Quiver Quantitative`) |
| Dataset | Congress / Insider / Contracts / etc. |
| Observation time | When the event was disclosed/recorded |
| Event | Purchase, sale, contract award, etc. |
| Entity | Person, company, agency, institution |
| Magnitude | Shares, estimated value, contract value, etc. |
| Direction | Buy/sell or positive/negative where the source explicitly supplies it |
| Evidence status | Verified / partial / unavailable |
| Research interpretation | Analyst synthesis, clearly separated from raw data |
| Source | API/source reference |

## Verification

Before enabling a dataset in production, make one authenticated API request and confirm the response schema against the current Quiver API documentation. Keep endpoint overrides in environment variables rather than hardcoding plan-specific assumptions.
