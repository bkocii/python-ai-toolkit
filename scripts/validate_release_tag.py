"""Validate that a release tag exactly matches the package version."""

from __future__ import annotations

import argparse
import re
import tomllib
from collections.abc import Sequence
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
RELEASE_VERSION_PATTERN = re.compile(
    r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:(?:a|b|rc)(?:0|[1-9]\d*)|\.dev(?:0|[1-9]\d*))?"
)


def load_project_version(pyproject_path: Path = DEFAULT_PYPROJECT_PATH) -> str:
    """Read the authoritative package version from pyproject.toml."""
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return pyproject["project"]["version"]


def validate_release_tag(tag: str, version: str) -> None:
    """Raise ValueError unless *tag* is the exact version tag for *version*."""
    if RELEASE_VERSION_PATTERN.fullmatch(version) is None:
        raise ValueError(f"unsupported release version format: {version!r}")

    expected_tag = f"v{version}"
    if tag != expected_tag:
        raise ValueError(
            f"release tag {tag!r} does not match package version; "
            f"expected {expected_tag!r}"
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a release tag against pyproject.toml."
    )
    parser.add_argument("tag", help="Version tag, for example v1.0.0")
    parser.add_argument(
        "--pyproject",
        type=Path,
        default=DEFAULT_PYPROJECT_PATH,
        help="Path to pyproject.toml",
    )
    args = parser.parse_args(argv)

    version = load_project_version(args.pyproject)
    try:
        validate_release_tag(args.tag, version)
    except ValueError as error:
        parser.error(str(error))

    print(f"release tag {args.tag} matches package version {version}: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
