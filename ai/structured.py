from typing import TypeVar

from pydantic import BaseModel

from ai.parser import parse_json_response

T = TypeVar("T", bound=BaseModel)


def build_structured_prompt(
    prompt: str,
    response_type: type[BaseModel],
) -> str:
    """
    Build a provider-independent structured-output prompt.

    This keeps schema prompting logic in one place instead of duplicating it
    across sync, async, image, and future request executors.
    """
    schema_json = response_type.model_json_schema()

    return f"""
{prompt}

Return valid JSON only.
The JSON must match this schema:
{schema_json}
"""


def parse_structured_response(
    raw_response: str,
    response_type: type[T],
) -> T:
    """
    Parse a raw model response into a Pydantic model.
    """
    return parse_json_response(raw_response, response_type)
