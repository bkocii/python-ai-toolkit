from ai.prompts import PromptBuilder


def test_prompt_builder_creates_sections():
    prompt = (
        PromptBuilder()
        .add("Role", "You are a test assistant.")
        .add("Task", "Return hello.")
        .build()
    )

    assert "Role:" in prompt
    assert "You are a test assistant." in prompt
    assert "Task:" in prompt
    assert "Return hello." in prompt