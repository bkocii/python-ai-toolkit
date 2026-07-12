from openai import OpenAI, OpenAIError, AsyncOpenAI
from ai.schemas import ProviderResponse, TokenUsage
from ai.exceptions import AIProviderError
from ai.providers.base import BaseAIProvider
from typing import Iterator


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
