from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"


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


def test_initial_ci_uses_one_explicit_supported_python_version():
    text = workflow_text()

    assert "actions/checkout@v7" in text
    assert "actions/setup-python@v7" in text
    assert text.count('python-version: "3.11"') == 1
    assert "matrix:" not in text


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
