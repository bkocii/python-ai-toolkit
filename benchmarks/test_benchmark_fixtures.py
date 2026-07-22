import logging

from benchmarks.fakes import (
    FakeAsyncTextProvider,
    FakeTextProvider,
    SequenceTextProvider,
)


def test_fake_text_provider_fixture(
    fake_text_provider,
):
    assert isinstance(
        fake_text_provider,
        FakeTextProvider,
    )

    response = fake_text_provider.ask_text("Benchmark prompt")

    assert response.text == "Benchmark response"


def test_fake_async_text_provider_fixture(
    fake_async_text_provider,
):
    assert isinstance(
        fake_async_text_provider,
        FakeAsyncTextProvider,
    )


def test_sequence_provider_factory_fixture(
    make_sequence_text_provider,
):
    provider = make_sequence_text_provider(
        [
            "Invalid response",
            "Valid response",
        ]
    )

    assert isinstance(
        provider,
        SequenceTextProvider,
    )
    assert provider.ask_text("First").text == "Invalid response"
    assert provider.ask_text("Second").text == "Valid response"


def test_benchmark_logger_uses_no_file_handler(
    benchmark_logger,
):
    assert benchmark_logger.propagate is False

    assert any(
        isinstance(handler, logging.NullHandler)
        for handler in benchmark_logger.handlers
    )

    assert not any(
        isinstance(handler, logging.FileHandler)
        for handler in benchmark_logger.handlers
    )
