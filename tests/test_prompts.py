import pytest

from ai.prompts import PromptTemplate


def test_prompt_template_renders_values():
    template = PromptTemplate(
        "Summarize this article in {language}: {article}"
    )

    result = template.render(
        language="English",
        article="Python is popular.",
    )

    assert result == "Summarize this article in English: Python is popular."


def test_prompt_template_rejects_empty_template():
    with pytest.raises(ValueError, match="Prompt template cannot be empty"):
        PromptTemplate("")


def test_prompt_template_rejects_whitespace_only_template():
    with pytest.raises(ValueError, match="Prompt template cannot be empty"):
        PromptTemplate("   ")


def test_prompt_template_raises_error_for_missing_value():
    template = PromptTemplate("Hello {name}")

    with pytest.raises(
        ValueError,
        match="Missing value for prompt template variable: name",
    ):
        template.render()