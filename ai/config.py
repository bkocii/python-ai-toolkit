import os
from dataclasses import dataclass
from dotenv import load_dotenv

from ai.exceptions import AIConfigurationError

load_dotenv()

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-5.4-mini"


@dataclass(frozen=True)
class AIConfig:
    api_key: str
    model: str = DEFAULT_MODEL
    provider: str = DEFAULT_PROVIDER
    input_cost_per_1m_tokens: str | None = None
    output_cost_per_1m_tokens: str | None = None
    max_retries: int = 1


def _normalize_provider(provider: str | None) -> str:
    return (provider or DEFAULT_PROVIDER).strip().lower()


def _provider_env_name(provider: str, setting: str) -> str:
    return f"{provider.upper()}_{setting}"


def _get_api_key(provider: str) -> str:
    provider_key_name = _provider_env_name(provider, "API_KEY")
    api_key = os.getenv(provider_key_name) or os.getenv("AI_API_KEY")

    if not api_key:
        raise AIConfigurationError(
            f"Missing API key for provider '{provider}'. "
            f"Set {provider_key_name}=your_api_key or AI_API_KEY=your_api_key in your .env file."
        )

    return api_key


def _get_model(provider: str) -> str:
    provider_model_name = _provider_env_name(provider, "MODEL")
    return os.getenv(provider_model_name) or os.getenv("AI_MODEL", DEFAULT_MODEL)


def _get_max_retries() -> int:
    raw_value = os.getenv("AI_MAX_RETRIES", "1")

    try:
        max_retries = int(raw_value)
    except ValueError as exc:
        raise AIConfigurationError(
            f"Invalid AI_MAX_RETRIES value '{raw_value}'. "
            "Set AI_MAX_RETRIES to a whole number, for example AI_MAX_RETRIES=1."
        ) from exc

    if max_retries < 0:
        raise AIConfigurationError(
            f"Invalid AI_MAX_RETRIES value '{max_retries}'. "
            "Set AI_MAX_RETRIES to zero or greater, for example AI_MAX_RETRIES=1."
        )

    return max_retries


def get_ai_config() -> AIConfig:
    from ai.config_validator import ConfigValidator

    provider = _normalize_provider(os.getenv("AI_PROVIDER"))

    config = AIConfig(
        api_key=_get_api_key(provider),
        model=_get_model(provider),
        provider=provider,
        input_cost_per_1m_tokens=os.getenv("AI_INPUT_COST_PER_1M_TOKENS"),
        output_cost_per_1m_tokens=os.getenv("AI_OUTPUT_COST_PER_1M_TOKENS"),
        max_retries=_get_max_retries(),
    )

    ConfigValidator.validate(config)

    return config
