import logging
import logging.config
import os
from pathlib import Path
from rich.logging import RichHandler

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE_PATH = LOG_DIR / "agent.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # File logs should stay clean and standard (no color codes)
        "file_format": {
            "format": "[%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # Rich handles its own visual formatting, so we just pass the message
        "rich_format": {"format": "%(message)s", "datefmt": "[%X]"},
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "level": "INFO",  # Change to DEBUG to see everything in terminal
            "formatter": "rich_format",
            "rich_tracebacks": True,  # Beautiful error parsing
            "markup": True,  # Allows "[bold red]Alert![/]" syntax
            "show_path": False,  # Hides file path to keep console clean
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",  # Capture everything in the file
            "formatter": "file_format",
            "filename": str(LOG_FILE_PATH),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "root": {"handlers": ["console", "file"], "level": "INFO", "propagate": True},
        "src": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        # Silence third-party libs
        "selenium": {"level": "WARNING"},
        "urllib3": {"level": "WARNING"},
        "httpx": {"level": "WARNING"},
        "webdriver_manager": {"level": "WARNING"},
    },
}


def get_logger(name: str):
    """Get a configured logger for a specific module."""
    logging.config.dictConfig(LOGGING_CONFIG)

    return logging.getLogger(name)
