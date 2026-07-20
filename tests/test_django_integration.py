from types import SimpleNamespace

import pytest

from ai.async_client import AsyncAIClient
from ai.client import AIClient
from ai.exceptions import AIConfigurationError
from ai.integrations.django import (
    get_ai_client,
    get_async_ai_client,
    get_django_ai_config,
)


def patch_django_settings(monkeypatch, **settings):
    fake_settings = SimpleNamespace(**settings)

    monkeypatch.setattr(
        "ai.integrations.django.config.django_settings",
        fake_settings,
    )


def test_get_django_ai_config_loads_configuration(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT={
            "provider": "openai",
            "api_key": "test-key",
            "model": "test-model",
            "embedding_model": "test-embedding-model",
            "embedding_dimensions": 512,
            "max_retries": 3,
        },
    )

    config = get_django_ai_config()

    assert config.provider == "openai"
    assert config.api_key == "test-key"
    assert config.model == "test-model"
    assert config.embedding_model == "test-embedding-model"
    assert config.embedding_dimensions == 512
    assert config.max_retries == 3


def test_get_django_ai_config_uses_ai_config_defaults(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT={
            "api_key": "test-key",
        },
    )

    config = get_django_ai_config()

    assert config.provider == "openai"
    assert config.model == "gpt-5.4-mini"
    assert config.embedding_model == "text-embedding-3-small"
    assert config.embedding_dimensions is None
    assert config.max_retries == 1


def test_get_django_ai_config_normalizes_provider(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT={
            "provider": " OpenAI ",
            "api_key": "test-key",
        },
    )

    config = get_django_ai_config()

    assert config.provider == "openai"


def test_get_django_ai_config_supports_custom_setting_name(monkeypatch):
    patch_django_settings(
        monkeypatch,
        CUSTOM_AI_CONFIG={
            "provider": "openai",
            "api_key": "custom-key",
            "model": "custom-model",
        },
    )

    config = get_django_ai_config("CUSTOM_AI_CONFIG")

    assert config.api_key == "custom-key"
    assert config.model == "custom-model"


def test_get_django_ai_config_rejects_missing_setting(monkeypatch):
    patch_django_settings(monkeypatch)

    with pytest.raises(
        AIConfigurationError,
        match="Missing Django setting 'AI_TOOLKIT'",
    ):
        get_django_ai_config()


def test_get_django_ai_config_rejects_non_mapping_setting(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT="not-a-dictionary",
    )

    with pytest.raises(
        AIConfigurationError,
        match="must be a mapping",
    ):
        get_django_ai_config()


def test_get_django_ai_config_rejects_unknown_fields(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT={
            "api_key": "test-key",
            "max_retry": 2,
        },
    )

    with pytest.raises(
        AIConfigurationError,
        match="unsupported fields: max_retry",
    ):
        get_django_ai_config()


def test_get_django_ai_config_rejects_missing_api_key(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT={
            "provider": "openai",
        },
    )

    with pytest.raises(
        AIConfigurationError,
        match="missing required field 'api_key'",
    ):
        get_django_ai_config()


def test_get_ai_client_uses_django_config(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT={
            "provider": "openai",
            "api_key": "test-key",
            "model": "test-model",
        },
    )

    captured = {}

    def fake_client(config):
        captured["config"] = config
        return "sync-client"

    monkeypatch.setattr(
        "ai.integrations.django.client.AIClient",
        fake_client,
    )

    client = get_ai_client()

    assert client == "sync-client"
    assert captured["config"].api_key == "test-key"
    assert captured["config"].model == "test-model"


def test_get_async_ai_client_uses_django_config(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT={
            "provider": "openai",
            "api_key": "test-key",
            "model": "test-model",
        },
    )

    captured = {}

    def fake_client(config):
        captured["config"] = config
        return "async-client"

    monkeypatch.setattr(
        "ai.integrations.django.client.AsyncAIClient",
        fake_client,
    )

    client = get_async_ai_client()

    assert client == "async-client"
    assert captured["config"].api_key == "test-key"
    assert captured["config"].model == "test-model"


def test_client_helpers_return_expected_client_types(monkeypatch):
    patch_django_settings(
        monkeypatch,
        AI_TOOLKIT={
            "provider": "openai",
            "api_key": "test-key",
        },
    )

    class FakeProvider:
        pass

    monkeypatch.setattr(
        "ai.client.ProviderFactory.create",
        lambda config: FakeProvider(),
    )
    monkeypatch.setattr(
        "ai.async_client.ProviderFactory.create",
        lambda config: FakeProvider(),
    )

    sync_client = get_ai_client()
    async_client = get_async_ai_client()

    assert isinstance(sync_client, AIClient)
    assert isinstance(async_client, AsyncAIClient)
