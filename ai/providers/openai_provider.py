from openai import OpenAI, OpenAIError, AsyncOpenAI
from ai.schemas import ProviderResponse, TokenUsage
from ai.exceptions import AIProviderError
from ai.providers.base import BaseAIProvider
from ai.tools import ToolCall, ToolDefinition, ToolResponse
from ai.images import ImageInput
from typing import Iterator, Any
import json


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI implementation of BaseAIProvider.
    """

    def __init__(self, api_key: str, model: str):
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

    def ask_text(self, prompt: str) -> ProviderResponse:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
            )
        except OpenAIError as exc:
            raise AIProviderError(f"OpenAI request failed: {exc}") from exc

        usage = getattr(response, "usage", None)

        token_usage = None
        if usage is not None:
            token_usage = TokenUsage(
                input_tokens=getattr(usage, "input_tokens", None),
                output_tokens=getattr(usage, "output_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            )

        return ProviderResponse(
            text=response.output_text,
            token_usage=token_usage,
        )

    def stream_text(self, prompt: str) -> Iterator[str]:
        """
        Stream plain text chunks from OpenAI.
        """
        try:
            stream = self.client.responses.create(
                model=self.model,
                input=prompt,
                stream=True,
            )

            for event in stream:
                event_type = getattr(event, "type", None)

                if event_type == "response.output_text.delta":
                    delta = getattr(event, "delta", "")

                    if delta:
                        yield delta

                elif event_type == "error":
                    message = getattr(event, "message", "Unknown streaming error")
                    raise AIProviderError(f"OpenAI streaming request failed: {message}")

        except OpenAIError as exc:
            raise AIProviderError(f"OpenAI streaming request failed: {exc}") from exc

    async def ask_text_async(self, prompt: str) -> ProviderResponse:
        """
        Send a prompt to OpenAI asynchronously.
        """
        try:
            response = await self.async_client.responses.create(
                model=self.model,
                input=prompt,
            )
        except OpenAIError as exc:
            raise AIProviderError(f"OpenAI async request failed: {exc}") from exc

        usage = getattr(response, "usage", None)

        token_usage = None
        if usage is not None:
            token_usage = TokenUsage(
                input_tokens=getattr(usage, "input_tokens", None),
                output_tokens=getattr(usage, "output_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            )

        return ProviderResponse(
            text=response.output_text,
            token_usage=token_usage,
        )

    def _to_openai_tool(self, tool: ToolDefinition) -> dict[str, Any]:
        """
        Convert provider-independent tool definition to OpenAI tool format.
        """
        return {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }

    def _parse_tool_arguments(self, raw_arguments: str) -> dict[str, Any]:
        """
        Parse tool call arguments returned by OpenAI.
        """
        try:
            return json.loads(raw_arguments or "{}")
        except json.JSONDecodeError as exc:
            raise AIProviderError(
                f"OpenAI returned invalid tool arguments: {raw_arguments}. "
                "Tool call arguments must be valid JSON."
            ) from exc

    def ask_with_tools(
        self,
        prompt: str,
        tools: list[ToolDefinition],
    ) -> ToolResponse:
        """
        Send a prompt to OpenAI with available tool definitions.
        """
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                tools=[self._to_openai_tool(tool) for tool in tools],
            )
        except OpenAIError as exc:
            raise AIProviderError(f"OpenAI tool request failed: {exc}") from exc

        tool_calls: list[ToolCall] = []

        for item in getattr(response, "output", []):
            if getattr(item, "type", None) != "function_call":
                continue

            tool_calls.append(
                ToolCall(
                    name=getattr(item, "name"),
                    arguments=self._parse_tool_arguments(
                        getattr(item, "arguments", "{}")
                    ),
                    call_id=getattr(item, "call_id", None),
                )
            )

        return ToolResponse(
            text=getattr(response, "output_text", None),
            tool_calls=tool_calls,
        )

    def _to_openai_image_content(self, image: ImageInput) -> dict:
        """
        Convert provider-independent image input to OpenAI image content.
        """
        content = {
            "type": "input_image",
            "image_url": image.source,
        }

        if image.detail is not None:
            content["detail"] = image.detail

        return content

    def ask_with_images(
        self,
        prompt: str,
        images: list[ImageInput],
    ) -> ProviderResponse:
        """
        Send a prompt with image inputs to OpenAI.
        """
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": prompt,
                            },
                            *[self._to_openai_image_content(image) for image in images],
                        ],
                    }
                ],
            )
        except OpenAIError as exc:
            raise AIProviderError(f"OpenAI image request failed: {exc}") from exc

        usage = getattr(response, "usage", None)

        token_usage = None
        if usage is not None:
            token_usage = TokenUsage(
                input_tokens=getattr(usage, "input_tokens", None),
                output_tokens=getattr(usage, "output_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            )

        return ProviderResponse(
            text=response.output_text,
            token_usage=token_usage,
        )
