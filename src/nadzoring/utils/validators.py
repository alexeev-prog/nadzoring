"""Input validation utilities."""

import re
import socket
from ipaddress import AddressValueError, ip_address
from re import Pattern


def validate_domain(domain: str) -> bool:
    """
    Validate a domain name against standard naming conventions.

    Checks length, optional trailing dot, and per-label character rules
    (1-63 characters, alphanumeric plus hyphens, no leading/trailing hyphens).

    Args:
        domain: Domain name string to validate.

    Returns:
        ``True`` if the domain name format is valid, ``False`` otherwise.

    Examples:
        >>> validate_domain("example.com")
        True
        >>> validate_domain("-bad.example.com")
        False

    """
    if len(domain) > 255:
        return False

    domain = domain.removesuffix(".")

    pattern: Pattern[str] = re.compile(
        r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$",
        re.IGNORECASE,
    )
    return bool(pattern.match(domain))


def validate_ip(ip: str) -> bool:
    """
    Check whether a string is a valid IPv4 or IPv6 address.

    Args:
        ip: IP address string to validate.

    Returns:
        ``True`` if the string is a valid IP address, ``False`` otherwise.

    Examples:
        >>> validate_ip("8.8.8.8")
        True
        >>> validate_ip("not-an-ip")
        False

    """
    try:
        ip_address(ip)
    except (ValueError, AddressValueError):
        return False
    else:
        return True


def resolve_hostname(hostname: str) -> str | None:
    """
    Resolve a hostname to its IPv4 address via DNS.

    Args:
        hostname: Hostname to resolve (e.g. ``"example.com"``).

    Returns:
        IPv4 address string on success, or ``None`` if resolution fails.

    Examples:
        >>> ip = resolve_hostname("localhost")
        >>> ip == "127.0.0.1"
        True

    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
