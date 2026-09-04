"""Structured logging with sanitized output (no stack traces to end users)."""
import sys
import logging as _stdlib_logging
try:
    from loguru import logger
except ImportError:  # Optional dependency: keep diagnostics/tests importable.
    class _FallbackLogger:
        def __init__(self):
            self._logger = _stdlib_logging.getLogger("sora")
        def remove(self, *args, **kwargs): pass
        def add(self, sink, **kwargs):
            if not self._logger.handlers:
                handler = _stdlib_logging.StreamHandler(sink)
                self._logger.addHandler(handler)
            self._logger.setLevel(kwargs.get("level", "INFO"))
        def __getattr__(self, name):
            return getattr(self._logger, name)
    logger = _FallbackLogger()
from sora.config.settings import config


def _sanitize(message: str) -> str:
    """Keep secrets out of logs."""
    for key in ("api_key", "token", "password", "secret"):
        if key in message.lower():
            return message[:120] + "... [redacted]"
    return message


def setup_logger():
    logger.remove()
    fmt = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    level = config.log_level if config.debug else "INFO"
    logger.add(sys.stderr, format=fmt, level=level)
    config.ensure_dirs()
    logger.add(
        str(config.logs_dir / "sora.log"),
        rotation="10 MB",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        encoding="utf-8",
    )
    return logger


def user_friendly_error(exc: Exception) -> str:
    """Map an exception to a safe, human-readable message."""
    return f"{type(exc).__name__} occurred while handling your request."


log = setup_logger()
