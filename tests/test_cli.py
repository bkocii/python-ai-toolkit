from types import SimpleNamespace

import pytest

from ai.cli.main import main
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
