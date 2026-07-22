import logging
from collections.abc import Callable

import pytest

from ai.schemas import ProviderResponse, TokenUsage
from benchmarks.fakes import (
    FakeAsyncTextProvider,
    FakeTextProvider,
    SequenceTextProvider,
)


@pytest.fixture(autouse=True)
def disable_benchmark_file_logging(monkeypatch):
    """
    Disable toolkit-managed file logging for configuration-loaded clients.
    """
    monkeypatch.setenv(
        "AI_FILE_LOGGING_ENABLED",
        "false",
    )


@pytest.fixture
def benchmark_logger() -> logging.Logger:
    """
    Return an isolated logger that performs no file or console I/O.

    Directly constructed executors must receive this logger explicitly.
    """
    logger = logging.Logger(
        "ai_toolkit.benchmark",
        level=logging.CRITICAL,
    )
    logger.propagate = False
    logger.addHandler(logging.NullHandler())

    return logger


@pytest.fixture
def benchmark_token_usage() -> TokenUsage:
    return TokenUsage(
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
    )


@pytest.fixture
def benchmark_provider_response(
    benchmark_token_usage: TokenUsage,
) -> ProviderResponse:
    return ProviderResponse(
        text="Benchmark response",
        token_usage=benchmark_token_usage,
    )


@pytest.fixture
def fake_text_provider(
    benchmark_token_usage: TokenUsage,
) -> FakeTextProvider:
    return FakeTextProvider(
        response_text="Benchmark response",
        token_usage=benchmark_token_usage,
    )


@pytest.fixture
def fake_async_text_provider(
    benchmark_token_usage: TokenUsage,
) -> FakeAsyncTextProvider:
    return FakeAsyncTextProvider(
        response_text="Benchmark response",
        token_usage=benchmark_token_usage,
    )


@pytest.fixture
def make_sequence_text_provider(
    benchmark_token_usage: TokenUsage,
) -> Callable[[list[str]], SequenceTextProvider]:
    def factory(
        responses: list[str],
    ) -> SequenceTextProvider:
        return SequenceTextProvider(
            responses=responses,
            token_usage=benchmark_token_usage,
        )

    return factory
