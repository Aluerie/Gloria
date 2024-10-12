from __future__ import annotations

import logging
import platform
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Generator

__all__ = ("setup_logging",)

# generated at https://patorjk.com/software/taag/ using "Standard" font
ASCII_STARTING_UP_ART = r"""
  ____           _             _   _
 |  _ \ ___  ___| |_ __ _ _ __| |_(_)_ __   __ _
 | |_) / _ \/ __| __/ _` | '__| __| | '_ \ / _` |
 |  _ <  __/\__ \ || (_| | |  | |_| | | | | (_| |
 |_| \_\___||___/\__\__,_|_|   \__|_|_| |_|\__, |
                                           |___/

            [ RESTARTING ]
"""


@contextmanager
def setup_logging() -> Generator[Any, Any, Any]:
    """Setup logging."""
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    try:
        # Stream Handler
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "{asctime} | {levelname:<7} | {name:<23} | {lineno:<4} | {funcName:<30} | {message}",
            "%H:%M:%S %d/%m",
            style="{",
        )

        handler.setFormatter(fmt)
        log.addHandler(handler)

        # File Handler
        file_handler = RotatingFileHandler(
            filename=".steam.log",
            encoding="utf-8",
            mode="w",
            maxBytes=9 * 1024 * 1024,  # 9 MiB
            backupCount=5,  # Rotate through 5 files
        )
        file_handler.setFormatter(fmt)
        log.addHandler(file_handler)

        if platform.system() == "Linux":
            # so start-ups in logs are way more noticeable
            log.info(ASCII_STARTING_UP_ART)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for h in handlers:
            h.close()
            log.removeHandler(h)
