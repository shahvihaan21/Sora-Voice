import sys
from pathlib import Path
try:
    from loguru import logger
except ImportError:
    import logging as _logging
    class _LoggerAdapter:
        def __init__(self): self._logger = _logging.getLogger("sora")
        def remove(self, *args, **kwargs): pass
        def add(self, sink, **kwargs):
            if not self._logger.handlers: self._logger.addHandler(_logging.StreamHandler(sink))
            self._logger.setLevel(kwargs.get("level", "INFO"))
        def __getattr__(self, name): return getattr(self._logger, name)
    logger = _LoggerAdapter()
from BACKEND.config import config

def setup_logger():
    # Remove default handler
    logger.remove()

    # Add console handler with custom colored format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if config.debug else "INFO"
    )

    # Ensure logs dir exists
    config.ensure_dirs()
    log_file = config.logs_dir / "aegis.log"

    # Add file handler for persistent logging
    logger.add(
        str(log_file),
        rotation="10 MB",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG" if config.debug else "INFO",
        encoding="utf-8"
    )

    return logger

log = setup_logger()
