import pytest

from ai.client import AIClient
from ai.exceptions import AIProviderError
from ai.executor import RequestExecutor
from ai.providers.base import BaseAIProvider
from ai.schemas import ProviderResponse


class FakeStreamingProvider(BaseAIProvider):
    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="full response")

    def stream_text(self, prompt: str):
        yield "Hello"
        yield " "
        yield "world"


class FakeNonStreamingProvider(BaseAIProvider):
    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="full response")


def test_request_executor_streams_text_chunks():
    provider = FakeStreamingProvider()
    executor = RequestExecutor(
        provider=provider,
        model="fake-model",
    )

    chunks = list(executor.stream("Say hello"))

    assert chunks == ["Hello", " ", "world"]


def test_base_provider_stream_text_raises_helpful_error():
    provider = FakeNonStreamingProvider()

    with pytest.raises(
        AIProviderError,
        match="does not support streaming",
    ):
        list(provider.stream_text("Say hello"))


def test_ai_client_stream_delegates_to_executor(monkeypatch):
    class FakeExecutor:
        def stream(self, prompt: str):
            yield f"streamed: {prompt}"

    ai = AIClient.__new__(AIClient)
    ai.executor = FakeExecutor()

    chunks = list(ai.stream("Hello"))

    assert chunks == ["streamed: Hello"]
