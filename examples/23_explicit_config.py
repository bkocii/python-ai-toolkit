"""
Create an AIClient from application-supplied configuration.

Set EXAMPLE_AI_API_KEY before running this example. In a production
application, pass the key from the application's secret manager instead.

The application owns the secret lookup below. Because AIClient receives a
complete AIConfig object, it does not resolve or merge the toolkit's provider,
model, embedding, retry, or logging environment settings.
"""

import os

from ai.client import AIClient
from ai.config import AIConfig
from ai.config_validator import ConfigValidator


def build_ai_client(api_key: str) -> AIClient:
    config = AIConfig(
        provider="openai",
        api_key=api_key,
        model="gpt-5.4-mini",
        embedding_model="text-embedding-3-small",
        max_retries=1,
        log_level="INFO",
        file_logging_enabled=False,
    )

    ConfigValidator.validate(config)
    return AIClient(config=config)


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Set EXAMPLE_AI_API_KEY through your application environment "
            "or replace this lookup with your secret manager."
        )

    client = build_ai_client(api_key)
    result = client.ask("Explain explicit dependency injection in one sentence.")

    print(result.data)
    print()
    print(f"Model: {result.model}")
    print(f"Request ID: {result.request_id}")


if __name__ == "__main__":
    main()
