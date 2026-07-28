from typing import Annotated

from fastapi import Depends

from ai.async_client import AsyncAIClient
from ai.client import AIClient


def get_ai_client() -> AIClient:
    """
    Create a synchronous AI client for a FastAPI request.
    """
    return AIClient()


def get_async_ai_client() -> AsyncAIClient:
    """
    Create an asynchronous AI client for a FastAPI request.
    """
    return AsyncAIClient()


AIClientDependency = Annotated[
    AIClient,
    Depends(get_ai_client),
]

AsyncAIClientDependency = Annotated[
    AsyncAIClient,
    Depends(get_async_ai_client),
]
