import re
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = PROJECT_ROOT / "CHANGELOG.md"
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


def changelog_text() -> str:
    return CHANGELOG_PATH.read_text(encoding="utf-8")


def version_1_section() -> str:
    text = changelog_text()
    return text.split("## [1.0.0] - Unreleased", 1)[1].split("\n---\n", 1)[0]


def normalized_version_1_section() -> str:
    return " ".join(version_1_section().split())


def test_changelog_has_one_release_ready_version_1_section():
    text = changelog_text()

    assert text.count("## [1.0.0] - Unreleased") == 1
    assert "## [0.7.0]" not in text
    assert "### Fixed" not in text.split("## [1.0.0] - Unreleased", 1)[0]

    headings = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", text, re.MULTILINE)
    assert headings == ["1.0.0", "0.6.0", "0.5.0", "0.4.0", "0.3.0", "0.2.0", "0.1.0"]


def test_version_1_section_explains_the_development_line():
    section = version_1_section()
    project = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))["project"]

    assert f"`{project['version']}`" in section
    assert "has not yet been tagged or published" in section
    assert "The former `0.7.0.dev0` development line" in section
    assert "never a separate stable release" in section


def test_version_1_section_uses_complete_user_facing_categories():
    section = version_1_section()
    headings = [
        "### Added",
        "### Changed",
        "### Fixed",
        "### Security",
        "### Compatibility and upgrade notes",
        "### Maintainer release readiness",
    ]

    positions = [section.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_version_1_section_records_the_frozen_contract_and_boundaries():
    section = normalized_version_1_section()

    for contract in [
        "71 symbols",
        "25 explicit module paths",
        "top-level `ai` package",
        "Streaming returns `Iterator[str]`",
        "tool calling returns `ToolResponse`",
        "embedding methods return `EmbeddingResponse`",
        "Tool calls are returned to the application",
        "`AsyncAIClient` supports plain and structured requests",
        "The built-in provider is OpenAI",
    ]:
        assert contract in section


def test_version_1_section_records_release_blocker_fixes():
    section = normalized_version_1_section()

    for fixed_behavior in [
        "raises `AIConfigurationError`",
        "JSON value other than an object",
        "Invalid, duplicate, or missing embedding indices",
        "include the current user message exactly once",
        "validate every requested agent name",
        "empty `MultiAgentResponse` is unsuccessful",
    ]:
        assert fixed_behavior in section


def test_historical_release_sections_remain_in_order():
    text = changelog_text()

    expected_features = {
        "0.6.0": "Embedding support",
        "0.5.0": "Streaming text responses",
        "0.4.0": "`AIClient.request()`",
        "0.3.0": "Provider abstraction layer",
        "0.2.0": "Core `AIClient`",
        "0.1.0": "Repository initialization",
    }

    for version, feature in expected_features.items():
        section = text.split(f"## [{version}]", 1)[1]
        assert feature in section
