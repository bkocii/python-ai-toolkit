import pytest

from ai.client import AIClient
from ai.exceptions import AIProviderError
from ai.executor import RequestExecutor
from ai.providers.base import BaseAIProvider
from ai.schemas import ProviderResponse
from ai.tools import ToolCall, ToolDefinition, ToolResponse
from ai.providers.openai_provider import OpenAIProvider


class FakeToolProvider(BaseAIProvider):
    def __init__(self):
        self.received_prompt = None
        self.received_tools = None

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="plain response")

    def ask_with_tools(
        self,
        prompt: str,
        tools: list[ToolDefinition],
    ) -> ToolResponse:
        self.received_prompt = prompt
        self.received_tools = tools

        return ToolResponse(
            text=None,
            tool_calls=[
                ToolCall(
                    name="get_weather",
                    arguments={"location": "Paris"},
                    call_id="call_123",
                )
            ],
        )


class FakeNonToolProvider(BaseAIProvider):
    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="plain response")


def test_tool_definition_stores_schema():
    tool = ToolDefinition(
        name="get_weather",
        description="Get current weather for a city.",
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string"},
            },
            "required": ["location"],
        },
    )

    assert tool.name == "get_weather"
    assert tool.description == "Get current weather for a city."
    assert tool.parameters["properties"]["location"]["type"] == "string"


def test_tool_response_stores_tool_calls():
    response = ToolResponse(
        tool_calls=[
            ToolCall(
                name="get_weather",
                arguments={"location": "Paris"},
                call_id="call_123",
            )
        ]
    )

    assert response.text is None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "get_weather"
    assert response.tool_calls[0].arguments == {"location": "Paris"}


def test_base_provider_ask_with_tools_raises_helpful_error():
    provider = FakeNonToolProvider()
    tool = ToolDefinition(
        name="get_weather",
        description="Get weather.",
    )

    with pytest.raises(
        AIProviderError,
        match="does not support tool calling",
    ):
        provider.ask_with_tools(
            prompt="What is the weather?",
            tools=[tool],
        )


def test_request_executor_execute_with_tools_delegates_to_provider():
    provider = FakeToolProvider()
    executor = RequestExecutor(
        provider=provider,
        model="fake-model",
    )
    tool = ToolDefinition(
        name="get_weather",
        description="Get weather.",
    )

    response = executor.execute_with_tools(
        prompt="What is the weather in Paris?",
        tools=[tool],
    )

    assert provider.received_prompt == "What is the weather in Paris?"
    assert provider.received_tools == [tool]
    assert response.tool_calls[0].name == "get_weather"
    assert response.tool_calls[0].arguments == {"location": "Paris"}


def test_ai_client_ask_with_tools_delegates_to_executor():
    class FakeExecutor:
        def execute_with_tools(
            self,
            prompt: str,
            tools: list[ToolDefinition],
        ) -> ToolResponse:
            return ToolResponse(
                tool_calls=[
                    ToolCall(
                        name="search_docs",
                        arguments={"query": prompt},
                    )
                ]
            )

    ai = AIClient.__new__(AIClient)
    ai.executor = FakeExecutor()

    tool = ToolDefinition(
        name="search_docs",
        description="Search documents.",
    )

    response = ai.ask_with_tools(
        prompt="Find project notes",
        tools=[tool],
    )

    assert response.tool_calls[0].name == "search_docs"
    assert response.tool_calls[0].arguments == {"query": "Find project notes"}


def test_openai_provider_converts_tool_definition_to_openai_format():
    provider = OpenAIProvider.__new__(OpenAIProvider)

    tool = ToolDefinition(
        name="get_weather",
        description="Get current weather for a city.",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name",
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        },
    )

    result = provider._to_openai_tool(tool)

    assert result == {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name",
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        },
    }


def test_openai_provider_parses_tool_arguments():
    provider = OpenAIProvider.__new__(OpenAIProvider)

    result = provider._parse_tool_arguments('{"location": "Paris"}')

    assert result == {"location": "Paris"}


def test_openai_provider_rejects_invalid_tool_arguments():
    provider = OpenAIProvider.__new__(OpenAIProvider)

    with pytest.raises(
        AIProviderError,
        match="OpenAI returned invalid tool arguments",
    ):
        provider._parse_tool_arguments("{not valid json}")
