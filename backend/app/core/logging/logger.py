"""
Structured logger configuration — console and rotated file output.
"""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

from app.core.logging.formatters import StructuredFormatter


def configure_logging(settings=None) -> None:
    """Configure system logger with structured formatting and file rotation."""
    log_level = logging.INFO
    log_file = "app.log"

    if settings:
        log_level = getattr(logging, getattr(settings, "LOG_LEVEL", "INFO").upper(), logging.INFO)
        log_file = getattr(settings, "LOG_FILE", "app.log")

    # Base logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)

    # 2. File Handler (with Rotation)
    if log_file:
        try:
            log_dir = os.path.dirname(os.path.abspath(log_file))
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(StructuredFormatter(use_colors=False))
            root_logger.addHandler(file_handler)
        except Exception as exc:
            logging.basicConfig(level=log_level)
            logging.warning("Failed to initialize file log handler: %s", exc)