import logging
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock
import asyncio

from ai.async_executor import AsyncRequestExecutor
from ai.cost import (
    calculate_cost_usd,
    estimate_cost_usd,
    resolve_cost_rates,
)
from ai.executor import RequestExecutor
from ai.schemas import TokenUsage


class StaticTextProvider:
    def __init__(self) -> None:
        self.response = SimpleNamespace(
            text="Test response",
            token_usage=TokenUsage(
                input_tokens=10,
                output_tokens=5,
                total_tokens=15,
            ),
        )

    def ask_text(self, prompt: str):
        return self.response


class AsyncStaticTextProvider:
    def __init__(self) -> None:
        self.response = SimpleNamespace(
            text="Test response",
            token_usage=TokenUsage(
                input_tokens=10,
                output_tokens=5,
                total_tokens=15,
            ),
        )

    async def ask_text_async(self, prompt: str):
        return self.response


def build_disabled_logger(
    name: str,
) -> logging.Logger:
    logger = logging.Logger(
        name,
        level=logging.CRITICAL,
    )
    logger.propagate = False
    logger.addHandler(logging.NullHandler())

    return logger


def test_resolve_cost_rates_uses_explicit_prices():
    prices = resolve_cost_rates(
        model="custom-model",
        input_cost_per_1m_tokens="2.00",
        output_cost_per_1m_tokens="4.00",
    )

    assert prices == {
        "input": Decimal("2.00"),
        "output": Decimal("4.00"),
    }


def test_resolve_cost_rates_returns_none_for_unknown_model():
    prices = resolve_cost_rates(
        model="unknown-model",
    )

    assert prices is None


def test_calculate_cost_usd_uses_pre_resolved_prices():
    token_usage = TokenUsage(
        input_tokens=500_000,
        output_tokens=250_000,
        total_tokens=750_000,
    )

    prices = {
        "input": Decimal("2.00"),
        "output": Decimal("4.00"),
    }

    cost = calculate_cost_usd(
        token_usage=token_usage,
        prices=prices,
    )

    assert cost == Decimal("2.000")


def test_calculate_cost_usd_returns_none_without_usage():
    cost = calculate_cost_usd(
        token_usage=None,
        prices={
            "input": Decimal("2.00"),
            "output": Decimal("4.00"),
        },
    )

    assert cost is None


def test_calculate_cost_usd_returns_none_without_prices():
    token_usage = TokenUsage(
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
    )

    cost = calculate_cost_usd(
        token_usage=token_usage,
        prices=None,
    )

    assert cost is None


def test_estimate_cost_usd_preserves_config_based_pricing(
    monkeypatch,
):
    monkeypatch.setattr(
        "ai.cost.get_ai_config",
        lambda: SimpleNamespace(
            input_cost_per_1m_tokens="2.00",
            output_cost_per_1m_tokens="4.00",
        ),
    )

    token_usage = TokenUsage(
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
    )

    cost = estimate_cost_usd(
        model="custom-model",
        token_usage=token_usage,
    )

    assert cost == Decimal("0.000040")


def test_request_executor_uses_pre_resolved_custom_prices():
    executor = RequestExecutor(
        provider=StaticTextProvider(),
        model="custom-model",
        logger=build_disabled_logger(
            "test.sync.cost",
        ),
        input_cost_per_1m_tokens="2.00",
        output_cost_per_1m_tokens="4.00",
    )

    result = executor.execute(
        "Test prompt",
    )

    assert result.estimated_cost_usd == Decimal("0.000040")


def test_async_request_executor_uses_pre_resolved_custom_prices():
    async def run_test():
        executor = AsyncRequestExecutor(
            provider=AsyncStaticTextProvider(),
            model="custom-model",
            logger=build_disabled_logger(
                "test.async.cost",
            ),
            input_cost_per_1m_tokens="2.00",
            output_cost_per_1m_tokens="4.00",
        )

        result = await executor.execute(
            "Test prompt",
        )

        assert result.estimated_cost_usd == Decimal("0.000040")

    asyncio.run(run_test())


def test_request_executor_skips_log_metadata_when_info_is_disabled():
    logger = build_disabled_logger(
        "test.sync.logging.guard",
    )

    executor = RequestExecutor(
        provider=StaticTextProvider(),
        model="test-model",
        logger=logger,
    )

    token_usage = Mock()

    executor._log_success(
        request_id="request-1",
        duration_ms=1.0,
        retries_used=0,
        token_usage=token_usage,
        estimated_cost_usd=None,
    )

    token_usage.model_dump.assert_not_called()


def test_async_request_executor_skips_log_metadata_when_info_is_disabled():
    logger = build_disabled_logger(
        "test.async.logging.guard",
    )

    executor = AsyncRequestExecutor(
        provider=AsyncStaticTextProvider(),
        model="test-model",
        logger=logger,
    )

    token_usage = Mock()

    executor._log_success(
        request_id="request-1",
        duration_ms=1.0,
        retries_used=0,
        token_usage=token_usage,
        estimated_cost_usd=None,
    )

    token_usage.model_dump.assert_not_called()
