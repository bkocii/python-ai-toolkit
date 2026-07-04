from openai import OpenAI

from ai.providers.base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI implementation of BaseAIProvider.
    """

    def __init__(self, api_key: str, model: str):
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def ask_text(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text
