import pytest
from ai.config import AIConfig
from ai.providers.factory import ProviderFactory
from ai.providers.openai_provider import OpenAIProvider
from ai.exceptions import AIConfigurationError


def test_provider_factory_creates_openai_provider():
    config = AIConfig(
        api_key="test-key",
        model="test-model",
        provider="openai",
    )

    provider = ProviderFactory.create(config)

    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "test-model"


def test_provider_factory_rejects_unsupported_provider():
    AIConfig(
        api_key="test-key",
        model="test-model",
        provider="unsupported",
    )

    with pytest.raises(
        AIConfigurationError,
        match="Provider 'openai' is already registered",
    ):
        ProviderFactory.register("openai", OpenAIProvider)


def test_register_provider():
    class CustomProvider(OpenAIProvider):
        pass

    ProviderFactory.register("custom", CustomProvider)

    assert "custom" in ProviderFactory.available_providers()


def test_duplicate_provider_registration_raises_error():
    with pytest.raises(
        AIConfigurationError,
        match="Provider 'openai' is already registered",
    ):
        ProviderFactory.register("openai", OpenAIProvider)


def test_available_providers_contains_openai():
    assert "openai" in ProviderFactory.available_providers()
