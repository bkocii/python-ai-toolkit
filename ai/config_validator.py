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
            raise AIConfigurationError("AI provider cannot be empty.")

        if not config.api_key.strip():
            raise AIConfigurationError("AI API key cannot be empty.")

        if not config.model.strip():
            raise AIConfigurationError("AI model cannot be empty.")

        if config.max_retries < 0:
            raise AIConfigurationError("AI_MAX_RETRIES must be zero or greater.")
