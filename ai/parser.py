import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from ai.exceptions import AIJSONParseError, AISchemaValidationError

T = TypeVar("T", bound=BaseModel)


def parse_json_response(raw_response: str, response_type: type[T]) -> T:
    """
    Parse raw AI text into a validated Pydantic object.
    """
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise AIJSONParseError(
            f"AI response was not valid JSON: {raw_response}"
        ) from exc

    try:
        return response_type.model_validate(data)
    except ValidationError as exc:
        raise AISchemaValidationError(
            f"AI response did not match schema: {raw_response}"
        ) from exc
