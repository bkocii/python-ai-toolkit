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


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("provider", None, "AI provider must be a string"),
        ("api_key", None, "AI API key must be a string"),
        ("model", 123, "AI model must be a string"),
        ("embedding_model", [], "AI embedding model must be a string"),
    ],
)
def test_config_validator_rejects_non_string_required_values(
    field_name,
    invalid_value,
    message,
):
    config = make_config(**{field_name: invalid_value})

    with pytest.raises(AIConfigurationError, match=message):
        ConfigValidator.validate(config)


@pytest.mark.parametrize("invalid_value", ["1", 1.5, True, None])
def test_config_validator_rejects_non_integer_retry_count(invalid_value):
    config = make_config(max_retries=invalid_value)

    with pytest.raises(
        AIConfigurationError,
        match="AI_MAX_RETRIES must be a whole number",
    ):
        ConfigValidator.validate(config)


@pytest.mark.parametrize("invalid_value", ["512", 512.0, True])
def test_config_validator_rejects_non_integer_embedding_dimensions(
    invalid_value,
):
    config = make_config(embedding_dimensions=invalid_value)

    with pytest.raises(
        AIConfigurationError,
        match="AI_EMBEDDING_DIMENSIONS must be a positive whole number",
    ):
        ConfigValidator.validate(config)


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        (
            "input_cost_per_1m_tokens",
            "not-a-number",
            "Invalid AI_INPUT_COST_PER_1M_TOKENS",
        ),
        (
            "output_cost_per_1m_tokens",
            "-1",
            "Invalid AI_OUTPUT_COST_PER_1M_TOKENS",
        ),
        (
            "input_cost_per_1m_tokens",
            "NaN",
            "Invalid AI_INPUT_COST_PER_1M_TOKENS",
        ),
        (
            "output_cost_per_1m_tokens",
            1,
            "AI_OUTPUT_COST_PER_1M_TOKENS must be a string",
        ),
    ],
)
def test_config_validator_rejects_invalid_custom_costs(
    field_name,
    invalid_value,
    message,
):
    values = {
        "input_cost_per_1m_tokens": "1.25",
        "output_cost_per_1m_tokens": "2.50",
        field_name: invalid_value,
    }
    config = make_config(**values)

    with pytest.raises(AIConfigurationError, match=message):
        ConfigValidator.validate(config)


def test_config_validator_requires_both_custom_costs():
    config = make_config(input_cost_per_1m_tokens="1.25")

    with pytest.raises(
        AIConfigurationError,
        match=(
            "AI_INPUT_COST_PER_1M_TOKENS and "
            "AI_OUTPUT_COST_PER_1M_TOKENS must be configured together"
        ),
    ):
        ConfigValidator.validate(config)


def test_config_validator_accepts_valid_custom_costs():
    config = make_config(
        input_cost_per_1m_tokens="1.25",
        output_cost_per_1m_tokens="2.50",
    )

    ConfigValidator.validate(config)


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("log_level", None, "AI_LOG_LEVEL must be a string"),
        ("log_file_path", None, "AI_LOG_FILE_PATH must be a string"),
        (
            "file_logging_enabled",
            1,
            "AI file logging enabled value must be true or false",
        ),
    ],
)
def test_config_validator_rejects_invalid_logging_types(
    field_name,
    invalid_value,
    message,
):
    config = make_config(**{field_name: invalid_value})

    with pytest.raises(AIConfigurationError, match=message):
        ConfigValidator.validate(config)
