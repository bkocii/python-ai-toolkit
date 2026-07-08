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

    _registry = {
        "openai": OpenAIProvider,
    }

    @classmethod
    def create(cls, config: AIConfig) -> BaseAIProvider:
        """
        Create a provider instance from the supplied configuration.
        """
        provider_class = cls._registry.get(config.provider)

        if provider_class is None:
            raise ValueError(f"Unsupported AI provider: {config.provider}")

        return provider_class(
            api_key=config.api_key,
            model=config.model,
        )

    @classmethod
    def register(
        cls,
        name: str,
        provider_class: type[BaseAIProvider],
    ) -> None:
        """
        Register a provider implementation.
        """
        if name in cls._registry:
            raise ValueError(f"Provider '{name}' is already registered.")

        cls._registry[name] = provider_class

    @classmethod
    def available_providers(cls) -> tuple[str, ...]:
        """
        Return registered provider names.
        """
        return tuple(sorted(cls._registry.keys()))
