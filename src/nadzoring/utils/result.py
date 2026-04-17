"""Result handling utilities for operations that return error-bearing dictionaries.

This module provides pure helper functions for working with result dictionaries
that follow the pattern of containing an optional ``"error"`` field. These
functions enable safe, type-aware handling of operation results without
requiring repetitive error-checking boilerplate.

All functions are pure and operate solely on dictionary data structures,
maintaining compatibility with the existing TypedDict-based result types
used throughout the codebase.

Typical usage:
    from nadzoring.dns_lookup.utils import resolve_with_timer
    from nadzoring.utils.result import is_success, unwrap, unwrap_or

    result = resolve_with_timer("example.com", "A")
    if is_success(result):
        print(result["records"])
    else:
        print(f"DNS error: {result['error']}")

    # Or raise on error:
    try:
        safe_result = unwrap(result)
        print(safe_result["records"])
    except NadzoringError as e:
        print(f"Operation failed: {e}")
"""

from collections.abc import Mapping
from typing import TypeVar

from nadzoring.utils.errors import NadzoringError

T = TypeVar("T")


def is_success(result: Mapping[str, object]) -> bool:
    """Determine whether an operation result completed without errors.

    Checks the presence and value of the ``"error"`` key in the result
    dictionary. A result is considered successful when either the key is
    absent or its value is ``None``.

    Args:
        result: Operation result dictionary that may contain an ``"error"``
            key with a string value or ``None``.

    Returns:
        ``True`` when the result contains no error (error key missing or
        set to ``None``), ``False`` when an error message is present.

    Examples:
        >>> is_success({"records": ["1.2.3.4"]})
        True
        >>> is_success({"error": None, "records": []})
        True
        >>> is_success({"error": "Domain does not exist"})
        False
    """
    return result.get("error") is None


def unwrap[TResult: Mapping[str, object]](result: TResult) -> TResult:
    """Extract the result dictionary or raise an exception on error.

    If the result contains an error, raises a ``NadzoringError`` with the
    error message. Otherwise returns the original result dictionary unchanged.

    This function is useful in contexts where failure should abort the
    current operation and propagate the error upward.

    Args:
        result: Operation result dictionary that may contain an ``"error"``
            key with a string value or ``None``.

    Returns:
        The original result dictionary when no error is present.

    Raises:
        NadzoringError: When ``result["error"]`` is not ``None``. The
            exception message is the string value of the error.

    Examples:
        >>> success = {"records": ["1.2.3.4"]}
        >>> unwrap(success) is success
        True

        >>> failure = {"error": "Query timeout"}
        >>> try:
        ...     unwrap(failure)
        ... except NadzoringError as e:
        ...     print(e)
        Query timeout
    """
    err = result.get("error")
    if err is not None:
        raise NadzoringError(str(err))
    return result


def unwrap_or[TResult: Mapping[str, object], TDefault](
    result: TResult,
    default: TDefault,
) -> TResult | TDefault:
    """Return the result dictionary or a fallback value on error.

    When the result contains no error, returns the original result dictionary.
    When an error is present, returns the provided default value instead.

    This function is useful in contexts where a failed operation should
    degrade gracefully, providing a sensible default (e.g., empty list,
    empty dict, or cached value) rather than propagating the error.

    Args:
        result: Operation result dictionary that may contain an ``"error"``
            key with a string value or ``None``.
        default: Value to return when the result contains an error. Can be
            of any type.

    Returns:
        The original result dictionary if successful, otherwise the
        ``default`` value.

    Examples:
        >>> result = {"error": "No A records"}
        >>> unwrap_or(result, [])
        []

        >>> result = {"records": ["1.2.3.4"]}
        >>> unwrap_or(result, [])
        {'records': ['1.2.3.4']}
    """
    return result if is_success(result) else default
