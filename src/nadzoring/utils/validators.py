# src/nadzoring/cli/utils/validators.py
"""Input validation utilities."""

import re
import socket
from ipaddress import ip_address
from re import Pattern


def validate_domain(domain: str) -> bool:
    """Validate domain name format."""
    if len(domain) > 255:
        return False
    if domain[-1] == ".":
        domain = domain[:-1]
    allowed: Pattern[str] = re.compile(
        r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$", re.IGNORECASE
    )
    return bool(allowed.match(domain))


def validate_ip(ip: str) -> bool:
    """Validate IP address format."""
    try:
        ip_address(ip)
    except ValueError:
        return False
    else:
        return True


def resolve_hostname(hostname: str) -> str | None:
    """Resolve hostname to IP address."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
