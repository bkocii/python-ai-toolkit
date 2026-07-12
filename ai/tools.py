from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """
    Provider-independent definition of a tool the model may request.
    """

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """
    Provider-independent representation of a tool call requested by the model.
    """

    name: str
    arguments: dict[str, Any]
    call_id: str | None = None


class ToolResponse(BaseModel):
    """
    Result of a model response that may contain text and/or tool calls.
    """

    text: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
