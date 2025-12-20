"""
Logging configuration and helpers.
Human-readable structured logging setup for the application.
"""

import logging
import sys
import structlog


def setup_logging() -> None:
    """Configure human-readable structlog + stdlib logging for FastAPI & Uvicorn."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%H:%M:%S"),
            structlog.dev.ConsoleRenderer(
                colors=True,
                pad_event=32,     # aligns log messages nicely
                sort_keys=False,  # preserves logical order
            ),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    # Silence uvicorn access logs (you already log requests yourself)
    logging.getLogger("uvicorn.access").disabled = True

    # Keep uvicorn error logs
    logging.getLogger("uvicorn.error").propagate = True

    # Reduce third-party noise (optional but recommended)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


def get_logger(name: str = "kalamna"):
    """Return a human-readable structlog logger."""
    return structlog.get_logger(name)
