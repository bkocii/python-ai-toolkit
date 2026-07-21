import logging
from io import StringIO

import pytest

from ai.exceptions import AIConfigurationError
from ai.logger import LOGGER_NAME, get_ai_logger


@pytest.fixture(autouse=True)
def reset_toolkit_logger():
    """
    Isolate the process-wide toolkit logger between tests.
    """
    logger = logging.getLogger(LOGGER_NAME)

    original_handlers = list(logger.handlers)
    original_level = logger.level
    original_propagate = logger.propagate

    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    yield

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    for handler in original_handlers:
        logger.addHandler(handler)

    logger.setLevel(original_level)
    logger.propagate = original_propagate


def flush_handlers(logger: logging.Logger) -> None:
    for handler in logger.handlers:
        handler.flush()


def test_file_logging_creates_parent_directory_and_file(
    tmp_path,
):
    log_path = tmp_path / "nested" / "toolkit.log"

    logger = get_ai_logger(
        file_path=str(log_path),
    )

    logger.info("Test message")
    flush_handlers(logger)

    assert log_path.exists()
    assert "Test message" in log_path.read_text(encoding="utf-8")


def test_disabled_file_logging_creates_no_directory_or_file(
    tmp_path,
):
    log_path = tmp_path / "logs" / "toolkit.log"

    logger = get_ai_logger(
        file_path=str(log_path),
        file_logging_enabled=False,
    )

    logger.info("Ignored file message")

    assert not log_path.exists()
    assert not any(
        isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    )


def test_logger_uses_configured_level(tmp_path):
    log_path = tmp_path / "toolkit.log"

    logger = get_ai_logger(
        level="WARNING",
        file_path=str(log_path),
    )

    logger.info("Hidden information")
    logger.warning("Visible warning")
    flush_handlers(logger)

    content = log_path.read_text(encoding="utf-8")

    assert "Hidden information" not in content
    assert "Visible warning" in content


def test_reconfiguration_replaces_toolkit_handler(
    tmp_path,
):
    first_path = tmp_path / "first.log"
    second_path = tmp_path / "second.log"

    logger = get_ai_logger(
        file_path=str(first_path),
    )
    logger = get_ai_logger(
        file_path=str(second_path),
    )

    managed_handlers = [
        handler
        for handler in logger.handlers
        if getattr(
            handler,
            "_ai_toolkit_managed",
            False,
        )
    ]

    assert len(managed_handlers) == 1
    assert isinstance(
        managed_handlers[0],
        logging.FileHandler,
    )
    assert managed_handlers[0].baseFilename == str(second_path.resolve())


def test_logger_preserves_application_handler():
    logger = logging.getLogger(LOGGER_NAME)
    output = StringIO()

    application_handler = logging.StreamHandler(output)
    logger.addHandler(application_handler)

    configured_logger = get_ai_logger(
        file_logging_enabled=False,
    )

    configured_logger.warning("Application message")
    application_handler.flush()

    assert application_handler in configured_logger.handlers
    assert "Application message" in output.getvalue()
    assert not any(
        isinstance(handler, logging.NullHandler)
        for handler in configured_logger.handlers
    )


def test_logger_disables_propagation():
    logger = get_ai_logger(
        file_logging_enabled=False,
    )

    assert logger.propagate is False


def test_logger_rejects_invalid_level():
    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI_LOG_LEVEL value 'VERBOSE'",
    ):
        get_ai_logger(
            level="verbose",
            file_logging_enabled=False,
        )
