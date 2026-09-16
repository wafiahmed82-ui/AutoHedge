# Quantum + AI ETF Portfolio Analyser

Research-only module for comparing quantum computing, AI, and AI-infrastructure ETFs from a UAE/Bangladesh investor workflow.

## Seed universe

The initial catalogue includes the instruments requested for research:

- WQTM — WisdomTree Quantum Computing UCITS ETF (Ireland, UCITS, accumulating)
- QANT — iShares Quantum Computing UCITS ETF (Ireland, UCITS, accumulating)
- QNTM — VanEck Quantum Computing UCITS ETF (Ireland, UCITS, accumulating)
- WTAI — WisdomTree Artificial Intelligence UCITS ETF (Ireland, UCITS, accumulating)
- QTUM — Defiance Quantum ETF (US-listed, non-UCITS)
- ARTY — iShares Future AI & Tech ETF (US-listed, non-UCITS)
- DRAM — memory/AI-infrastructure exposure; the analyser requires exact listing/ISIN selection before routing because both US and European UCITS products use DRAM-related naming.

## What the analyser checks

1. Domicile and UCITS status.
2. Accumulating/distributing structure when known.
3. Total expense ratio when verified.
4. ISIN and listing identity so the system does not confuse a US ETF with an Ireland-domiciled UCITS variant.
5. Portfolio weights and overlap, when holdings are provided by a trusted source.
6. Portfolio-level share of Ireland-domiciled and UCITS exposure.
7. Research warnings for new funds, short histories, thematic concentration, currency exposure, and missing product facts.

## Tax handling

The dashboard must not label an Ireland-domiciled ETF as automatically "lower tax" for the user. Irish domicile and UCITS structure are product facts. Personal tax depends on the investor's residence, broker, withholding rules, estate rules, treaties, fund structure and the specific security/listing. The analyser therefore exposes the domicile/UCITS facts and sends tax questions to a separate tax-review step.

## Trading integration

This analyser feeds the Research Dashboard and Trade Suggestion layer only. It does not create or submit orders. A future execution flow must resolve the exact ISIN/listing, current price, liquidity, account eligibility, currency and pre-trade risk limits before an order can be considered.
