import logging
import sys
try:
    from pythonjsonlogger import json as jsonlogger
except ImportError:
    from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure structured JSON logging for enterprise observability."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Remove existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    log_handler = logging.StreamHandler(sys.stdout)

    if settings.ENVIRONMENT == "production":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(module)s %(lineno)d %(message)s"
        )
    else:
        # Development human-readable formatting
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").handlers = [log_handler]
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )

    return logger
