from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
SUPPORTED_PYTHON_VERSIONS = ("3.11", "3.12", "3.13", "3.14")


def workflow_text() -> str:
    return CI_WORKFLOW_PATH.read_text(encoding="utf-8")


def test_ci_workflow_runs_for_pushes_and_pull_requests():
    text = workflow_text()

    assert text.startswith("name: CI\n")
    assert "\n  push:\n" in text
    assert "\n  pull_request:\n" in text
    assert "pull_request_target" not in text
    assert "workflow_run" not in text


def test_ci_workflow_uses_read_only_repository_access():
    text = workflow_text()

    assert "\npermissions:\n  contents: read\n" in text
    assert "persist-credentials: false" in text
    assert "contents: write" not in text
    assert "id-token: write" not in text


def test_ci_uses_the_complete_supported_python_matrix():
    text = workflow_text()

    assert "actions/checkout@v7" in text
    assert "actions/setup-python@v7" in text
    assert "name: Tests (Python ${{ matrix.python-version }})" in text
    assert "fail-fast: false" in text
    assert 'python-version: ["3.11", "3.12", "3.13", "3.14"]' in text
    assert "python-version: ${{ matrix.python-version }}" in text
    assert all(f'"{version}"' in text for version in SUPPORTED_PYTHON_VERSIONS)


def test_ci_installs_from_package_metadata_and_runs_quality_checks():
    text = workflow_text()

    assert 'python -m pip install -e ".[dev]"' in text
    assert "python -m pip check" in text
    assert "python -m black --check ." in text
    assert "python -m ruff check ." in text
    assert "AI_FILE_LOGGING_ENABLED" in text
    assert "python -m pytest -q" in text


def test_ci_builds_distributions_after_all_quality_jobs_pass():
    text = workflow_text()

    assert "\n  build:\n" in text
    assert "name: Build distributions" in text
    assert "needs: tests" in text
    assert 'python-version: "3.11"' in text
    assert "python -m pip install build twine" in text
    assert "python -m build" in text


def test_ci_validates_the_exact_built_distributions_before_upload():
    text = workflow_text()

    build_position = text.index("run: python -m build")
    twine_position = text.index("run: python -m twine check --strict dist/*")
    archive_position = text.index("run: python scripts/validate_distributions.py")
    upload_position = text.index("uses: actions/upload-artifact@v7")

    assert build_position < twine_position < archive_position < upload_position


def test_ci_retains_only_validated_distribution_artifacts():
    text = workflow_text()

    assert "actions/upload-artifact@v7" in text
    assert "name: python-package-distributions" in text
    assert "dist/*.whl" in text
    assert "dist/*.tar.gz" in text
    assert "if-no-files-found: error" in text


def test_ci_does_not_publish_distributions():
    text = workflow_text().lower()

    assert "publish" not in text
    assert "pypi" not in text
