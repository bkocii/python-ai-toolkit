from decimal import Decimal, InvalidOperation
from typing import ClassVar

from ai.config import AIConfig, AILoggingConfig
from ai.exceptions import AIConfigurationError


class ConfigValidator:
    """
    Validate provider-independent AI configuration.

    Provider registration and availability are validated separately
    by ProviderFactory.
    """

    VALID_LOG_LEVELS: ClassVar[frozenset[str]] = frozenset(
        {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }
    )

    @staticmethod
    def _validate_required_string(
        value: object,
        *,
        type_error: str,
        empty_error: str,
    ) -> None:
        if not isinstance(value, str):
            raise AIConfigurationError(type_error)

        if not value.strip():
            raise AIConfigurationError(empty_error)

    @staticmethod
    def _validate_optional_cost(
        value: object,
        *,
        setting_name: str,
    ) -> bool:
        if value is None:
            return False

        if not isinstance(value, str):
            raise AIConfigurationError(
                f"{setting_name} must be a string containing a non-negative number."
            )

        normalized_value = value.strip()

        if not normalized_value:
            return False

        try:
            cost = Decimal(normalized_value)
        except InvalidOperation as exc:
            raise AIConfigurationError(
                f"Invalid {setting_name} value '{value}'. "
                "Set it to a non-negative number."
            ) from exc

        if not cost.is_finite() or cost < 0:
            raise AIConfigurationError(
                f"Invalid {setting_name} value '{value}'. "
                "Set it to a finite, non-negative number."
            )

        return True

    @staticmethod
    def validate(config: AIConfig) -> None:
        ConfigValidator._validate_required_string(
            config.provider,
            type_error="AI provider must be a string.",
            empty_error=(
                "AI provider cannot be empty. "
                "Set AI_PROVIDER in your .env file, for example AI_PROVIDER=openai."
            ),
        )
        ConfigValidator._validate_required_string(
            config.api_key,
            type_error="AI API key must be a string.",
            empty_error=(
                "AI API key cannot be empty. "
                "Set a provider-specific API key such as OPENAI_API_KEY, "
                "or use AI_API_KEY as a generic fallback."
            ),
        )
        ConfigValidator._validate_required_string(
            config.model,
            type_error="AI model must be a string.",
            empty_error=(
                "AI model cannot be empty. "
                "Set a provider-specific model such as OPENAI_MODEL, "
                "or use AI_MODEL as a generic fallback."
            ),
        )

        if isinstance(config.max_retries, bool) or not isinstance(
            config.max_retries,
            int,
        ):
            raise AIConfigurationError(
                "AI_MAX_RETRIES must be a whole number zero or greater."
            )
        if config.max_retries < 0:
            raise AIConfigurationError(
                f"Invalid AI_MAX_RETRIES value '{config.max_retries}'. "
                "Set AI_MAX_RETRIES to zero or greater, for example AI_MAX_RETRIES=1."
            )

        ConfigValidator._validate_required_string(
            config.embedding_model,
            type_error="AI embedding model must be a string.",
            empty_error=(
                "AI embedding model cannot be empty. "
                "Set a provider-specific embedding model such as "
                "OPENAI_EMBEDDING_MODEL, or use AI_EMBEDDING_MODEL as a generic "
                "fallback."
            ),
        )

        if config.embedding_dimensions is not None:
            if isinstance(config.embedding_dimensions, bool) or not isinstance(
                config.embedding_dimensions,
                int,
            ):
                raise AIConfigurationError(
                    "AI_EMBEDDING_DIMENSIONS must be a positive whole number."
                )

            if config.embedding_dimensions <= 0:
                raise AIConfigurationError(
                    "Invalid AI_EMBEDDING_DIMENSIONS value "
                    f"'{config.embedding_dimensions}'. "
                    "Set AI_EMBEDDING_DIMENSIONS to a positive whole number."
                )

        input_cost_configured = ConfigValidator._validate_optional_cost(
            config.input_cost_per_1m_tokens,
            setting_name="AI_INPUT_COST_PER_1M_TOKENS",
        )
        output_cost_configured = ConfigValidator._validate_optional_cost(
            config.output_cost_per_1m_tokens,
            setting_name="AI_OUTPUT_COST_PER_1M_TOKENS",
        )

        if input_cost_configured != output_cost_configured:
            raise AIConfigurationError(
                "AI_INPUT_COST_PER_1M_TOKENS and "
                "AI_OUTPUT_COST_PER_1M_TOKENS must be configured together."
            )

        ConfigValidator.validate_logging(
            AILoggingConfig(
                level=config.log_level,
                file_path=config.log_file_path,
                file_logging_enabled=config.file_logging_enabled,
            )
        )

    @staticmethod
    def validate_logging(config: AILoggingConfig) -> None:
        if not isinstance(config.file_logging_enabled, bool):
            raise AIConfigurationError(
                "AI file logging enabled value must be true or false."
            )

        if not isinstance(config.level, str):
            raise AIConfigurationError("AI_LOG_LEVEL must be a string.")

        if config.level not in ConfigValidator.VALID_LOG_LEVELS:
            valid_levels = ", ".join(sorted(ConfigValidator.VALID_LOG_LEVELS))

            raise AIConfigurationError(
                f"Invalid AI_LOG_LEVEL value '{config.level}'. "
                f"Choose one of: {valid_levels}."
            )

        if not isinstance(config.file_path, str):
            raise AIConfigurationError("AI_LOG_FILE_PATH must be a string.")

        if config.file_logging_enabled and not config.file_path.strip():
            raise AIConfigurationError(
                "AI_LOG_FILE_PATH cannot be empty when file logging is enabled."
            )
