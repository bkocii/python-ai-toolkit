import pytest


@pytest.fixture(autouse=True)
def disable_benchmark_file_logging(monkeypatch):
    """
    Prevent toolkit-managed file I/O from affecting benchmarks.
    """
    monkeypatch.setenv("AI_FILE_LOGGING_ENABLED", "false")
