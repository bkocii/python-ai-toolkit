import asyncio

import pytest

from ai.schemas import TokenUsage
from benchmarks.fakes import (
    FakeAsyncTextProvider,
    FakeTextProvider,
    SequenceTextProvider,
)


def make_token_usage() -> TokenUsage:
    return TokenUsage(
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
    )


def test_fake_text_provider_returns_configured_response():
    provider = FakeTextProvider(
        response_text="Static response",
        token_usage=make_token_usage(),
    )

    response = provider.ask_text("Ignored prompt")

    assert response.text == "Static response"
    assert response.token_usage is not None
    assert response.token_usage.total_tokens == 15


def test_fake_text_provider_returns_prebuilt_response():
    provider = FakeTextProvider(
        response_text="Static response",
        token_usage=make_token_usage(),
    )

    first_response = provider.ask_text("First prompt")
    second_response = provider.ask_text("Second prompt")

    assert first_response is second_response


def test_fake_async_text_provider_returns_configured_response():
    provider = FakeAsyncTextProvider(
        response_text="Async response",
        token_usage=make_token_usage(),
    )

    response = asyncio.run(provider.ask_text_async("Ignored prompt"))

    assert response.text == "Async response"
    assert response.token_usage is not None
    assert response.token_usage.total_tokens == 15


def test_sequence_text_provider_returns_responses_in_order():
    provider = SequenceTextProvider(
        responses=[
            "First response",
            "Second response",
        ],
        token_usage=make_token_usage(),
    )

    first_response = provider.ask_text("First prompt")
    second_response = provider.ask_text("Second prompt")

    assert first_response.text == "First response"
    assert second_response.text == "Second response"
    assert provider.call_count == 2


def test_sequence_text_provider_rejects_empty_response_list():
    with pytest.raises(
        ValueError,
        match="requires at least one response",
    ):
        SequenceTextProvider(responses=[])


def test_sequence_text_provider_raises_when_exhausted():
    provider = SequenceTextProvider(
        responses=["Only response"],
    )

    provider.ask_text("First prompt")

    with pytest.raises(
        RuntimeError,
        match="no remaining responses",
    ):
        provider.ask_text("Unexpected second prompt")
