import pytest
from pydantic import BaseModel

from ai.request_builder import AIRequestBuilder
from ai.schemas import AIResult


class DummyResponse(BaseModel):
    answer: str


class FakeExecutor:
    def __init__(self):
        self.received_prompt = None
        self.received_response_type = None

    def execute(self, prompt, response_type=None):
        self.received_prompt = prompt
        self.received_response_type = response_type

        return AIResult(
            data="ok",
            model="fake-model",
            duration_ms=1,
            retries_used=0,
            request_id="test-request-id",
            token_usage=None,
            estimated_cost_usd=None,
            cached=False,
            raw_response="ok",
            original_raw_response=None,
        )


def test_request_builder_executes_plain_text_request():
    executor = FakeExecutor()

    result = (
        AIRequestBuilder(executor)
        .prompt("Hello")
        .execute()
    )

    assert result.data == "ok"
    assert executor.received_prompt == "Hello"
    assert executor.received_response_type is None


def test_request_builder_executes_structured_request():
    executor = FakeExecutor()

    result = (
        AIRequestBuilder(executor)
        .prompt("Return JSON")
        .response_type(DummyResponse)
        .execute()
    )

    assert result.data == "ok"
    assert executor.received_prompt == "Return JSON"
    assert executor.received_response_type is DummyResponse


def test_request_builder_requires_prompt_before_execute():
    executor = FakeExecutor()

    with pytest.raises(ValueError, match="Prompt is required"):
        AIRequestBuilder(executor).execute()


def test_request_builder_methods_are_fluent():
    executor = FakeExecutor()
    builder = AIRequestBuilder(executor)

    assert builder.prompt("Hello") is builder
    assert builder.response_type(DummyResponse) is builder

