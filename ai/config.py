import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AIConfig:
    """
    Central place for AI configuration.

    We keep configuration here so the rest of the code does not read
    environment variables directly.
    """

    api_key: str
    model: str = "gpt-5.4-mini"


def get_ai_config() -> AIConfig:
    """
    Load AI configuration from environment variables.

    Raises:
        RuntimeError: If OPENAI_API_KEY is missing.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

    return AIConfig(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
    )