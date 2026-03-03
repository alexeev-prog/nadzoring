"""Input validation utilities."""

import re
import socket
from ipaddress import ip_address
from re import Pattern


def validate_domain(domain: str) -> bool:
    """
    Validate domain name format.

    Checks if the provided string is a valid domain name according to
    standard domain naming conventions.

    Args:
        domain: Domain name string to validate.

    Returns:
        True if the domain name format is valid, False otherwise.

    """
    if len(domain) > 255:
        return False
    if domain[-1] == ".":
        domain = domain[:-1]
    allowed: Pattern[str] = re.compile(
        r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$", re.IGNORECASE
    )
    return bool(allowed.match(domain))


def validate_ip(ip: str) -> bool:
    """
    Validate IP address format.

    Checks if the provided string is a valid IPv4 or IPv6 address.

    Args:
        ip: IP address string to validate.

    Returns:
        True if the IP address format is valid, False otherwise.

    """
    try:
        ip_address(ip)
    except ValueError:
        return False
    else:
        return True


def resolve_hostname(hostname: str) -> str | None:
    """
    Resolve hostname to IP address.

    Performs DNS lookup to resolve the given hostname to its corresponding
    IPv4 address.

    Args:
        hostname: Hostname to resolve.

    Returns:
        IP address string if resolution succeeds, None if resolution fails.

    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
