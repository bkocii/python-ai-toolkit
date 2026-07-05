import logging
from pathlib import Path


def get_ai_logger() -> logging.Logger:
    """
    Return toolkit logger.

    Logs are written to logs/ai_toolkit.log.
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("ai_toolkit")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(logs_dir / "ai_toolkit.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
