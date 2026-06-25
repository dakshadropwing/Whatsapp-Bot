"""
Logging formatters — ANSI colored structured console formatting.
"""
from __future__ import annotations

import logging
import time


class StructuredFormatter(logging.Formatter):
    """Custom formatter rendering detailed console lines with ANSI colors."""

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[41m",  # Red background
        "RESET": "\033[0m",
    }

    def __init__(self, use_colors: bool = True) -> None:
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        asctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        level = record.levelname

        if self.use_colors:
            color = self.COLORS.get(level, "")
            reset = self.COLORS.get("RESET", "")
            level_str = f"{color}{level:<8}{reset}"
        else:
            level_str = f"{level:<8}"

        msg = record.getMessage()
        name = record.name

        exc_str = ""
        if record.exc_info:
            exc_str = f"\n{self.formatException(record.exc_info)}"

        return f"{asctime} | {level_str} | {name} | {msg}{exc_str}"
