from typing import Generic, TypeVar
from decimal import Decimal
from pydantic import BaseModel

T = TypeVar("T")


class TokenUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

    def add(self, other: "TokenUsage | None") -> "TokenUsage":
        if other is None:
            return self

        return TokenUsage(
            input_tokens=(self.input_tokens or 0) + (other.input_tokens or 0),
            output_tokens=(self.output_tokens or 0) + (other.output_tokens or 0),
            total_tokens=(self.total_tokens or 0) + (other.total_tokens or 0),
        )


class ProviderResponse(BaseModel):
    text: str
    token_usage: TokenUsage | None = None


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
    token_usage: TokenUsage | None = None
    estimated_cost_usd: Decimal | None = None
    request_id: str
