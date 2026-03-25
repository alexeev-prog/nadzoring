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
    """
    Custom log formatter that adds color coding to log levels.

    Provides colored output for different log levels when enabled.
    Supports both detailed and simple format strings.

    Attributes:
        grey: ANSI escape code for grey color
        blue: ANSI escape code for blue color
        green: ANSI escape code for green color
        yellow: ANSI escape code for yellow color
        red: ANSI escape code for red color
        bold_red: ANSI escape code for bold red color
        reset: ANSI escape code to reset color
        format_str: Default detailed log format string
        simple_format_str: Simple log format string for basic output
        quiet_format_str: Minimal log format string with just the message
        FORMATS: Mapping of log levels to their colored detailed format strings
        SIMPLE_FORMATS: Mapping of log levels to their colored simple format strings

    """

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
        """
        Initialize the colored formatter.

        Args:
            fmt: Optional custom format string (unused, kept for compatibility)
            datefmt: Optional date format string. Defaults to None.
            use_colors: Whether to enable colored output. Defaults to True.
            simple: Whether to use simple format instead of detailed format.
                   Defaults to False.

        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
        self.simple = simple

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with optional colors and format style.

        Args:
            record: The log record to format.

        Returns:
            Formatted log string with appropriate colors and format based on
            the configuration and log level.

        """
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
    """
    Configure logging for command-line interface mode.

    Sets up the root logger with appropriate level and formatter based on
    CLI arguments. Clears any existing handlers before configuration.

    Args:
        verbose: If True, sets log level to DEBUG with detailed formatting.
                Defaults to False.
        quiet: If True, disables all logging by setting level above CRITICAL.
              Defaults to False.
        no_color: If True, disables colored output in log messages.
                 Defaults to False.

    Note:
        - quiet takes precedence over verbose
        - When quiet is True, all logging is disabled regardless of other args
        - When verbose is True and quiet is False, uses detailed format with DEBUG level
        - Otherwise, uses simple format with WARNING level

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
    """
    Get a child logger or the root logger.

    Creates or retrieves a child logger for the specified module name.
    If no name is provided, returns the root logger instance.

    Args:
        name: Optional module name for creating a child logger.
              Defaults to None.

    Returns:
        Logger instance - either a child logger if name is provided,
        or the root logger instance otherwise.

    """
    if name:
        return logger.getChild(name)
    return logger
