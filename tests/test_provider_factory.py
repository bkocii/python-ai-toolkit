import pytest
from ai.config import AIConfig
from ai.providers.factory import PROVIDER_REGISTRY, ProviderFactory
from ai.providers.openai_provider import OpenAIProvider


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
    config = AIConfig(
        api_key="test-key",
        model="test-model",
        provider="unsupported",
    )

    with pytest.raises(ValueError, match="Unsupported AI provider"):
        ProviderFactory.create(config)


def test_provider_registry_contains_openai_provider():
    assert PROVIDER_REGISTRY["openai"] is OpenAIProvider
