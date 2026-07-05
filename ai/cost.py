from decimal import Decimal
from ai.config import get_ai_config
from ai.schemas import TokenUsage

# Prices are per 1M tokens.
# Update these when model pricing changes.
MODEL_PRICES_USD = {
    "gpt-5.4-mini": {
        "input": Decimal("0.00"),
        "output": Decimal("0.00"),
    }
}


def estimate_cost_usd(model: str, token_usage: TokenUsage | None) -> Decimal | None:
    """
    Estimate request cost in USD.

    Returns None if:
    - token usage is missing
    - model pricing is unknown
    """
    if token_usage is None:
        return None

    config = get_ai_config()

    if config.input_cost_per_1m_tokens and config.output_cost_per_1m_tokens:
        prices = {
            "input": Decimal(config.input_cost_per_1m_tokens),
            "output": Decimal(config.output_cost_per_1m_tokens),
        }
    else:
        prices = MODEL_PRICES_USD.get(model)

    if prices is None:
        return None

    input_tokens = token_usage.input_tokens or 0
    output_tokens = token_usage.output_tokens or 0

    input_cost = Decimal(input_tokens) / Decimal(1_000_000) * prices["input"]
    output_cost = Decimal(output_tokens) / Decimal(1_000_000) * prices["output"]

    return input_cost + output_cost
