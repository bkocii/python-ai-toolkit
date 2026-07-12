import asyncio

from pydantic import BaseModel

from ai.async_client import AsyncAIClient
from ai.async_executor import AsyncRequestExecutor
from ai.providers.base import BaseAIProvider
from ai.schemas import ProviderResponse


class DummyResponse(BaseModel):
    answer: str


class FakeAsyncProvider(BaseAIProvider):
    def __init__(self, responses: list[str] | None = None):
        self.responses = responses or ["hello"]
        self.prompts: list[str] = []

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="sync response")

    async def ask_text_async(self, prompt: str) -> ProviderResponse:
        self.prompts.append(prompt)
        return ProviderResponse(text=self.responses.pop(0))


def test_async_executor_returns_plain_text_result():
    async def run_test():
        provider = FakeAsyncProvider(["hello async"])
        executor = AsyncRequestExecutor(
            provider=provider,
            model="fake-model",
        )

        result = await executor.execute("Say hello")

        assert result.data == "hello async"
        assert result.raw_response == "hello async"
        assert provider.prompts == ["Say hello"]

    asyncio.run(run_test())


def test_async_executor_returns_structured_result():
    async def run_test():
        provider = FakeAsyncProvider(['{"answer": "yes"}'])
        executor = AsyncRequestExecutor(
            provider=provider,
            model="fake-model",
        )

        result = await executor.execute(
            prompt="Return JSON",
            response_type=DummyResponse,
        )

        assert isinstance(result.data, DummyResponse)
        assert result.data.answer == "yes"

    asyncio.run(run_test())


def test_async_executor_retries_structured_response():
    async def run_test():
        provider = FakeAsyncProvider(
            [
                "not json",
                '{"answer": "fixed"}',
            ]
        )
        executor = AsyncRequestExecutor(
            provider=provider,
            model="fake-model",
            max_retries=1,
        )

        result = await executor.execute(
            prompt="Return JSON",
            response_type=DummyResponse,
        )

        assert result.data.answer == "fixed"
        assert result.retries_used == 1
        assert len(provider.prompts) == 2

    asyncio.run(run_test())


def test_base_provider_ask_text_async_raises_helpful_error():
    async def run_test():
        class FakeSyncOnlyProvider(BaseAIProvider):
            def ask_text(self, prompt: str) -> ProviderResponse:
                return ProviderResponse(text="sync response")

        provider = FakeSyncOnlyProvider()

        try:
            await provider.ask_text_async("Hello")
        except Exception as exc:
            assert "does not support async requests" in str(exc)
        else:
            raise AssertionError("Expected async provider error")

    asyncio.run(run_test())


def test_async_client_ask_delegates_to_executor():
    async def run_test():
        class FakeExecutor:
            async def execute(self, prompt, response_type=None):
                return f"async: {prompt}"

        ai = AsyncAIClient.__new__(AsyncAIClient)
        ai.executor = FakeExecutor()

        result = await ai.ask("Hello")

        assert result == "async: Hello"

    asyncio.run(run_test())
