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


def test_ci_installs_from_package_metadata_and_runs_existing_checks():
    text = workflow_text()

    assert 'python -m pip install -e ".[dev]"' in text
    assert "python -m pip check" in text
    assert "AI_FILE_LOGGING_ENABLED" in text
    assert "python -m pytest -q" in text


def test_initial_ci_does_not_take_over_later_release_tasks():
    text = workflow_text().lower()

    assert "python -m black" not in text
    assert "python -m ruff" not in text
    assert "python -m build" not in text
    assert "twine" not in text
    assert "publish" not in text
    assert "pypi" not in text
