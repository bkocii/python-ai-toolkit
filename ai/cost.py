from collections.abc import Mapping
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


def resolve_cost_rates(
    model: str,
    input_cost_per_1m_tokens: str | None = None,
    output_cost_per_1m_tokens: str | None = None,
) -> dict[str, Decimal] | None:
    """
    Resolve token prices once for a model.

    Explicit input and output prices take precedence over the built-in
    model-price table.
    """
    if input_cost_per_1m_tokens and output_cost_per_1m_tokens:
        return {
            "input": Decimal(input_cost_per_1m_tokens),
            "output": Decimal(output_cost_per_1m_tokens),
        }

    model_prices = MODEL_PRICES_USD.get(model)

    if model_prices is None:
        return None

    return dict(model_prices)


def calculate_cost_usd(
    token_usage: TokenUsage | None,
    prices: Mapping[str, Decimal] | None,
) -> Decimal | None:
    """
    Calculate request cost from pre-resolved token prices.

    This function performs no configuration loading or environment access.
    """
    if token_usage is None or prices is None:
        return None

    input_tokens = token_usage.input_tokens or 0
    output_tokens = token_usage.output_tokens or 0

    input_cost = Decimal(input_tokens) / Decimal(1_000_000) * prices["input"]
    output_cost = Decimal(output_tokens) / Decimal(1_000_000) * prices["output"]

    return input_cost + output_cost


def estimate_cost_usd(
    model: str,
    token_usage: TokenUsage | None,
) -> Decimal | None:
    """
    Estimate request cost in USD.

    This compatibility wrapper preserves configuration-based pricing for
    callers that invoke estimate_cost_usd() directly.

    Request executors use pre-resolved pricing through calculate_cost_usd()
    so configuration is not reloaded for every request.
    """
    if token_usage is None:
        return None

    config = get_ai_config()

    prices = resolve_cost_rates(
        model=model,
        input_cost_per_1m_tokens=(config.input_cost_per_1m_tokens),
        output_cost_per_1m_tokens=(config.output_cost_per_1m_tokens),
    )

    return calculate_cost_usd(
        token_usage=token_usage,
        prices=prices,
    )
