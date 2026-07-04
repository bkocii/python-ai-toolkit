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
    with pytest.raises(AIJSONParseError):
        parse_json_response(
            "not json",
            SampleResponse,
        )


def test_parse_json_response_invalid_schema():
    with pytest.raises(AISchemaValidationError):
        parse_json_response(
            '{"name": "Genius Green"}',
            SampleResponse,
        )
