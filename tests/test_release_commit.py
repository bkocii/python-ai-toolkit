import re
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DATE = "2026-07-30"
EXPECTED_PROJECT_URLS = {
    "Repository": "https://github.com/bkocii/python-ai-toolkit",
    "Documentation": "https://github.com/bkocii/python-ai-toolkit/tree/main/docs",
    "Issues": "https://github.com/bkocii/python-ai-toolkit/issues",
    "Changelog": ("https://github.com/bkocii/python-ai-toolkit/blob/main/CHANGELOG.md"),
}


def read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_release_changelog_is_dated_once():
    changelog = read("CHANGELOG.md")

    assert changelog.count(f"## [1.0.0] - {RELEASE_DATE}") == 1
    assert "## [1.0.0] - Unreleased" not in changelog
    assert "Version 1.0.0 is the first stable API release." in changelog


def test_release_metadata_uses_canonical_public_urls():
    project = tomllib.loads(read("pyproject.toml"))["project"]

    assert project["version"] == "1.0.0"
    assert project["urls"] == EXPECTED_PROJECT_URLS


def test_readme_is_pypi_ready():
    readme = read("README.md")

    assert "python -m pip install python-ai-toolkit" in readme
    assert 'python -m pip install "python-ai-toolkit[django]"' in readme
    assert 'python -m pip install "python-ai-toolkit[fastapi]"' in readme
    assert "not published on PyPI yet" not in readme
    assert "publication is still pending" not in readme


def test_readme_has_no_repository_relative_destinations():
    relative_destinations = re.findall(
        r"\]\((?!#|https?://|mailto:)([^)]+)\)",
        read("README.md"),
    )

    assert relative_destinations == []


def test_public_package_documents_use_stable_release_wording():
    documents = {
        "README.md": "first stable release",
        "docs/installation.md": "distributed through PyPI",
        "docs/compatibility.md": "stable package metadata is `1.0.0`",
        "docs/api_reference.md": "first stable release",
    }

    for relative_path, stable_text in documents.items():
        text = read(relative_path)
        assert stable_text in text, relative_path
        assert "has not yet been tagged or published" not in text, relative_path


def test_release_state_records_completed_tag_publication_and_release_notes():
    project_state = read("docs/development/project_state.md")
    roadmap = read("docs/development/roadmap.md")
    handoff = read("docs/development/session_handoff.md")

    assert "* [x] V1-007 Create release commit" in roadmap
    assert "* [x] V1-008 Create Git tag `v1.0.0`" in roadmap
    assert "* [x] V1-012 Publish release notes" in roadmap
    assert "`PROD-007 — Version 1.0.0 Release` is complete." in project_state
    assert "**Next task:** Post-release roadmap review" in handoff
    assert "https://pypi.org/project/python-ai-toolkit/1.0.0/" in project_state
    assert (
        "https://github.com/bkocii/python-ai-toolkit/releases/tag/v1.0.0"
        in project_state
    )
