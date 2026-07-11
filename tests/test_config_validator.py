import pytest

from ai.config import AIConfig
from ai.config_validator import ConfigValidator
from ai.exceptions import AIConfigurationError


def make_config(**overrides) -> AIConfig:
    values = {
        "api_key": "test-key",
        "model": "test-model",
        "provider": "openai",
        "max_retries": 1,
    }

    values.update(overrides)

    return AIConfig(**values)


def test_config_validator_accepts_valid_config():
    config = make_config()

    ConfigValidator.validate(config)


def test_config_validator_rejects_empty_provider():
    config = make_config(provider="   ")

    with pytest.raises(
        AIConfigurationError,
        match="AI provider cannot be empty",
    ):
        ConfigValidator.validate(config)


def test_config_validator_rejects_empty_api_key():
    config = make_config(api_key="   ")

    with pytest.raises(
        AIConfigurationError,
        match="AI API key cannot be empty",
    ):
        ConfigValidator.validate(config)


def test_config_validator_rejects_empty_model():
    config = make_config(model="   ")

    with pytest.raises(
        AIConfigurationError,
        match="AI model cannot be empty",
    ):
        ConfigValidator.validate(config)


def test_config_validator_rejects_negative_retry_count():
    config = make_config(max_retries=-1)

    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI_MAX_RETRIES value '-1'",
    ):
        ConfigValidator.validate(config)
