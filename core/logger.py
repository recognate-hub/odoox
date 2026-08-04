import logging
import structlog
import sys
from typing import Any

from config.settings import get_settings


def setup_logging() -> None:
    """
    Configure structured logging for the application using Structlog.
    """
    settings = get_settings()
    log_level_name = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> Any:
    """
    Get a structured logger for a given module.
    
    Args:
        name (str): The name of the module (usually __name__).
        
    Returns:
        structlog.BoundLogger: The configured structured logger.
    """
    return structlog.get_logger(name)
