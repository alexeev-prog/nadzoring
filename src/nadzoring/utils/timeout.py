"""Module for unified timeout handling across modules.

This module provides a consistent interface for managing timeouts across different
operations including socket connections, read operations, and overall operation
lifetime limits. It includes configuration classes, context managers, and decorators
to standardize timeout handling throughout the application.
"""

import socket
import threading
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import TypeVar

F = TypeVar("F", bound=Callable)


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

        Note:
            This method applies the read timeout only. For connection-specific
            timeout configuration, use configure_socket_with_timeouts() with
            connect_mode=True.
        """
        sock.settimeout(self.read)


@contextmanager
def timeout_context(timeout: TimeoutConfig):
    """Context manager that enforces a lifetime timeout on a block of code.

    Creates a timer that will raise a TimeoutError if the enclosed operation
    exceeds the configured lifetime. If no lifetime is configured, the context
    manager becomes a no-op.

    Args:
        timeout: Timeout configuration containing the lifetime value.

    Yields:
        None: Control is yielded to the enclosed code block.

    Raises:
        TimeoutError: If the operation exceeds the configured lifetime timeout.

    Example:
        config = TimeoutConfig(lifetime=5.0)
        try:
            with timeout_context(config):
                # Operation that must complete within 5 seconds
                long_running_operation()
        except TimeoutError:
            handle_timeout()

    Note:
        The timer runs in a daemon thread which does not block interpreter shutdown.
        The timer is always cancelled when the context exits, even if an exception
        occurs.
    """
    if timeout.lifetime is None:
        yield
        return

    timeout_occurred = threading.Event()

    def _timeout_handler():
        timeout_occurred.set()

    timer = threading.Timer(timeout.lifetime, _timeout_handler)
    timer.daemon = True
    timer.start()

    try:
        yield

        if timeout_occurred.is_set():
            raise TimeoutError(f"Operation exceeded lifetime timeout: {timeout.lifetime}s")
    finally:
        timer.cancel()


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

        # During connection phase
        configure_socket_with_timeouts(sock, config, connect_mode=True)
        sock.connect(('example.com', 80))

        # After connection, switch to read timeout
        configure_socket_with_timeouts(sock, config, connect_mode=False)
        data = sock.recv(1024)

    Note:
        This function does not modify the socket's blocking mode, only the timeout
        value. The timeout is applied in seconds as a float.
    """
    if connect_mode:
        sock.settimeout(config.connect)
    else:
        sock.settimeout(config.read)


def with_lifetime_timeout(timeout_config: TimeoutConfig) -> Callable[[F], F]:
    """Decorator factory that wraps a function with a lifetime timeout.

    Creates a decorator that enforces a lifetime timeout on the decorated function.
    If the function execution exceeds the configured lifetime, a TimeoutError is
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
            # This function must complete within 10 seconds
            return expensive_network_operation()

        try:
            result = fetch_data()
        except TimeoutError:
            print("Operation timed out after 10 seconds")

    Note:
        The decorator works by wrapping the function call in a timeout_context.
        All arguments and return values are preserved through the wrapper.
        The decorated function's metadata (__name__, __doc__, etc.) are preserved
        using functools.wraps.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with timeout_context(timeout_config):
                return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
