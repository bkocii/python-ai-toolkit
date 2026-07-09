from typing import Generic, TypeVar

from pydantic import BaseModel

from ai.executor import RequestExecutor
from ai.schemas import AIResult

T = TypeVar("T", bound=BaseModel)


class AIRequestBuilder(Generic[T]):
    """
    Fluent builder for configuring AI requests.

    This builder is intentionally mutable.
    Each configuration method updates the current builder and returns self.
    Execution is still delegated to RequestExecutor.
    """

    def __init__(self, executor: RequestExecutor):
        self._executor = executor
        self._prompt: str | None = None
        self._response_model: type[T] | None = None

    def prompt(self, text: str) -> "AIRequestBuilder[T]":
        self._prompt = text
        return self

    def response_model(self, model: type[T]) -> "AIRequestBuilder[T]":
        self._response_model = model
        return self

    def execute(self) -> AIResult[str] | AIResult[T]:
        if self._prompt is None:
            raise ValueError("Prompt is required before executing an AI request.")

        return self._executor.execute(
            prompt=self._prompt,
            response_type=self._response_model,
        )
