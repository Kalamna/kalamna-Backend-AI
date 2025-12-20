"""
Logging configuration and helpers.
Structured logging setup for the application.
"""

import logging
from logging.config import dictConfig


def setup_logging():
    """Configure console and file handlers plus uvicorn access logging."""
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": "kalamna.log",
                    "formatter": "default",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["console"],
                    "level": "WARNING",
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
                "kalamna": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )


def get_logger(name: str = "kalamna") -> logging.Logger:
    """Return a named logger configured by setup_logging."""
    return logging.getLogger(name)
