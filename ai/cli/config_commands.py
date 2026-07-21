import argparse

from ai.config import AIConfig, get_ai_config


def mask_api_key(api_key: str) -> str:
    """
    Mask an API key while preserving the final four characters.
    """
    if len(api_key) <= 4:
        return "********"

    return f"********{api_key[-4:]}"


def format_optional_value(value: object | None) -> str:
    """
    Format an optional configuration value for terminal output.
    """
    if value is None:
        return "not configured"

    formatted_value = str(value).strip()

    return formatted_value or "not configured"


def format_ai_config(config: AIConfig) -> str:
    """
    Format AI configuration without exposing complete secrets.
    """
    embedding_dimensions = (
        str(config.embedding_dimensions)
        if config.embedding_dimensions is not None
        else "default"
    )

    lines = [
        f"Provider: {config.provider}",
        f"API key: {mask_api_key(config.api_key)}",
        f"Model: {config.model}",
        f"Embedding model: {config.embedding_model}",
        f"Embedding dimensions: {embedding_dimensions}",
        f"Maximum retries: {config.max_retries}",
        f"Log level: {config.log_level}",
        f"Log file path: {format_optional_value(config.log_file_path)}",
        ("File logging enabled: " f"{'yes' if config.file_logging_enabled else 'no'}"),
        (
            "Input cost per 1M tokens: "
            f"{format_optional_value(config.input_cost_per_1m_tokens)}"
        ),
        (
            "Output cost per 1M tokens: "
            f"{format_optional_value(config.output_cost_per_1m_tokens)}"
        ),
    ]

    return "\n".join(lines)


def run_config_show_command(_args: argparse.Namespace) -> int:
    """
    Display the resolved toolkit configuration.
    """
    config = get_ai_config()

    print(format_ai_config(config))

    return 0


def run_config_validate_command(_args: argparse.Namespace) -> int:
    """
    Validate the structure of the resolved toolkit configuration.
    """
    get_ai_config()

    print(
        "Configuration is structurally valid. "
        "Provider credentials were not verified."
    )

    return 0
