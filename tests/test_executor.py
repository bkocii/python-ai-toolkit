from pydantic import BaseModel

from ai.executor import RequestExecutor
from ai.schemas import ProviderResponse, TokenUsage


class FakeProvider:
    def __init__(self, text: str):
        self.text = text
        self.calls = 0

    def ask_text(self, prompt: str) -> ProviderResponse:
        self.calls += 1
        return ProviderResponse(
            text=self.text,
            token_usage=TokenUsage(
                input_tokens=10,
                output_tokens=5,
                total_tokens=15,
            ),
        )


class SampleResponse(BaseModel):
    name: str


def test_executor_returns_text_result():
    provider = FakeProvider("hello")
    executor = RequestExecutor(provider=provider, model="test-model")

    result = executor.execute("Say hello")

    assert result.data == "hello"
    assert result.model == "test-model"
    assert result.request_id
    assert result.duration_ms is not None
    assert result.token_usage.total_tokens == 15


def test_executor_returns_schema_result():
    provider = FakeProvider('{"name": "Genius Green"}')
    executor = RequestExecutor(provider=provider, model="test-model")

    result = executor.execute(
        prompt="Return product",
        response_type=SampleResponse,
    )

    assert result.data.name == "Genius Green"
    assert result.retries_used == 0
    assert provider.calls == 1
