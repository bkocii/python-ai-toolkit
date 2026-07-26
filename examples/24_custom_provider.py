"""
Register and use a custom provider without changing AIClient.

This local provider makes no network request and does not need a real
credential. It implements only the required synchronous plain-text capability.
Registration is process-local and must happen before client construction.
"""

from ai.client import AIClient
from ai.config import AIConfig
from ai.config_validator import ConfigValidator
from ai.providers.base import BaseAIProvider
from ai.providers.factory import ProviderFactory
from ai.schemas import ProviderResponse, TokenUsage

PROVIDER_NAME = "local_echo"


class LocalEchoProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str):
        del api_key
        self.model = model

    def ask_text(self, prompt: str) -> ProviderResponse:
        response_text = f"[{self.model}] {prompt}"
        input_tokens = len(prompt.split())
        output_tokens = len(response_text.split())

        return ProviderResponse(
            text=response_text,
            token_usage=TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
        )


def build_ai_client() -> AIClient:
    ProviderFactory.register(PROVIDER_NAME, LocalEchoProvider)

    config = AIConfig(
        provider=PROVIDER_NAME,
        api_key="not-used-by-local-provider",
        model="local-echo-v1",
        file_logging_enabled=False,
    )

    ConfigValidator.validate(config)
    return AIClient(config=config)


def main() -> None:
    client = build_ai_client()
    result = client.ask("Explain custom provider registration in one sentence.")

    print(result.data)
    print()
    print(f"Model: {result.model}")
    print(f"Token usage: {result.token_usage}")
    print(f"Registered providers: {ProviderFactory.available_providers()}")


if __name__ == "__main__":
    main()
