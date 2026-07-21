import logging
from pathlib import Path

from ai.exceptions import AIConfigurationError

LOGGER_NAME = "ai_toolkit"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

_MANAGED_HANDLER_ATTRIBUTE = "_ai_toolkit_managed"


def _resolve_log_level(level: str) -> int:
    """
    Convert a log-level name into a logging level.
    """
    normalized_level = level.strip().upper()
    resolved_level = getattr(logging, normalized_level, None)

    if not isinstance(resolved_level, int):
        raise AIConfigurationError(
            f"Invalid AI_LOG_LEVEL value '{normalized_level}'. "
            "Choose one of: CRITICAL, DEBUG, ERROR, INFO, WARNING."
        )

    return resolved_level


def _is_toolkit_managed_handler(
    handler: logging.Handler,
) -> bool:
    return bool(
        getattr(
            handler,
            _MANAGED_HANDLER_ATTRIBUTE,
            False,
        )
    )


def _mark_toolkit_managed_handler(
    handler: logging.Handler,
) -> logging.Handler:
    setattr(
        handler,
        _MANAGED_HANDLER_ATTRIBUTE,
        True,
    )

    return handler


def _remove_toolkit_managed_handlers(
    logger: logging.Logger,
) -> None:
    """
    Remove only handlers created by the toolkit.

    Application-owned handlers are preserved.
    """
    for handler in list(logger.handlers):
        if not _is_toolkit_managed_handler(handler):
            continue

        logger.removeHandler(handler)
        handler.close()


def get_ai_logger(
    level: str = "INFO",
    file_path: str = "logs/ai_toolkit.log",
    file_logging_enabled: bool = True,
) -> logging.Logger:
    """
    Return the configured toolkit logger.

    Toolkit-managed handlers may be replaced when configuration changes.
    Handlers added by applications are preserved.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(_resolve_log_level(level))
    logger.propagate = False

    _remove_toolkit_managed_handlers(logger)

    if file_logging_enabled:
        resolved_path = Path(file_path).expanduser()
        resolved_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_handler = logging.FileHandler(
            resolved_path,
            encoding="utf-8",
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

        logger.addHandler(_mark_toolkit_managed_handler(file_handler))

    elif not logger.handlers:
        null_handler = logging.NullHandler()

        logger.addHandler(_mark_toolkit_managed_handler(null_handler))

    return logger
