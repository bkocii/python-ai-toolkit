from ai.config import AIConfig
from ai.providers.base import BaseAIProvider
from ai.providers.openai_provider import OpenAIProvider

PROVIDER_REGISTRY = {
    "openai": OpenAIProvider,
}


class ProviderFactory:
    """
    Factory responsible for creating AI providers.

    AIClient delegates provider creation to this class,
    keeping provider selection logic out of the client.
    """

    @staticmethod
    def create(config: AIConfig) -> BaseAIProvider:
        """
        Create a provider instance from the supplied configuration.
        """
        provider_class = PROVIDER_REGISTRY.get(config.provider)

        if provider_class is None:
            raise ValueError(f"Unsupported AI provider: {config.provider}")

        return provider_class(
            api_key=config.api_key,
            model=config.model,
        )
