from typing import TypeVar, overload

from pydantic import BaseModel

from ai.config import get_ai_config
from ai.parser import parse_json_response
from ai.providers.openai_provider import OpenAIProvider
from ai.schemas import AIResult

T = TypeVar("T", bound=BaseModel)


class AIClient:
    """
    Main public client used by applications.

    AIClient decides how to handle a request based on response_type:

    - response_type is None:
        Return plain text.

    - response_type is a Pydantic model:
        Request structured JSON and validate it.
    """

    def __init__(self):
        config = get_ai_config()
        self.model = config.model

        if config.provider == "openai":
            self.provider = OpenAIProvider(
                api_key=config.api_key,
                model=config.model,
            )
        else:
            raise ValueError(f"Unsupported AI provider: {config.provider}")

    @overload
    def ask(self, prompt: str) -> AIResult[str]: ...

    @overload
    def ask(self, prompt: str, response_type: type[T]) -> AIResult[T]: ...

    def ask(
        self,
        prompt: str,
        response_type: type[T] | None = None,
    ) -> AIResult[str] | AIResult[T]:
        """
        Send a prompt to the configured provider.

        If response_type is provided, the model is instructed to return JSON,
        and the result is validated against that Pydantic schema.
        """
        final_prompt = prompt

        if response_type is not None:
            schema_json = response_type.model_json_schema()

            final_prompt = f"""
{prompt}

Return valid JSON only.
The JSON must match this schema:
{schema_json}
"""

        raw_response = self.provider.ask_text(final_prompt)

        if response_type is None:
            return AIResult(
                data=raw_response,
                model=self.model,
                raw_response=raw_response,
            )

        parsed = parse_json_response(raw_response, response_type)

        return AIResult(
            data=parsed,
            model=self.model,
            raw_response=raw_response,
        )

    def ask_text(self, prompt: str) -> str:
        """
        Backward-compatible shortcut for plain text responses.
        """
        return self.ask(prompt).data
