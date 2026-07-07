from ai.retry import build_json_repair_prompt


def test_build_json_repair_prompt_contains_original_prompt_and_response():
    prompt = build_json_repair_prompt(
        original_prompt="Return product JSON",
        invalid_response="not json",
    )

    assert "Return product JSON" in prompt
    assert "not json" in prompt
    assert "Return ONLY corrected valid JSON" in prompt