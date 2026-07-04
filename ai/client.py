from ai.config import get_ai_config
from ai.providers.openai_provider import OpenAIProvider


class AIClient:
    """
    Main public client used by applications.

    AIClient does not know provider-specific API details.
    It delegates actual model calls to a provider class.
    """

    def __init__(self):
        config = get_ai_config()

        if config.provider == "openai":
            self.provider = OpenAIProvider(
                api_key=config.api_key,
                model=config.model,
            )
        else:
            raise ValueError(f"Unsupported AI provider: {config.provider}")

    def ask_text(self, prompt: str) -> str:
        return self.provider.ask_text(prompt)
