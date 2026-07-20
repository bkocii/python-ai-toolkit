from ai.client import AIClient
from ai.config import AIConfig
from ai.providers.factory import ProviderFactory
from ai.providers.base import BaseAIProvider
from ai.schemas import ProviderResponse


class FakeProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="fake response")


def test_client_accepts_explicit_config(monkeypatch):
    config = AIConfig(
        provider="fake",
        api_key="fake-key",
        model="fake-model",
        max_retries=3,
    )

    monkeypatch.setitem(
        ProviderFactory._registry,
        "fake",
        FakeProvider,
    )

    client = AIClient(config=config)

    assert client.model == "fake-model"
    assert isinstance(client.provider, FakeProvider)
    assert client.provider.api_key == "fake-key"
    assert client.executor.max_retries == 3


def test_client_loads_environment_config_when_config_not_supplied(monkeypatch):
    config = AIConfig(
        provider="fake",
        api_key="environment-key",
        model="environment-model",
        max_retries=2,
    )

    monkeypatch.setattr(
        "ai.client.get_ai_config",
        lambda: config,
    )
    monkeypatch.setitem(
        ProviderFactory._registry,
        "fake",
        FakeProvider,
    )

    client = AIClient()

    assert client.model == "environment-model"
    assert client.provider.api_key == "environment-key"
    assert client.executor.max_retries == 2
