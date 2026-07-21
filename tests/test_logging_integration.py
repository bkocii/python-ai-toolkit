import logging

from ai.async_client import AsyncAIClient
from ai.async_executor import AsyncRequestExecutor
from ai.client import AIClient
from ai.config import AIConfig
from ai.executor import RequestExecutor


def test_request_executor_uses_injected_logger():
    logger = logging.getLogger("test-sync-executor")

    executor = RequestExecutor(
        provider=object(),
        model="fake-model",
        logger=logger,
    )

    assert executor.logger is logger


def test_async_request_executor_uses_injected_logger():
    logger = logging.getLogger("test-async-executor")

    executor = AsyncRequestExecutor(
        provider=object(),
        model="fake-model",
        logger=logger,
    )

    assert executor.logger is logger


def test_request_executor_uses_default_logger_when_not_injected(
    monkeypatch,
):
    expected_logger = logging.getLogger("default-sync-logger")

    monkeypatch.setattr(
        "ai.executor.get_ai_logger",
        lambda: expected_logger,
    )

    executor = RequestExecutor(
        provider=object(),
        model="fake-model",
    )

    assert executor.logger is expected_logger


def test_async_request_executor_uses_default_logger_when_not_injected(
    monkeypatch,
):
    expected_logger = logging.getLogger("default-async-logger")

    monkeypatch.setattr(
        "ai.async_executor.get_ai_logger",
        lambda: expected_logger,
    )

    executor = AsyncRequestExecutor(
        provider=object(),
        model="fake-model",
    )

    assert executor.logger is expected_logger


def test_ai_client_configures_and_injects_logger(monkeypatch):
    config = AIConfig(
        provider="openai",
        api_key="test-key",
        model="test-model",
        log_level="ERROR",
        log_file_path="custom/toolkit.log",
        file_logging_enabled=False,
    )

    provider = object()
    expected_logger = logging.getLogger("configured-sync-logger")
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "ai.client.ProviderFactory.create",
        lambda supplied_config: provider,
    )

    def fake_get_ai_logger(
        level,
        file_path,
        file_logging_enabled,
    ):
        captured["level"] = level
        captured["file_path"] = file_path
        captured["file_logging_enabled"] = file_logging_enabled
        return expected_logger

    monkeypatch.setattr(
        "ai.client.get_ai_logger",
        fake_get_ai_logger,
    )

    client = AIClient(config=config)

    assert client.provider is provider
    assert client.executor.logger is expected_logger
    assert captured == {
        "level": "ERROR",
        "file_path": "custom/toolkit.log",
        "file_logging_enabled": False,
    }


def test_async_ai_client_configures_and_injects_logger(monkeypatch):
    config = AIConfig(
        provider="openai",
        api_key="test-key",
        model="test-model",
        log_level="WARNING",
        log_file_path="custom/async-toolkit.log",
        file_logging_enabled=False,
    )

    provider = object()
    expected_logger = logging.getLogger("configured-async-logger")
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "ai.async_client.ProviderFactory.create",
        lambda supplied_config: provider,
    )

    def fake_get_ai_logger(
        level,
        file_path,
        file_logging_enabled,
    ):
        captured["level"] = level
        captured["file_path"] = file_path
        captured["file_logging_enabled"] = file_logging_enabled
        return expected_logger

    monkeypatch.setattr(
        "ai.async_client.get_ai_logger",
        fake_get_ai_logger,
    )

    client = AsyncAIClient(config=config)

    assert client.provider is provider
    assert client.executor.logger is expected_logger
    assert captured == {
        "level": "WARNING",
        "file_path": "custom/async-toolkit.log",
        "file_logging_enabled": False,
    }
