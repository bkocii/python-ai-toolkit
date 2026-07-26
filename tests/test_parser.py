import pytest
from pydantic import BaseModel

from ai.exceptions import AIJSONParseError, AISchemaValidationError
from ai.parser import parse_json_response


class SampleResponse(BaseModel):
    name: str
    price: float


def test_parse_json_response_valid():
    result = parse_json_response(
        '{"name": "Genius Green", "price": 2.5}',
        SampleResponse,
    )

    assert result.name == "Genius Green"
    assert result.price == 2.5


def test_parse_json_response_invalid_json():
    sensitive_response = "not json; password=do-not-log"

    with pytest.raises(AIJSONParseError) as exc_info:
        parse_json_response(
            sensitive_response,
            SampleResponse,
        )

    assert str(exc_info.value) == "AI response was not valid JSON."
    assert sensitive_response not in str(exc_info.value)


def test_parse_json_response_invalid_schema():
    sensitive_response = '{"password": "do-not-log"}'

    with pytest.raises(AISchemaValidationError) as exc_info:
        parse_json_response(
            sensitive_response,
            SampleResponse,
        )

    assert str(exc_info.value) == ("AI response did not match the requested schema.")
    assert sensitive_response not in str(exc_info.value)
