import os
from dataclasses import dataclass
from dotenv import load_dotenv
from ai.exceptions import AIConfigurationError

load_dotenv()


@dataclass(frozen=True)
class AIConfig:
    api_key: str
    model: str = "gpt-5.4-mini"
    provider: str = "openai"
    input_cost_per_1m_tokens: str | None = None
    output_cost_per_1m_tokens: str | None = None
    max_retries: int = 1


def get_ai_config() -> AIConfig:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise AIConfigurationError(
            "OPENAI_API_KEY is missing. Add it to your .env file."
        )

    return AIConfig(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
        provider=os.getenv("AI_PROVIDER", "openai"),
        input_cost_per_1m_tokens=os.getenv("AI_INPUT_COST_PER_1M_TOKENS"),
        output_cost_per_1m_tokens=os.getenv("AI_OUTPUT_COST_PER_1M_TOKENS"),
        max_retries=int(os.getenv("AI_MAX_RETRIES", "1")),
    )
