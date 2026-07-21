import pytest

from ai.config import get_ai_config, get_ai_logging_config
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
        "AI_LOG_LEVEL",
        "AI_LOG_FILE_PATH",
        "AI_FILE_LOGGING_ENABLED",
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


def test_get_ai_logging_config_uses_defaults(monkeypatch):
    clear_ai_env(monkeypatch)

    config = get_ai_logging_config()

    assert config.level == "INFO"
    assert config.file_path == "logs/ai_toolkit.log"
    assert config.file_logging_enabled is True


def test_get_ai_logging_config_loads_environment_values(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_LOG_LEVEL", " warning ")
    monkeypatch.setenv("AI_LOG_FILE_PATH", "custom/logs/toolkit.log")
    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", "false")

    config = get_ai_logging_config()

    assert config.level == "WARNING"
    assert config.file_path == "custom/logs/toolkit.log"
    assert config.file_logging_enabled is False


@pytest.mark.parametrize(
    "raw_value",
    [
        "1",
        "true",
        "TRUE",
        "yes",
        "on",
    ],
)
def test_get_ai_logging_config_accepts_enabled_values(
    monkeypatch,
    raw_value,
):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", raw_value)

    config = get_ai_logging_config()

    assert config.file_logging_enabled is True


@pytest.mark.parametrize(
    "raw_value",
    [
        "0",
        "false",
        "FALSE",
        "no",
        "off",
    ],
)
def test_get_ai_logging_config_accepts_disabled_values(
    monkeypatch,
    raw_value,
):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", raw_value)

    config = get_ai_logging_config()

    assert config.file_logging_enabled is False


def test_get_ai_logging_config_rejects_invalid_boolean(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", "maybe")

    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI_FILE_LOGGING_ENABLED value 'maybe'",
    ):
        get_ai_logging_config()


def test_get_ai_logging_config_rejects_invalid_log_level(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_LOG_LEVEL", "verbose")

    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI_LOG_LEVEL value 'VERBOSE'",
    ):
        get_ai_logging_config()


def test_get_ai_logging_config_rejects_empty_enabled_file_path(
    monkeypatch,
):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", "true")
    monkeypatch.setenv("AI_LOG_FILE_PATH", "   ")

    with pytest.raises(
        AIConfigurationError,
        match="AI_LOG_FILE_PATH cannot be empty",
    ):
        get_ai_logging_config()


def test_get_ai_logging_config_allows_empty_disabled_file_path(
    monkeypatch,
):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", "false")
    monkeypatch.setenv("AI_LOG_FILE_PATH", "   ")

    config = get_ai_logging_config()

    assert config.file_logging_enabled is False
    assert config.file_path == ""


def test_get_ai_config_includes_logging_configuration(monkeypatch):
    clear_ai_env(monkeypatch)

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("AI_LOG_FILE_PATH", "runtime/ai.log")
    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", "false")

    config = get_ai_config()

    assert config.log_level == "ERROR"
    assert config.log_file_path == "runtime/ai.log"
    assert config.file_logging_enabled is False
