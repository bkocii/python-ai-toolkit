from typing import TypeVar, overload

from pydantic import BaseModel
from ai.request_builder import AIRequestBuilder
from ai.config import get_ai_config
from ai.executor import RequestExecutor
from ai.providers.factory import ProviderFactory
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

        self.provider = ProviderFactory.create(config)

        self.executor = RequestExecutor(
            provider=self.provider,
            model=self.model,
            max_retries=config.max_retries,
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

    def request(self) -> AIRequestBuilder:
        """
        Create a fluent request builder for advanced AI requests.
        """
        return AIRequestBuilder(self.executor)
