from typing import TypeVar, overload
from ai.logger import get_ai_logger
from pydantic import BaseModel

from ai.async_executor import AsyncRequestExecutor
from ai.config import get_ai_config, AIConfig
from ai.providers.factory import ProviderFactory
from ai.schemas import AIResult

T = TypeVar("T", bound=BaseModel)


class AsyncAIClient:
    """
    Async public client used by applications.

    AsyncAIClient mirrors AIClient, but uses AsyncRequestExecutor
    and provider async methods.
    """

    def __init__(self, config: AIConfig | None = None):
        resolved_config = config if config is not None else get_ai_config()
        self.model = resolved_config.model

        self.provider = ProviderFactory.create(resolved_config)

        logger = get_ai_logger(
            level=resolved_config.log_level,
            file_path=resolved_config.log_file_path,
            file_logging_enabled=resolved_config.file_logging_enabled,
        )

        self.executor = AsyncRequestExecutor(
            provider=self.provider,
            model=self.model,
            max_retries=resolved_config.max_retries,
            logger=logger,
            input_cost_per_1m_tokens=(resolved_config.input_cost_per_1m_tokens),
            output_cost_per_1m_tokens=(resolved_config.output_cost_per_1m_tokens),
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
