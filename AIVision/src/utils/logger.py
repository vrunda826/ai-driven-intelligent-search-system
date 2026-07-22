"""Centralized logger for the ai-vision pipeline."""

import logging
import os
import sys


def get_logger(name: str, log_file: str = None, level: str = "INFO") -> logging.Logger:
    """Create (or fetch) a logger with a console handler and an optional file handler.

    Args:
        name: logger name, typically __name__ of the calling module.
        log_file: path to a log file. Parent directory is created if missing.
        level: logging level as a string, e.g. "INFO", "DEBUG".

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured (e.g. re-imported), avoid duplicate handlers.
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
