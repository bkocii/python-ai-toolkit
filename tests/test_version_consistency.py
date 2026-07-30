import tomllib
from pathlib import Path

from scripts.verify_core_installation import EXPECTED_VERSION as CORE_VERSION
from scripts.verify_framework_extra_installation import (
    EXPECTED_VERSION as FRAMEWORK_VERSION,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION = "1.0.0"
CURRENT_TAG = f"v{CURRENT_VERSION}"


def read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def project_metadata() -> dict:
    return tomllib.loads(read("pyproject.toml"))["project"]


def test_authoritative_version_and_install_verifiers_match():
    assert project_metadata()["version"] == CURRENT_VERSION
    assert CORE_VERSION == CURRENT_VERSION
    assert FRAMEWORK_VERSION == CURRENT_VERSION


def test_package_metadata_describes_a_stable_release():
    classifiers = project_metadata()["classifiers"]

    assert "Development Status :: 5 - Production/Stable" in classifiers
    assert "Development Status :: 4 - Beta" not in classifiers


def test_current_user_facing_statuses_use_version_1():
    documents = [
        "README.md",
        "docs/api_reference.md",
        "docs/compatibility.md",
        "docs/installation.md",
        "docs/development/performance_profiling.md",
    ]

    for relative_path in documents:
        text = read(relative_path)
        assert CURRENT_VERSION in text, relative_path
        assert "0.7.0-dev" not in text, relative_path


def test_authoritative_status_headers_use_version_1():
    status_headers = {
        "docs/development/project_state.md": 20,
        "docs/development/roadmap.md": 22,
        "docs/development/session_handoff.md": 12,
    }

    for relative_path, line_count in status_headers.items():
        header = "\n".join(read(relative_path).splitlines()[:line_count])
        assert CURRENT_VERSION in header, relative_path
        assert "0.7.0-dev" not in header, relative_path


def test_release_rehearsal_and_installation_commands_match_version_1():
    release_guide = read("docs/releasing.md")
    installation_guide = read("docs/installation.md")

    assert CURRENT_TAG in release_guide
    assert f"python-package-distributions-{CURRENT_TAG}" in release_guide
    assert f"pyproject.toml version {CURRENT_VERSION}" in installation_guide
    assert f"required tag          {CURRENT_TAG}" in installation_guide
    assert f"python_ai_toolkit-{CURRENT_VERSION}-py3-none-any.whl" in installation_guide
    assert f"python_ai_toolkit-{CURRENT_VERSION}.tar.gz" in installation_guide


def test_changelog_uses_the_version_1_release_date():
    changelog = read("CHANGELOG.md")
    version_heading = f"## [{CURRENT_VERSION}] - 2026-07-30"

    assert changelog.count(version_heading) == 1
    assert f"Version {CURRENT_VERSION} is the first stable API release." in changelog
    assert f"## [{CURRENT_VERSION}] - Unreleased" not in changelog


def test_historical_development_version_evidence_is_preserved():
    changelog = read("CHANGELOG.md")
    roadmap = read("docs/development/roadmap.md")
    handoff = read("docs/development/session_handoff.md")

    assert "The former `0.7.0.dev0` development line" in changelog
    assert "created `python_ai_toolkit-0.7.0.dev0.tar.gz`" in roadmap
    assert "current package tag v0.7.0.dev0 passed exact version validation" in roadmap
    assert "built `python_ai_toolkit-0.7.0.dev0.tar.gz`" in handoff
