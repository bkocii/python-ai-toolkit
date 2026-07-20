import argparse
import sys
from collections.abc import Sequence

from ai.client import AIClient
from ai.exceptions import AIError


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="ai-toolkit",
        description="Run AI requests from the command line.",
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
