from collections.abc import Mapping
from typing import Any

from django.conf import settings as django_settings

from ai.config import AIConfig
from ai.config_validator import ConfigValidator
from ai.exceptions import AIConfigurationError

DEFAULT_DJANGO_SETTING_NAME = "AI_TOOLKIT"

_ALLOWED_CONFIG_FIELDS = {
    "api_key",
    "model",
    "provider",
    "embedding_model",
    "embedding_dimensions",
    "input_cost_per_1m_tokens",
    "output_cost_per_1m_tokens",
    "max_retries",
    "log_level",
    "log_file_path",
    "file_logging_enabled",
}


def get_django_ai_config(
    setting_name: str = DEFAULT_DJANGO_SETTING_NAME,
) -> AIConfig:
    """
    Build provider-independent AIConfig from Django settings.

    Expected Django setting:

    AI_TOOLKIT = {
        "provider": "openai",
        "api_key": "...",
        "model": "gpt-5.4-mini",
    }
    """
    try:
        raw_config = getattr(django_settings, setting_name)
    except AttributeError as exc:
        raise AIConfigurationError(
            f"Missing Django setting '{setting_name}'. "
            f"Add {setting_name} to your Django settings module."
        ) from exc

    if not isinstance(raw_config, Mapping):
        raise AIConfigurationError(
            f"Django setting '{setting_name}' must be a mapping, "
            "for example a dictionary."
        )

    config_values: dict[str, Any] = dict(raw_config)

    unknown_fields = sorted(set(config_values) - _ALLOWED_CONFIG_FIELDS)

    if unknown_fields:
        formatted_fields = ", ".join(unknown_fields)

        raise AIConfigurationError(
            f"Django setting '{setting_name}' contains unsupported fields: "
            f"{formatted_fields}."
        )

    if "api_key" not in config_values:
        raise AIConfigurationError(
            f"Django setting '{setting_name}' is missing required field 'api_key'."
        )

    provider = config_values.get("provider")

    if isinstance(provider, str):
        config_values["provider"] = provider.strip().lower()

    log_level = config_values.get("log_level")

    if isinstance(log_level, str):
        config_values["log_level"] = log_level.strip().upper()

    log_file_path = config_values.get("log_file_path")

    if isinstance(log_file_path, str):
        config_values["log_file_path"] = log_file_path.strip()

    try:
        config = AIConfig(**config_values)
    except TypeError as exc:
        raise AIConfigurationError(
            f"Invalid Django setting '{setting_name}': {exc}"
        ) from exc

    ConfigValidator.validate(config)

    return config
