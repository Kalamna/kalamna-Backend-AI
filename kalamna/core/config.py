# logging conf

from logging.config import dictConfig


def setup_logging():
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
                    "level": "WARNING",  # silence uvicorn.info chatter
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": "WARNING",  # reduce startup noise
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": "WARNING",  # hide access logs unless elevated
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
