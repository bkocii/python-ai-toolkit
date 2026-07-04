import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def parse_json_response(raw_response: str, response_type: type[T]) -> T:
    """
    Parse raw AI text into a validated Pydantic object.

    Args:
        raw_response:
            Raw text returned by the model.

        response_type:
            Pydantic schema class we expect.

    Returns:
        Validated Pydantic object.

    Raises:
        ValueError:
            If JSON parsing or schema validation fails.
    """
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI response was not valid JSON: {raw_response}") from exc

    try:
        return response_type.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"AI response did not match schema: {raw_response}") from exc
