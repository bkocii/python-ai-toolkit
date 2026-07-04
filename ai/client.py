from openai import OpenAI

from ai.config import get_ai_config


class AIClient:
    """
    Reusable wrapper around the OpenAI client.

    Goal:
    - One place for model configuration.
    - One place for future logging, retries, caching, and cost tracking.
    """

    def __init__(self, model: str | None = None):
        config = get_ai_config()

        self.model = model or config.model
        self.client = OpenAI(api_key=config.api_key)

    def ask_text(self, prompt: str) -> str:
        """
        Send a plain text prompt to the model and return plain text.

        Later we will add:
        - ask_json()
        - ask_schema()
        - tool calling
        - retries
        """
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text