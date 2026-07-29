from pathlib import Path

import pytest

from scripts.validate_release_tag import (
    load_project_version,
    main,
    validate_release_tag,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "release.yml"
SUPPORTED_PYTHON_VERSIONS = ("3.11", "3.12", "3.13", "3.14")


def workflow_text() -> str:
    return RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")


def test_release_workflow_runs_only_for_version_tags():
    text = workflow_text()

    assert text.startswith("name: Release candidate\n")
    assert '\n      - "v*.*.*"\n' in text
    assert "\n  pull_request:" not in text
    assert "\n  workflow_dispatch:" not in text
    assert "\n  workflow_run:" not in text
    assert "\n  branches:" not in text


def test_release_workflow_uses_read_only_tagged_source():
    text = workflow_text()

    assert "\npermissions:\n  contents: read\n" in text
    assert text.count("ref: ${{ github.sha }}") == 3
    assert text.count("persist-credentials: false") == 3
    assert "contents: write" not in text


def test_release_workflow_validates_tag_before_quality_jobs():
    text = workflow_text()

    validate_position = text.index("\n  validate-tag:\n")
    tests_position = text.index("\n  tests:\n")
    build_position = text.index("\n  build:\n")

    assert validate_position < tests_position < build_position
    assert 'run: python scripts/validate_release_tag.py "${GITHUB_REF_NAME}"' in text
    assert "needs: validate-tag" in text


def test_release_workflow_repeats_supported_quality_matrix():
    text = workflow_text()

    assert "actions/checkout@v7" in text
    assert "actions/setup-python@v7" in text
    assert "fail-fast: false" in text
    assert 'python-version: ["3.11", "3.12", "3.13", "3.14"]' in text
    assert all(f'"{version}"' in text for version in SUPPORTED_PYTHON_VERSIONS)
    assert 'python -m pip install -e ".[dev]"' in text
    assert "python -m pip check" in text
    assert "python -m black --check ." in text
    assert "python -m ruff check ." in text
    assert "python -m pytest -q" in text


def test_release_workflow_builds_and_validates_after_quality_jobs():
    text = workflow_text()

    build_job_position = text.index("\n  build:\n")
    build_position = text.index("run: python -m build", build_job_position)
    twine_position = text.index(
        "run: python -m twine check --strict dist/*", build_job_position
    )
    archive_position = text.index(
        "run: python scripts/validate_distributions.py", build_job_position
    )
    upload_position = text.index("uses: actions/upload-artifact@v7", build_job_position)

    assert "needs: tests" in text[build_job_position:]
    assert build_position < twine_position < archive_position < upload_position
    assert "dist/*.whl" in text
    assert "dist/*.tar.gz" in text
    assert "if-no-files-found: error" in text
    assert "python-package-distributions-${{ github.ref_name }}" in text


def test_release_workflow_publishes_only_after_validated_build():
    text = workflow_text()

    build_position = text.index("\n  build:\n")
    publish_position = text.index("\n  publish:\n")
    publish_text = text[publish_position:]
    download_position = publish_text.index("uses: actions/download-artifact@v8")
    publish_action_position = publish_text.index(
        "uses: pypa/gh-action-pypi-publish@v1.14.1"
    )

    assert build_position < publish_position
    assert "needs: build" in publish_text
    assert (
        "if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')"
        in publish_text
    )
    assert download_position < publish_action_position
    assert "name: python-package-distributions-${{ github.ref_name }}" in publish_text
    assert "path: dist/" in publish_text
    assert "packages-dir: dist/" in publish_text


def test_release_workflow_limits_trusted_identity_to_publish_job():
    text = workflow_text()
    publish_text = text[text.index("\n  publish:\n") :]

    assert text.count("id-token: write") == 1
    assert "\n    permissions:\n      id-token: write\n" in publish_text
    assert "\n    environment:\n      name: pypi\n" in publish_text
    assert "url: https://pypi.org/p/python-ai-toolkit" in publish_text
    assert "secrets." not in text
    assert "password:" not in text
    assert "PYPI_API_TOKEN" not in text


def test_release_workflow_publish_job_cannot_rebuild_or_change_source():
    text = workflow_text()
    publish_text = text[text.index("\n  publish:\n") :].lower()

    assert "actions/checkout" not in publish_text
    assert "actions/setup-python" not in publish_text
    assert "python -m build" not in publish_text
    assert "validate_distributions.py" not in publish_text
    assert "\n      - run:" not in publish_text
    assert "contents: write" not in publish_text


def test_release_workflow_does_not_create_a_github_release():
    text = workflow_text().lower()

    assert "gh release" not in text
    assert "softprops/action-gh-release" not in text


def test_release_tag_must_exactly_match_package_version():
    version = load_project_version()

    validate_release_tag(f"v{version}", version)

    with pytest.raises(ValueError, match="does not match package version"):
        validate_release_tag("v1.0.0", version)

    with pytest.raises(ValueError, match="does not match package version"):
        validate_release_tag(version, version)


@pytest.mark.parametrize(
    "version",
    [
        "1.0.0",
        "1.0.0a1",
        "1.0.0b1",
        "1.0.0rc1",
        "0.7.0.dev0",
    ],
)
def test_release_tag_accepts_supported_version_formats(version):
    validate_release_tag(f"v{version}", version)


@pytest.mark.parametrize(
    "version",
    [
        "1",
        "1.0",
        "01.0.0",
        "1.0.0-preview",
        "latest",
    ],
)
def test_release_tag_rejects_unsupported_version_formats(version):
    with pytest.raises(ValueError, match="unsupported release version format"):
        validate_release_tag(f"v{version}", version)


def test_release_tag_cli_accepts_current_project_version(capsys):
    version = load_project_version()

    assert main([f"v{version}"]) == 0
    assert f"release tag v{version} matches package version {version}: PASSED" in (
        capsys.readouterr().out
    )
