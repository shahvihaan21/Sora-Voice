import sys
from pathlib import Path
from loguru import logger
from core.config import config

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
