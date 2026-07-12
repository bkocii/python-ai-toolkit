from typing import TypeVar, overload

from pydantic import BaseModel

from ai.async_executor import AsyncRequestExecutor
from ai.config import get_ai_config
from ai.providers.factory import ProviderFactory
from ai.schemas import AIResult

T = TypeVar("T", bound=BaseModel)


class AsyncAIClient:
    """
    Async public client used by applications.

    AsyncAIClient mirrors AIClient, but uses AsyncRequestExecutor
    and provider async methods.
    """

    def __init__(self):
        config = get_ai_config()
        self.model = config.model

        self.provider = ProviderFactory.create(config)

        self.executor = AsyncRequestExecutor(
            provider=self.provider,
            model=self.model,
            max_retries=config.max_retries,
        )

    @overload
    async def ask(self, prompt: str) -> AIResult[str]: ...

    @overload
    async def ask(self, prompt: str, response_type: type[T]) -> AIResult[T]: ...

    async def ask(
        self,
        prompt: str,
        response_type: type[T] | None = None,
    ) -> AIResult[str] | AIResult[T]:
        """
        Send a prompt asynchronously to the configured provider.

        If response_type is provided, AsyncRequestExecutor handles structured JSON
        parsing and Pydantic validation.
        """
        return await self.executor.execute(
            prompt=prompt,
            response_type=response_type,
        )

    async def ask_text(self, prompt: str) -> str:
        """
        Backward-compatible async shortcut for plain text responses.
        """
        return (await self.ask(prompt)).data
