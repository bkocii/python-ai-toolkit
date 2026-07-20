import argparse
import sys
from collections.abc import Sequence
from ai.cli.config_commands import (
    run_config_show_command,
    run_config_validate_command,
)
from ai.client import AIClient
from ai.exceptions import AIError


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="ai-toolkit",
        description="Use the Python AI Toolkit from the command line.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    ask_parser = subparsers.add_parser(
        "ask",
        help="Send a plain-text prompt to the configured AI provider.",
    )
    ask_parser.add_argument(
        "prompt",
        nargs="+",
        help="Prompt to send to the AI provider.",
    )
    ask_parser.set_defaults(handler=run_ask_command)

    config_parser = subparsers.add_parser(
        "config",
        help="Inspect and validate toolkit configuration.",
    )

    config_subparsers = config_parser.add_subparsers(
        dest="config_command",
        required=True,
    )

    config_show_parser = config_subparsers.add_parser(
        "show",
        help="Display the resolved toolkit configuration.",
    )
    config_show_parser.set_defaults(
        handler=run_config_show_command,
    )

    config_validate_parser = config_subparsers.add_parser(
        "validate",
        help=(
            "Validate the structure of the resolved toolkit configuration "
            "without contacting the provider."
        ),
    )
    config_validate_parser.set_defaults(
        handler=run_config_validate_command,
    )

    return parser


def run_ask_command(args: argparse.Namespace) -> int:
    """
    Execute the ask command.
    """
    prompt = " ".join(args.prompt)

    client = AIClient()
    result = client.ask(prompt)

    print(result.data)

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run the command-line interface.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.handler(args)
    except AIError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
