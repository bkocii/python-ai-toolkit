from types import SimpleNamespace

import pytest

from ai.cli.config_commands import mask_api_key
from ai.cli.main import main
from ai.config import AIConfig
from ai.exceptions import AIConfigurationError


def test_ask_command_prints_response(monkeypatch, capsys):
    captured_prompts: list[str] = []

    class FakeAIClient:
        def ask(self, prompt: str):
            captured_prompts.append(prompt)
            return SimpleNamespace(data="Dependency injection explained.")

    monkeypatch.setattr(
        "ai.cli.main.AIClient",
        FakeAIClient,
    )

    exit_code = main(
        [
            "ask",
            "Explain",
            "dependency",
            "injection",
        ]
    )

    output = capsys.readouterr()

    assert exit_code == 0
    assert output.out == "Dependency injection explained.\n"
    assert output.err == ""
    assert captured_prompts == [
        "Explain dependency injection",
    ]


def test_ask_command_handles_toolkit_error(monkeypatch, capsys):
    class FailingAIClient:
        def __init__(self):
            raise AIConfigurationError("Missing API key.")

    monkeypatch.setattr(
        "ai.cli.main.AIClient",
        FailingAIClient,
    )

    exit_code = main(
        [
            "ask",
            "Hello",
        ]
    )

    output = capsys.readouterr()

    assert exit_code == 1
    assert output.out == ""
    assert output.err == "Error: Missing API key.\n"


def test_cli_requires_command():
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 2


def test_ask_command_requires_prompt():
    with pytest.raises(SystemExit) as exc_info:
        main(["ask"])

    assert exc_info.value.code == 2


def test_mask_api_key_preserves_only_last_four_characters():
    assert mask_api_key("secret-api-key-1234") == "********1234"


def test_mask_api_key_hides_short_keys_completely():
    assert mask_api_key("key") == "********"


def test_config_show_prints_masked_configuration(monkeypatch, capsys):
    config = AIConfig(
        provider="openai",
        api_key="secret-api-key-1234",
        model="test-model",
        embedding_model="test-embedding-model",
        embedding_dimensions=512,
        input_cost_per_1m_tokens="1.25",
        output_cost_per_1m_tokens=None,
        max_retries=3,
        log_level="WARNING",
        log_file_path="custom/toolkit.log",
        file_logging_enabled=False,
    )

    monkeypatch.setattr(
        "ai.cli.config_commands.get_ai_config",
        lambda: config,
    )

    exit_code = main(
        [
            "config",
            "show",
        ]
    )

    output = capsys.readouterr()

    assert exit_code == 0
    assert output.err == ""

    assert "Provider: openai" in output.out
    assert "API key: ********1234" in output.out
    assert "secret-api-key-1234" not in output.out
    assert "Model: test-model" in output.out
    assert "Embedding model: test-embedding-model" in output.out
    assert "Embedding dimensions: 512" in output.out
    assert "Maximum retries: 3" in output.out
    assert "Input cost per 1M tokens: 1.25" in output.out
    assert "Output cost per 1M tokens: not configured" in output.out
    assert "Log level: WARNING" in output.out
    assert "Log file path: custom/toolkit.log" in output.out
    assert "File logging enabled: no" in output.out


def test_config_show_formats_default_optional_values(monkeypatch, capsys):
    config = AIConfig(
        provider="openai",
        api_key="test-key",
        model="test-model",
        embedding_model="test-embedding-model",
    )

    monkeypatch.setattr(
        "ai.cli.config_commands.get_ai_config",
        lambda: config,
    )

    exit_code = main(["config", "show"])

    output = capsys.readouterr()

    assert exit_code == 0
    assert "Embedding dimensions: default" in output.out
    assert "Input cost per 1M tokens: not configured" in output.out
    assert "Output cost per 1M tokens: not configured" in output.out
    assert "Log level: INFO" in output.out
    assert "Log file path: logs/ai_toolkit.log" in output.out
    assert "File logging enabled: yes" in output.out


def test_config_validate_prints_success(monkeypatch, capsys):
    config = AIConfig(
        provider="openai",
        api_key="test-key",
        model="test-model",
    )

    monkeypatch.setattr(
        "ai.cli.config_commands.get_ai_config",
        lambda: config,
    )

    exit_code = main(
        [
            "config",
            "validate",
        ]
    )

    output = capsys.readouterr()

    assert exit_code == 0
    assert output.out == (
        "Configuration is structurally valid. "
        "Provider credentials were not verified.\n"
    )
    assert output.err == ""


def test_config_validate_handles_configuration_error(monkeypatch, capsys):
    def raise_configuration_error():
        raise AIConfigurationError("Missing API key.")

    monkeypatch.setattr(
        "ai.cli.config_commands.get_ai_config",
        raise_configuration_error,
    )

    exit_code = main(
        [
            "config",
            "validate",
        ]
    )

    output = capsys.readouterr()

    assert exit_code == 1
    assert output.out == ""
    assert output.err == "Error: Missing API key.\n"


def test_config_command_requires_subcommand():
    with pytest.raises(SystemExit) as exc_info:
        main(["config"])

    assert exc_info.value.code == 2
