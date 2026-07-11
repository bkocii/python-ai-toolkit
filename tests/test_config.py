import pytest

from ai.config import get_ai_config
from ai.exceptions import AIConfigurationError


def clear_ai_env(monkeypatch):
    keys = [
        "AI_PROVIDER",
        "AI_API_KEY",
        "AI_MODEL",
        "AI_MAX_RETRIES",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_MODEL",
        "AI_INPUT_COST_PER_1M_TOKENS",
        "AI_OUTPUT_COST_PER_1M_TOKENS",
    ]

    for key in keys:
        monkeypatch.delenv(key, raising=False)


def test_get_ai_config_loads_openai_provider_config(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "openai-model")

    config = get_ai_config()

    assert config.provider == "openai"
    assert config.api_key == "openai-key"
    assert config.model == "openai-model"


def test_get_ai_config_supports_generic_fallback(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_PROVIDER", "custom")
    monkeypatch.setenv("AI_API_KEY", "generic-key")
    monkeypatch.setenv("AI_MODEL", "generic-model")

    config = get_ai_config()

    assert config.provider == "custom"
    assert config.api_key == "generic-key"
    assert config.model == "generic-model"


def test_get_ai_config_normalizes_provider_name(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_PROVIDER", " OpenAI ")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")

    config = get_ai_config()

    assert config.provider == "openai"


def test_get_ai_config_raises_error_when_api_key_missing(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_PROVIDER", "anthropic")

    with pytest.raises(
        AIConfigurationError,
        match="ANTHROPIC_API_KEY or AI_API_KEY is missing",
    ):
        get_ai_config()


def test_get_ai_config_rejects_invalid_retry_count(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AI_MAX_RETRIES", "not-a-number")

    with pytest.raises(AIConfigurationError, match="AI_MAX_RETRIES must be an integer"):
        get_ai_config()


def test_get_ai_config_rejects_negative_retry_count(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AI_MAX_RETRIES", "-1")

    with pytest.raises(
        AIConfigurationError, match="AI_MAX_RETRIES must be zero or greater"
    ):
        get_ai_config()


def test_get_ai_config_validates_loaded_model(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "   ")

    with pytest.raises(
        AIConfigurationError,
        match="AI model cannot be empty",
    ):
        get_ai_config()
