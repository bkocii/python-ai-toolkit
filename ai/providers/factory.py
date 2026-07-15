from ai.config import AIConfig
from ai.exceptions import AIConfigurationError
from ai.providers.base import BaseAIProvider
from ai.providers.openai_provider import OpenAIProvider
from inspect import Parameter, signature


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
    def _build_provider_kwargs(
        cls,
        provider_class: type[BaseAIProvider],
        config: AIConfig,
    ) -> dict:
        """
        Build constructor kwargs for a provider.

        Required provider arguments are always passed.
        Optional advanced capability arguments are passed only when the
        provider constructor accepts them.
        """
        kwargs = {
            "api_key": config.api_key,
            "model": config.model,
        }

        parameters = signature(provider_class).parameters

        accepts_kwargs = any(
            parameter.kind == Parameter.VAR_KEYWORD for parameter in parameters.values()
        )

        optional_kwargs = {
            "embedding_model": config.embedding_model,
            "embedding_dimensions": config.embedding_dimensions,
        }

        for name, value in optional_kwargs.items():
            if accepts_kwargs or name in parameters:
                kwargs[name] = value

        return kwargs

    @classmethod
    def create(cls, config: AIConfig) -> BaseAIProvider:
        """
        Create a provider instance from the supplied configuration.
        """
        provider_class = cls._registry.get(config.provider)

        if provider_class is None:
            available = ", ".join(cls.available_providers())

            raise AIConfigurationError(
                f"Unsupported AI provider '{config.provider}'. "
                f"Available providers: {available}. "
                "Set AI_PROVIDER to a registered provider or register "
                "a custom provider before creating AIClient."
            )

        return provider_class(
            **cls._build_provider_kwargs(
                provider_class=provider_class,
                config=config,
            )
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
            raise AIConfigurationError(
                f"Provider '{name}' is already registered. "
                "Choose a different provider name or remove the existing registration."
            )

        cls._registry[name] = provider_class

    @classmethod
    def available_providers(cls) -> tuple[str, ...]:
        """
        Return registered provider names.
        """
        return tuple(sorted(cls._registry.keys()))
