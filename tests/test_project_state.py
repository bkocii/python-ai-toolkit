from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def section(text: str, heading: str, next_heading: str) -> str:
    return text.split(heading, 1)[1].split(next_heading, 1)[0]


def test_project_state_header_identifies_the_completed_release_stage():
    text = read("docs/development/project_state.md")
    header = section(text, "# Project State", "## Implemented Capabilities")

    assert "1.0.0" in header
    assert "Sprint 9 — Production Readiness is complete." in header
    assert "* PROD-007 Version 1.0.0 Release" in header
    assert "* V1-012 Publish release notes" in header
    assert "Post-release roadmap review" in header
    assert "No implementation task is active." in header
    assert "cb43e4983fc4bf40b9b4c9fa4125ef68748f8b4c" in header


def test_project_state_records_all_completed_release_tasks():
    text = read("docs/development/project_state.md")
    progress = section(
        text,
        "## Current Milestone Progress",
        "## PyPI Package Status",
    )

    for task_number in range(1, 8):
        assert f"V1-{task_number:03d}" in progress

    for task_number in range(8, 13):
        assert f"V1-{task_number:03d}" in progress

    assert "* V1-005 Update project state" in progress
    assert "* V1-006 Complete release documentation" in progress
    assert "* V1-007 Create release commit" in progress
    assert "* V1-008 Create Git tag `v1.0.0`" in progress
    assert "* V1-012 Publish release notes" in progress
    assert "Remaining Version 1 release tasks" not in progress
    assert "Completed" in progress


def test_current_package_status_uses_version_1_without_rewriting_history():
    text = read("docs/development/project_state.md")
    package_status = section(
        text,
        "## PyPI Package Status",
        "## Version 1 Release Documentation Status",
    )

    assert "stable release source as `1.0.0`" in package_status
    assert "stable status" in package_status
    assert "python_ai_toolkit-1.0.0.tar.gz" in package_status
    assert "python_ai_toolkit-1.0.0-py3-none-any.whl" in package_status
    assert "report version `1.0.0`" in package_status
    assert "The earlier `0.7.0.dev0` build" in package_status
    assert "historical" in package_status
    assert "development evidence" in package_status


def test_project_state_records_completed_release_documentation():
    text = read("docs/development/project_state.md")
    release_documentation = section(
        text,
        "## Version 1 Release Documentation Status",
        "## Continuous Integration Status",
    )

    assert "`V1-006 — Complete Release Documentation` is complete." in (
        release_documentation
    )
    assert "13 focused release-documentation regressions passed" in (
        release_documentation
    )
    assert "466 normal tests passed" in release_documentation
    assert "changelog was still `Unreleased`" in release_documentation
    assert "`V1-007` through `V1-012`" in release_documentation
    assert "created no release date, tag, deployment approval" in release_documentation


def test_project_state_records_the_release_commit_and_tag_boundary():
    text = read("docs/development/project_state.md")
    release_commit = section(
        text,
        "## Version 1 Release Commit Status",
        "## Continuous Integration Status",
    )

    assert "`V1-007 — Create Release Commit` is complete." in release_commit
    assert "dates the Version 1.0 changelog `2026-07-30`" in release_commit
    assert "canonical project URLs" in release_commit
    assert "no\nrepository-relative README destinations" in release_commit
    assert "created no `v1.0.0` tag" in release_commit


def test_project_state_reports_the_resolved_quality_status():
    text = read("docs/development/project_state.md")
    profiling_status = section(
        text,
        "## Performance Profiling Status",
        "## Next Milestone Task",
    )

    assert "Current\nquality gates are clean." in profiling_status
    assert "resolved by `RELEASE-003`" in profiling_status
    assert "remain open before the Sprint 9 full-quality exit" not in profiling_status


def test_roadmap_closes_the_complete_version_1_release_sequence():
    text = read("docs/development/roadmap.md")
    release = section(
        text,
        "## PROD-007 — Version 1.0.0 Release",
        "# Future Backlog",
    )

    assert "* [x] V1-005 Update project state" in release
    assert "* [x] V1-006 Complete release documentation" in release
    assert "* [x] V1-007 Create release commit" in release
    assert "* [x] V1-008 Create Git tag `v1.0.0`" in release
    assert "* [x] V1-009 Build and publish distributions" in release
    assert "* [x] V1-010 Verify installation from PyPI" in release
    assert "* [x] V1-011 Run post-release smoke tests" in release
    assert "* [x] V1-012 Publish release notes" in release
    assert "#### V1-006 — Complete Release Documentation" in release
    assert "Status: Completed" in section(
        release,
        "#### V1-006 — Complete Release Documentation",
        "### Public API Freeze",
    )
    assert "V1-007 — Create release commit" in release
    assert "https://github.com/bkocii/python-ai-toolkit/releases/tag/v1.0.0" in release


def test_handoff_points_the_next_session_to_post_release_planning():
    text = read("docs/development/session_handoff.md")
    header = "\n".join(text.splitlines()[:12])

    assert "**Current milestone:** Version 1.0.0 Released" in header
    assert "**Next task:** Post-release roadmap review" in header
    assert "# V1-005 — Update Project State" in text
    assert "# V1-006 — Complete Release Documentation" in text
    assert "# V1-007 — Create Release Commit" in text
    assert "# Version 1.0 Release Completion" in text
    assert "# Exact Next Task — Post-Release Roadmap Review" in text
    assert "Verify that Sprint 9 and V1-001 through V1-012 are complete." in text
    assert "confirm that V1-008 is still the correct next task" not in text


def test_release_boundary_records_the_published_version_1_release():
    project_state = read("docs/development/project_state.md")
    roadmap = read("docs/development/roadmap.md")
    handoff = read("docs/development/session_handoff.md")
    changelog = read("CHANGELOG.md")

    assert "## [1.0.0] - 2026-07-30" in changelog
    assert "`PROD-007 — Version 1.0.0 Release` is complete." in project_state
    assert "https://pypi.org/project/python-ai-toolkit/1.0.0/" in project_state
    assert "No runtime API, dependency, package metadata" in roadmap
    assert "`V1-008` through `V1-012` are complete." in handoff
