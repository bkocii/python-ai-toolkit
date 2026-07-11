from ai.config import AIConfig
from ai.exceptions import AIConfigurationError


class ConfigValidator:
    """
    Validate provider-independent AI configuration.

    Provider registration and availability are validated separately
    by ProviderFactory.
    """

    @staticmethod
    def validate(config: AIConfig) -> None:
        if not config.provider.strip():
            raise AIConfigurationError(
                "AI provider cannot be empty. "
                "Set AI_PROVIDER in your .env file, for example AI_PROVIDER=openai."
            )

        if not config.api_key.strip():
            raise AIConfigurationError(
                "AI API key cannot be empty. "
                "Set a provider-specific API key such as OPENAI_API_KEY, "
                "or use AI_API_KEY as a generic fallback."
            )

        if not config.model.strip():
            raise AIConfigurationError(
                "AI model cannot be empty. "
                "Set a provider-specific model such as OPENAI_MODEL, "
                "or use AI_MODEL as a generic fallback."
            )

        if config.max_retries < 0:
            raise AIConfigurationError(
                f"Invalid AI_MAX_RETRIES value '{config.max_retries}'. "
                "Set AI_MAX_RETRIES to zero or greater, for example AI_MAX_RETRIES=1."
            )
