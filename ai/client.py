from typing import TypeVar, overload

from pydantic import BaseModel

from ai.config import get_ai_config
from ai.executor import RequestExecutor
from ai.providers.openai_provider import OpenAIProvider
from ai.schemas import AIResult

T = TypeVar("T", bound=BaseModel)


class AIClient:
    """
    Main public client used by applications.

    AIClient is intentionally small.

    Responsibilities:
    - Load configuration
    - Select provider
    - Expose public ask() and ask_text() methods

    Request execution, retry, parsing, logging, timing, and cost tracking
    are handled by RequestExecutor.
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

        self.executor = RequestExecutor(
            provider=self.provider,
            model=self.model,
        )

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

        If response_type is provided, RequestExecutor handles structured JSON
        parsing and Pydantic validation.
        """
        return self.executor.execute(
            prompt=prompt,
            response_type=response_type,
        )

    def ask_text(self, prompt: str) -> str:
        """
        Backward-compatible shortcut for plain text responses.
        """
        return self.ask(prompt).data
