def build_json_repair_prompt(
    original_prompt: str,
    invalid_response: str,
) -> str:
    """
    Build a prompt asking the model to repair invalid JSON.

    The model should return only corrected JSON matching the original schema.
    """
    return f"""
The previous response did not match the required JSON schema.

Original prompt:
{original_prompt}

Invalid response:
{invalid_response}

Return ONLY corrected valid JSON matching the schema.
"""
