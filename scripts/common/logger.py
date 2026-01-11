"""Logger configuration."""

import logging
import logging.handlers
import sys
import datetime

from typing import Optional

def configure_logging(
    log_level: str = "INFO",
    log_file_path: Optional[str] = None
):
    """Configure the root logger.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file_path: Optional file path to log to a file. If None, logs to console.

    Returns:
        None
    """
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add handler
    handlers = []
    if log_file_path:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file_path,
            interval=30,
            when="D",
            atTime=datetime.time(hour=1, minute=0, second=0),
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers
    )
