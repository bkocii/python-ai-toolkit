from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_GUIDE_PATH = PROJECT_ROOT / "docs" / "releasing.md"
README_PATH = PROJECT_ROOT / "README.md"
INSTALLATION_GUIDE_PATH = PROJECT_ROOT / "docs" / "installation.md"
COMPATIBILITY_GUIDE_PATH = PROJECT_ROOT / "docs" / "compatibility.md"
API_REFERENCE_PATH = PROJECT_ROOT / "docs" / "api_reference.md"
CHANGELOG_PATH = PROJECT_ROOT / "CHANGELOG.md"


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
        "## Phase 5 — Verify installation from PyPI (`V1-010`)",
        "## Phase 6 — Run post-release smoke tests (`V1-011`)",
        "## Phase 7 — Publish release notes (`V1-012`)",
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
    assert "python-package-distributions-v1.0.0" in text
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

    assert (
        "[Release procedure]"
        "(https://github.com/bkocii/python-ai-toolkit/blob/main/docs/releasing.md)"
        in readme
    )
    assert "[release procedure](releasing.md)" in installation


def test_version_1_release_tasks_are_explicit_and_ordered():
    complete_text = guide_text()
    text = complete_text[
        complete_text.index("## Version 1.0 execution map") : complete_text.index(
            "## Phase 1 — Prepare the release"
        )
    ]
    tasks = [
        "`V1-006`",
        "`V1-007`",
        "`V1-008`",
        "`V1-009`",
        "`V1-010`",
        "`V1-011`",
        "`V1-012`",
    ]

    positions = [text.index(task) for task in tasks]

    assert positions == sorted(positions)
    assert "No release commit, tag, approval, or publication" in text
    assert "No Git tag" in text
    assert "do not approve `pypi`" in text
    assert "required reviewer on the `pypi` environment" in text


def test_release_commit_gate_covers_public_package_documentation():
    text = guide_text()

    assert "actual release date" in text
    assert "`1.0.0 — Unreleased` changelog heading" in text
    assert 'public "not published yet" wording' in text
    assert "canonical repository, documentation, issue-tracker, and changelog" in text
    assert "README link in the built long description resolves from PyPI" in text
    assert "Do not make those release-date or published-status changes" in text


def test_post_release_smoke_gate_uses_installed_public_behavior():
    text = guide_text()

    for expected_command in [
        '"$projectRoot\\scripts\\verify_core_installation.py"',
        '"python-ai-toolkit[django]==$version"',
        '"python-ai-toolkit[fastapi]==$version"',
        '"$projectRoot\\scripts\\verify_framework_extra_installation.py" django',
        '"$projectRoot\\scripts\\verify_framework_extra_installation.py" fastapi',
    ]:
        assert expected_command in text

    assert "plain and structured offline client requests pass" in text
    assert "unselected framework absent" in text
    assert "A live OpenAI request is optional" in text
    assert "never place a real key" in text


def test_release_notes_use_the_existing_verified_tag():
    text = guide_text()

    assert "Choose the existing `v1.0.0` tag." in text
    assert "Do not create another tag." in text
    assert "Set as a pre-release" in text
    assert "Do not upload a second copy of the wheel or source distribution" in text
    assert "GitHub Release is visible" in text
    assert "Only then is the Version 1.0 release milestone complete." in text


def test_public_documents_are_ready_for_the_stable_release():
    readme = README_PATH.read_text(encoding="utf-8")
    installation = INSTALLATION_GUIDE_PATH.read_text(encoding="utf-8")
    compatibility = COMPATIBILITY_GUIDE_PATH.read_text(encoding="utf-8")
    api_reference = API_REFERENCE_PATH.read_text(encoding="utf-8")
    changelog = CHANGELOG_PATH.read_text(encoding="utf-8")

    assert "Version `1.0.0` is the first stable release" in readme
    assert "https://pypi.org/project/python-ai-toolkit/1.0.0/" in readme
    assert "https://github.com/bkocii/python-ai-toolkit/releases/tag/v1.0.0" in readme
    assert "Sprint 9 — Production Readiness is complete." in readme
    assert "python -m pip install python-ai-toolkit" in readme
    assert "distributed through PyPI" in installation
    assert "stable package metadata is `1.0.0`" in compatibility
    assert "Version `1.0.0` is the first stable release" in api_reference
    assert "## [1.0.0] - 2026-07-30" in changelog

    public_documents = [readme, installation, compatibility, api_reference, changelog]
    for text in public_documents:
        assert "has not yet been tagged or published" not in text
        assert "not published on PyPI yet" not in text
