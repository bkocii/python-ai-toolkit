import pytest

from ai.config import AIConfig
from ai.exceptions import AIConfigurationError
from ai.providers.base import BaseAIProvider
from ai.providers.factory import ProviderFactory
from ai.providers.openai_provider import OpenAIProvider
from ai.schemas import ProviderResponse


def test_provider_factory_creates_openai_provider_without_network_clients(
    monkeypatch,
):
    sync_client = object()
    async_client = object()

    monkeypatch.setattr(
        "ai.providers.openai_provider.OpenAI",
        lambda **_kwargs: sync_client,
    )
    monkeypatch.setattr(
        "ai.providers.openai_provider.AsyncOpenAI",
        lambda **_kwargs: async_client,
    )

    config = AIConfig(
        api_key="test-key",
        model="test-model",
        provider="openai",
    )

    provider = ProviderFactory.create(config)

    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "test-model"
    assert provider.client is sync_client
    assert provider.async_client is async_client


def test_provider_factory_rejects_unsupported_provider():
    config = AIConfig(
        api_key="test-key",
        model="test-model",
        provider="unsupported",
    )

    with pytest.raises(
        AIConfigurationError,
        match="Unsupported AI provider 'unsupported'",
    ):
        ProviderFactory.create(config)


def test_register_provider(monkeypatch):
    class CustomProvider(OpenAIProvider):
        pass

    monkeypatch.setitem(
        ProviderFactory._registry,
        "custom",
        CustomProvider,
    )

    assert "custom" in ProviderFactory.available_providers()


def test_duplicate_provider_registration_raises_error():
    with pytest.raises(
        AIConfigurationError,
        match="Provider 'openai' is already registered",
    ):
        ProviderFactory.register("openai", OpenAIProvider)


def test_available_providers_contains_openai():
    assert "openai" in ProviderFactory.available_providers()


def test_provider_factory_passes_embedding_config_to_provider():
    class FakeEmbeddingConfiguredProvider(BaseAIProvider):
        def __init__(
            self,
            api_key: str,
            model: str,
            embedding_model: str,
            embedding_dimensions: int | None = None,
        ):
            self.api_key = api_key
            self.model = model
            self.embedding_model = embedding_model
            self.embedding_dimensions = embedding_dimensions

        def ask_text(self, prompt: str) -> ProviderResponse:
            return ProviderResponse(text="ok")

    ProviderFactory.register(
        "fake_embedding_configured",
        FakeEmbeddingConfiguredProvider,
    )

    config = AIConfig(
        api_key="test-key",
        model="test-model",
        provider="fake_embedding_configured",
        embedding_model="test-embedding-model",
        embedding_dimensions=256,
    )

    provider = ProviderFactory.create(config)

    assert provider.embedding_model == "test-embedding-model"
    assert provider.embedding_dimensions == 256

    ProviderFactory._registry.pop("fake_embedding_configured")
