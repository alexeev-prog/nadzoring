"""
Input validation utilities.

Each function is responsible for a single validation concern (SRP).
Validators return ``bool`` and never raise; higher-level callers that
want exceptions should use :mod:`nadzoring.utils.errors`.
"""

import re
import socket
from ipaddress import AddressValueError, ip_address
from re import Pattern

# ---------------------------------------------------------------------------
# Domain validation
# ---------------------------------------------------------------------------

_DOMAIN_PATTERN: Pattern[str] = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$",
    re.IGNORECASE,
)

_MAX_DOMAIN_LENGTH = 255
_MAX_LABEL_LENGTH = 63


def validate_domain(domain: str) -> bool:
    """
    Validate a domain name against standard naming conventions.

    Checks total length (≤ 255), optional trailing dot, and per-label
    character rules (1-63 chars, alphanumeric + hyphens, no leading or
    trailing hyphens).

    Args:
        domain: Domain name string to validate.

    Returns:
        ``True`` if the format is valid, ``False`` otherwise.

    Examples:
        >>> validate_domain("example.com")
        True
        >>> validate_domain("-bad.example.com")
        False
        >>> validate_domain("a" * 256)
        False

    """
    if not domain or len(domain) > _MAX_DOMAIN_LENGTH:
        return False

    domain = domain.removesuffix(".")
    return bool(_DOMAIN_PATTERN.match(domain))


# ---------------------------------------------------------------------------
# IP address validation
# ---------------------------------------------------------------------------


def validate_ip(ip: str) -> bool:
    """
    Check whether a string is a valid IPv4 or IPv6 address.

    Args:
        ip: IP address string to validate.

    Returns:
        ``True`` if the string is a valid address, ``False`` otherwise.

    Examples:
        >>> validate_ip("8.8.8.8")
        True
        >>> validate_ip("::1")
        True
        >>> validate_ip("not-an-ip")
        False

    """
    if not ip:
        return False
    try:
        ip_address(ip)
    except (ValueError, AddressValueError):
        return False
    return True


def validate_ipv4(ip: str) -> bool:
    """
    Check whether a string is a valid IPv4 address.

    Args:
        ip: IP address string to validate.

    Returns:
        ``True`` for valid IPv4 addresses only.

    Examples:
        >>> validate_ipv4("192.168.1.1")
        True
        >>> validate_ipv4("::1")
        False

    """
    if not ip:
        return False
    try:
        return ip_address(ip).version == 4
    except (ValueError, AddressValueError):
        return False


def validate_ipv6(ip: str) -> bool:
    """
    Check whether a string is a valid IPv6 address.

    Args:
        ip: IP address string to validate.

    Returns:
        ``True`` for valid IPv6 addresses only.

    Examples:
        >>> validate_ipv6("::1")
        True
        >>> validate_ipv6("8.8.8.8")
        False

    """
    if not ip:
        return False
    try:
        return ip_address(ip).version == 6
    except (ValueError, AddressValueError):
        return False


# ---------------------------------------------------------------------------
# Port validation
# ---------------------------------------------------------------------------

_PORT_MIN = 1
_PORT_MAX = 65535


def validate_port(port: int) -> bool:
    """
    Check whether an integer is a valid TCP/UDP port number.

    Args:
        port: Port number to validate.

    Returns:
        ``True`` when *port* is in the range 1-65535.

    Examples:
        >>> validate_port(80)
        True
        >>> validate_port(0)
        False
        >>> validate_port(65536)
        False

    """
    return _PORT_MIN <= port <= _PORT_MAX


# ---------------------------------------------------------------------------
# Hostname resolution
# ---------------------------------------------------------------------------


def resolve_hostname(hostname: str) -> str | None:
    """
    Resolve a hostname to its IPv4 address via the system DNS resolver.

    Args:
        hostname: Hostname to resolve (e.g. ``"example.com"``).

    Returns:
        IPv4 address string on success, or ``None`` if resolution fails.

    Examples:
        >>> ip = resolve_hostname("localhost")
        >>> ip == "127.0.0.1"
        True
        >>> resolve_hostname("this.domain.does.not.exist.invalid")
        # returns None

    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
