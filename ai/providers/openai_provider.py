from openai import OpenAI, OpenAIError
from ai.schemas import ProviderResponse, TokenUsage
from ai.exceptions import AIProviderError
from ai.providers.base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI implementation of BaseAIProvider.
    """

    def __init__(self, api_key: str, model: str):
        self.model = model
        self.client = OpenAI(api_key=api_key)

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
