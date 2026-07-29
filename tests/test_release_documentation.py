from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_GUIDE_PATH = PROJECT_ROOT / "docs" / "releasing.md"
README_PATH = PROJECT_ROOT / "README.md"
INSTALLATION_GUIDE_PATH = PROJECT_ROOT / "docs" / "installation.md"


def guide_text() -> str:
    return RELEASE_GUIDE_PATH.read_text(encoding="utf-8")


def normalized_guide_text() -> str:
    return " ".join(guide_text().split())


def test_release_guide_covers_complete_release_lifecycle():
    text = guide_text()
    headings = [
        "## Non-production workflow rehearsal",
        "## One-time account setup",
        "## Phase 1 — Prepare the release",
        "## Phase 2 — Approve the exact commit",
        "## Phase 3 — Create and push the tag",
        "## Phase 4 — Monitor and approve publication",
        "## Phase 5 — Verify the published release",
        "## Failure and recovery",
        "## Final checklist",
    ]

    positions = [text.index(heading) for heading in headings]

    assert positions == sorted(positions)


def test_release_guide_documents_safe_manual_rehearsal():
    text = guide_text()
    normalized_text = normalized_guide_text()

    for expected_result in [
        "**Validate release identity** — passed",
        "**Tests (Python 3.11)** — passed",
        "**Tests (Python 3.12)** — passed",
        "**Tests (Python 3.13)** — passed",
        "**Tests (Python 3.14)** — passed",
        "**Build release distributions** — passed",
        "**Publish distributions to PyPI** — skipped",
    ]:
        assert expected_result in text

    assert "**Run workflow**" in text
    assert "python-package-distributions-v0.7.0.dev0" in text
    assert "It does not create or push a Git tag." in normalized_text
    assert "do not enter the `pypi` environment" in normalized_text
    assert "request an OIDC identity token" in normalized_text
    assert "Do not approve a deployment" in text


def test_release_guide_records_rehearsal_evidence_and_limits():
    text = normalized_guide_text()

    assert "exactly one wheel and one source distribution" in text
    assert "strict Twine validation and the offline archive" in text
    assert "creates no tag, PyPI project, package version, GitHub Release" in text
    assert "temporary workflow artifact can expire normally or be deleted" in text
    assert "does not prove the PyPI trusted-publisher identity or upload" in text
    assert "first roadmap-authorized release" in text


def test_release_guide_preserves_exact_trusted_publisher_identity():
    text = guide_text()

    for expected_value in [
        "| PyPI project | `python-ai-toolkit` |",
        "| Owner | `bkocii` |",
        "| Repository | `python-ai-toolkit` |",
        "| Workflow | `release.yml` |",
        "| Environment | `pypi` |",
    ]:
        assert expected_value in text

    assert "Do not add a PyPI password, username, or API-token secret." in text


def test_release_guide_uses_exact_tag_and_quality_commands():
    text = guide_text()
    commands = [
        '$tag = "v$version"',
        "python scripts\\validate_release_tag.py $tag",
        "python -m pip check",
        "python -m black --check .",
        "python -m ruff check .",
        "python -m pytest -q",
        "python -m build",
        "python -m twine check --strict dist\\*",
        "python scripts\\validate_distributions.py",
        "git tag -a $tag",
        "git push origin $tag",
    ]

    positions = [text.index(command) for command in commands]

    assert positions == sorted(positions)
    assert "git push --tags" in text
    assert "Do not use `git push --tags`" in text


def test_release_guide_requires_exact_commit_and_protected_approval():
    text = guide_text()

    assert "git pull --ff-only origin main" in text
    assert "git status --short` must print nothing" in text
    assert "git rev-list -n 1 $tag" in text
    assert "git rev-parse HEAD" in text
    assert "**Review deployments**" in text
    assert "approve only after the checks above" in text


def test_release_guide_documents_immutable_recovery_boundary():
    text = guide_text()

    assert "treat that tag as immutable" in text
    assert "commit with a new version and tag" in text
    assert "Do not blindly rerun" in text
    assert "Yank the defective release" in text
    assert "Treat deletion as permanent" in text
    assert "Never delete a release as an attempt to repair" in text


def test_release_guide_is_linked_from_primary_maintainer_docs():
    readme = README_PATH.read_text(encoding="utf-8")
    installation = INSTALLATION_GUIDE_PATH.read_text(encoding="utf-8")

    assert "[Release procedure](docs/releasing.md)" in readme
    assert "[release procedure](releasing.md)" in installation
