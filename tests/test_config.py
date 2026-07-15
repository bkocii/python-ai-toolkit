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
        "OPENAI_EMBEDDING_MODEL",
        "AI_EMBEDDING_MODEL",
        "AI_EMBEDDING_DIMENSIONS",
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
        match="Missing API key for provider 'anthropic'",
    ):
        get_ai_config()


def test_get_ai_config_rejects_invalid_retry_count(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AI_MAX_RETRIES", "not-a-number")

    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI_MAX_RETRIES value 'not-a-number'",
    ):
        get_ai_config()


def test_get_ai_config_rejects_negative_retry_count(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AI_MAX_RETRIES", "-1")

    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI_MAX_RETRIES value '-1'",
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


def test_get_ai_config_loads_provider_specific_embedding_model(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")

    config = get_ai_config()

    assert config.embedding_model == "text-embedding-3-large"


def test_get_ai_config_supports_generic_embedding_model_fallback(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AI_EMBEDDING_MODEL", "custom-embedding-model")

    config = get_ai_config()

    assert config.embedding_model == "custom-embedding-model"


def test_get_ai_config_loads_embedding_dimensions(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AI_EMBEDDING_DIMENSIONS", "512")

    config = get_ai_config()

    assert config.embedding_dimensions == 512


def test_get_ai_config_rejects_invalid_embedding_dimensions(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AI_EMBEDDING_DIMENSIONS", "many")

    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI_EMBEDDING_DIMENSIONS value 'many'",
    ):
        get_ai_config()


def test_get_ai_config_rejects_negative_embedding_dimensions(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AI_EMBEDDING_DIMENSIONS", "-1")

    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI_EMBEDDING_DIMENSIONS value '-1'",
    ):
        get_ai_config()
