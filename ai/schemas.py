from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class AIResult(BaseModel, Generic[T]):
    """
    Standard response object returned by AIClient.

    data:
        The actual response. Can be plain text or a validated Pydantic object.

    model:
        The model used for the request.

    raw_response:
        Original text returned by the model.
    """

    data: T
    model: str
    raw_response: str
    original_raw_response: str | None = None
    duration_ms: float | None = None
    retries_used: int = 0
