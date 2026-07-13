import pytest
from pydantic import BaseModel

from ai.exceptions import AIJSONParseError, AISchemaValidationError
from ai.structured import build_structured_prompt, parse_structured_response


class Answer(BaseModel):
    value: str


def test_build_structured_prompt_includes_original_prompt():
    prompt = build_structured_prompt(
        prompt="Return an answer.",
        response_type=Answer,
    )

    assert "Return an answer." in prompt


def test_build_structured_prompt_includes_json_instruction():
    prompt = build_structured_prompt(
        prompt="Return an answer.",
        response_type=Answer,
    )

    assert "Return valid JSON only." in prompt
    assert "The JSON must match this schema:" in prompt


def test_build_structured_prompt_includes_schema_fields():
    prompt = build_structured_prompt(
        prompt="Return an answer.",
        response_type=Answer,
    )

    assert "value" in prompt


def test_parse_structured_response_returns_pydantic_model():
    result = parse_structured_response(
        raw_response='{"value": "yes"}',
        response_type=Answer,
    )

    assert isinstance(result, Answer)
    assert result.value == "yes"


def test_parse_structured_response_rejects_invalid_json():
    with pytest.raises(AIJSONParseError):
        parse_structured_response(
            raw_response="not json",
            response_type=Answer,
        )


def test_parse_structured_response_rejects_invalid_schema():
    with pytest.raises(AISchemaValidationError):
        parse_structured_response(
            raw_response='{"wrong": "field"}',
            response_type=Answer,
        )
