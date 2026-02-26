# src/nadzoring/logger.py
"""Logging configuration module."""

import logging
import sys
from logging import Logger, StreamHandler
from typing import Any, ClassVar, Literal, TextIO

logger: Logger = logging.getLogger("nadzoring")

logger.handlers.clear()
logger.propagate = False

DEBUG: Literal[10] = logging.DEBUG
INFO: Literal[20] = logging.INFO
WARNING: Literal[30] = logging.WARNING
ERROR: Literal[40] = logging.ERROR
CRITICAL: Literal[50] = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors."""

    grey: ClassVar[str] = "\x1b[38;20m"
    blue: ClassVar[str] = "\x1b[34;20m"
    green: ClassVar[str] = "\x1b[32;20m"
    yellow: ClassVar[str] = "\x1b[33;20m"
    red: ClassVar[str] = "\x1b[31;20m"
    bold_red: ClassVar[str] = "\x1b[31;1m"
    reset: ClassVar[str] = "\x1b[0m"

    format_str: ClassVar[str] = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    simple_format_str: ClassVar[str] = "%(levelname)s: %(message)s"
    quiet_format_str: ClassVar[str] = "%(message)s"

    FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: blue + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset,
    }

    SIMPLE_FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: blue + simple_format_str + reset,
        logging.INFO: green + simple_format_str + reset,
        logging.WARNING: yellow + simple_format_str + reset,
        logging.ERROR: red + simple_format_str + reset,
        logging.CRITICAL: bold_red + simple_format_str + reset,
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        *,
        use_colors: bool = True,
        simple: bool = False,
    ) -> None:
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
        self.simple = simple

    def format(self, record: logging.LogRecord) -> str:
        if self.use_colors:
            if self.simple:
                formatter = logging.Formatter(
                    self.SIMPLE_FORMATS.get(record.levelno, self.simple_format_str),
                    self.datefmt,
                )
            else:
                formatter = logging.Formatter(
                    self.FORMATS.get(record.levelno, self.format_str),
                    self.datefmt,
                )
        elif self.simple:
            formatter = logging.Formatter(self.simple_format_str, self.datefmt)
        else:
            formatter = logging.Formatter(self.format_str, self.datefmt)

        return formatter.format(record)


def setup_cli_logging(
    *, verbose: bool = False, quiet: bool = False, no_color: bool = False
) -> None:
    """Setup logging for CLI mode.

    Args:
        verbose: Verbose output (DEBUG level)
        quiet: Quiet mode (only results, no logs)
        no_color: Disable colored output
    """
    logger.handlers.clear()

    if quiet:
        logger.setLevel(logging.CRITICAL + 1)  # Disable all logging
        return

    console_handler: StreamHandler[TextIO | Any] = logging.StreamHandler(sys.stderr)

    if verbose:
        logger.setLevel(logging.DEBUG)
        formatter = ColoredFormatter(
            datefmt="%Y-%m-%d %H:%M:%S",
            use_colors=not no_color,
            simple=False,
        )
    else:
        logger.setLevel(logging.WARNING)
        formatter = ColoredFormatter(use_colors=not no_color, simple=True)

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def get_logger(name: str | None = None) -> logging.Logger:
    """Get child logger.

    Args:
        name: Module name

    Returns:
        Logger instance
    """
    if name:
        return logger.getChild(name)
    return logger
