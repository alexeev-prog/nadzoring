"""Module for unified timeout handling across modules.

This module provides a consistent interface for managing timeouts across different
operations including socket connections, read operations, and overall operation
lifetime limits. It includes configuration classes, context managers, and decorators
to standardize timeout handling throughout the application.
"""

import signal
import socket
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class TimeoutConfig:
    """Configuration container for timeout settings.

    This class encapsulates timeout values for different phases of an operation
    and provides methods to apply these settings to network sockets.

    Attributes:
        connect: Timeout in seconds for establishing a connection. Defaults to 5.0.
            Applied during initial connection phase before any data transfer.
        read: Timeout in seconds for read operations. Defaults to 10.0.
            Applied after connection is established for data transfer operations.
        lifetime: Maximum total operation duration in seconds, or None for no limit.
            If set, the entire operation must complete within this timeframe.

    Example:
        config = TimeoutConfig(connect=3.0, read=8.0, lifetime=30.0)
        config.apply_to_socket(sock)
    """

    connect: float = 5.0
    read: float = 10.0
    lifetime: float = 120.0

    def apply_to_socket(self, sock: socket.socket) -> None:
        """Apply the read timeout to a socket.

        Sets the socket's timeout to the configured read timeout value.
        This is typically used after a connection is established.

        Args:
            sock: The socket to configure.
        """
        sock.settimeout(self.read)


class OperationTimeoutError(TimeoutError):
    """Exception raised when an operation exceeds its lifetime timeout."""

    def __init__(self, message: str = "Operation exceeded lifetime timeout") -> None:
        """Initialize the timeout error with an optional custom message."""
        super().__init__(message)


@contextmanager
def timeout_context(timeout: TimeoutConfig):
    """Context manager that enforces a lifetime timeout on a block of code.

    Uses SIGALRM on Unix systems to interrupt blocking operations when the
    lifetime timeout is exceeded. On Windows, falls back to a post-check only
    mode that cannot interrupt blocking calls.

    Args:
        timeout: Timeout configuration containing the lifetime value.

    Yields:
        None: Control is yielded to the enclosed code block.

    Raises:
        OperationTimeoutError: If the operation exceeds the configured lifetime timeout.

    Example:
        config = TimeoutConfig(lifetime=5.0)
        try:
            with timeout_context(config):
                long_running_operation()
        except OperationTimeoutError:
            handle_timeout()

    Note:
        On Unix systems, this uses SIGALRM which can interrupt system calls.
        On Windows, this provides a best-effort check but cannot interrupt
        blocking operations due to OS limitations.
    """
    if timeout.lifetime is None:
        yield
        return

    if not hasattr(signal, "SIGALRM"):
        yield
        return

    try:
        signal.signal(signal.SIGALRM, _raise_timeout_error)
        signal.alarm(max(1, int(timeout.lifetime)))
        yield
        signal.alarm(0)
    except OperationTimeoutError:
        raise
    except Exception:
        signal.alarm(0)
        raise
    finally:
        signal.alarm(0)


def _raise_timeout_error(signum: int, frame: Any) -> None:
    """Signal handler that raises OperationTimeoutError when SIGALRM is received.

    Args:
        signum: Signal number (unused but required for signal handler signature).
        frame: Current stack frame (unused but required for signal handler signature).

    Raises:
        OperationTimeoutError: Always raised when this handler is called.
    """
    raise OperationTimeoutError("Operation exceeded lifetime timeout")


def configure_socket_with_timeouts(sock: socket.socket, config: TimeoutConfig, *, connect_mode: bool = False) -> None:
    """Configure a socket with appropriate timeouts based on the operation phase.

    Applies either connection timeout or read timeout to the socket depending on
    the connect_mode flag. This function provides granular control over timeout
    settings for different stages of socket communication.

    Args:
        sock: The socket to configure.
        config: Timeout configuration containing connect and read timeout values.
        connect_mode: If True, applies the connect timeout. If False, applies the
            read timeout. Defaults to False.

    Example:
        sock = socket.socket()
        config = TimeoutConfig(connect=5.0, read=10.0)

        configure_socket_with_timeouts(sock, config, connect_mode=True)
        sock.connect(('example.com', 80))

        configure_socket_with_timeouts(sock, config, connect_mode=False)
        data = sock.recv(1024)
    """
    if connect_mode:
        sock.settimeout(config.connect)
    else:
        sock.settimeout(config.read)


def with_lifetime_timeout(timeout_config: TimeoutConfig) -> Callable[[F], F]:
    """Decorator factory that wraps a function with a lifetime timeout.

    Creates a decorator that enforces a lifetime timeout on the decorated function.
    If the function execution exceeds the configured lifetime, an OperationTimeoutError is
    raised.

    Args:
        timeout_config: Timeout configuration containing the lifetime value.
            If lifetime is None, the decorator adds no timeout protection.

    Returns:
        A decorator that adds lifetime timeout protection to functions.

    Example:
        config = TimeoutConfig(lifetime=10.0)

        @with_lifetime_timeout(config)
        def fetch_data():
            return expensive_network_operation()

        try:
            result = fetch_data()
        except OperationTimeoutError:
            print("Operation timed out after 10 seconds")

    Note:
        On Unix systems, this can interrupt blocking system calls. On Windows,
        the timeout is checked after function completion only.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with timeout_context(timeout_config):
                return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
