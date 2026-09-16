"""
AutoHedge workers: thesis generation, alternative-data research, risk, execution,
and quantitative analysis.
"""

from datetime import datetime

from swarms import Agent

from autohedge.prompts import (
    DIRECTOR_PROMPT,
    EXECUTION_PROMPT,
    QUANT_PROMPT,
    RISK_PROMPT,
    SENTIMENT_PROMPT,
)
from autohedge.tools.exa_search_tool import exa_search
from autohedge.tools.quiver_research import quiver_research

_NOW = datetime.now()
_DATE_TIME_LINE = _NOW.strftime("%A, %B %d, %Y at %H:%M")
if _NOW.tzinfo:
    _DATE_TIME_LINE += f" {_NOW.tzname() or ''}"
_SYSTEM_SUFFIX = f"\n\nCurrent date and time (use this as now): {_DATE_TIME_LINE.strip()}"

sentiment_agent = Agent(
    agent_name="Sentiment-Agent",
    system_prompt=SENTIMENT_PROMPT + _SYSTEM_SUFFIX,
    model_name="gpt-4o-mini",
    verbose=True,
    max_loops=1,
    tools=[exa_search],
)

alternative_data_agent = Agent(
    agent_name="Alternative-Data-Researcher",
    system_prompt=(
        "You are a read-only alternative-data research analyst. "
        "Use Quiver Quantitative evidence when a ticker is supplied. "
        "Cross-check congressional activity, insider activity, government "
        "contracts, and other available datasets. Distinguish observed data "
        "from interpretation. Never treat alternative data alone as a buy/sell "
        "instruction and never place or request an order. Return concise, "
        "source-aware JSON-friendly findings and explicitly report missing data."
        + _SYSTEM_SUFFIX
    ),
    model_name="gpt-4.1",
    output_type="str",
    max_loops=1,
    verbose=True,
    tools=[quiver_research],
    context_length=16000,
)

risk_agent = Agent(
    agent_name="Risk-Manager",
    system_prompt=RISK_PROMPT.strip()
    + "\n\nWhen you receive a message, it will contain:\nStock, Thesis, Quant Analysis, and Alternative-Data Research.\n\nProvide risk assessment including:\n1. Recommended position size\n2. Maximum drawdown risk\n3. Market risk exposure\n4. Overall risk score\n5. Conflicts or data-quality warnings",
    model_name="gpt-4.1",
    output_type="str",
    max_loops=1,
    verbose=True,
    context_length=16000,
)

execution_agent = Agent(
    agent_name="Execution-Agent",
    system_prompt=EXECUTION_PROMPT.strip()
    + "\n\nWhen you receive a message, it will contain:\nStock, Thesis, Risk Assessment.\n\nGenerate trade order including:\n1. Order type (market/limit)\n2. Quantity\n3. Entry price\n4. Stop loss\n5. Take profit\n6. Time in force",
    model_name="gpt-4.1",
    output_type="str",
    max_loops=1,
    verbose=True,
    context_length=16000,
)

quant_agent = Agent(
    agent_name="Quant-Analyst",
    system_prompt=QUANT_PROMPT.strip()
    + "\n\nWhen you receive a message, it will contain:\nStock and Thesis from your Director.\n\nGenerate quantitative analysis with: ticker, technical_score (0-1), volume_score (0-1), trend_strength (0-1), volatility, probability_score (0-1), key_levels (support, resistance, pivot).",
    model_name="gpt-4.1",
    output_type="str",
    max_loops=1,
    verbose=True,
    context_length=16000,
)

ALL_AGENTS = [
    sentiment_agent,
    alternative_data_agent,
    risk_agent,
    quant_agent,
]

director_agent = Agent(
    agent_name="Trading-Director",
    system_prompt=(
        DIRECTOR_PROMPT
        + "\n\nFor research, request Alternative-Data-Researcher evidence and treat it as one evidence layer alongside price, fundamental, sentiment, and risk analysis. Do not infer causation from congressional, insider, lobbying, or contract activity alone."
        + _SYSTEM_SUFFIX
    ),
    model_name="gpt-4.1",
    max_loops=1,
    handoffs=ALL_AGENTS,
)


if __name__ == "__main__":
    output = director_agent.run(
        "Analyze the stock market and provide a thesis on the overall market position and expected trends."
    )
    print(output)
