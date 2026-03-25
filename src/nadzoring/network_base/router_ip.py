"""
Default gateway (router) IP address resolution for Linux and Windows.

On some Linux distributions the ``net-tools`` package must be installed
because the ``route`` command is not available by default::

    sudo apt install net-tools
"""

from ipaddress import AddressValueError, IPv4Address, IPv6Address
from logging import Logger
from platform import system
from socket import gaierror, gethostbyname
from subprocess import CalledProcessError, check_output

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def get_ip_from_host(hostname: str) -> str:
    """
    Resolve a hostname to an IP address, returning the input on failure.

    Args:
        hostname: Hostname or IP address string to resolve.

    Returns:
        Resolved IP address string, or ``hostname`` unchanged if resolution
        fails.

    """
    try:
        return gethostbyname(hostname)
    except gaierror:
        return hostname


def _is_valid_ipv4(value: str) -> bool:
    """Return ``True`` if *value* is a syntactically valid IPv4 address."""
    try:
        IPv4Address(value)
    except (AddressValueError, ValueError):
        return False
    return True


def _is_valid_ipv6(value: str) -> bool:
    """Return ``True`` if *value* is a syntactically valid IPv6 address."""
    try:
        IPv6Address(value)
    except (AddressValueError, ValueError):
        return False
    return True


def check_ipv4(hostname: str) -> str:
    """
    Return a resolved IPv4 address for *hostname*, or the input unchanged.

    If *hostname* is already a valid IPv4 address it is returned in normalized
    dotted-decimal form. Otherwise a DNS lookup is attempted via
    :func:`get_ip_from_host`.

    Args:
        hostname: Hostname or IPv4 address string.

    Returns:
        Normalized IPv4 address string, or *hostname* unchanged when
        resolution fails.
    """
    parts = hostname.split(".")
    if len(parts) == 4 and all(part.isdigit() for part in parts):
        octets = [int(part) for part in parts]
        if all(0 <= octet <= 255 for octet in octets):
            return ".".join(str(octet) for octet in octets)

    if _is_valid_ipv4(hostname):
        return hostname
    return get_ip_from_host(hostname)


def check_ipv6(hostname: str) -> str:
    """
    Return a resolved IPv6 address for *hostname*, or the input unchanged.

    If *hostname* is already a valid IPv6 address it is returned as-is.
    Otherwise a DNS lookup is attempted via :func:`get_ip_from_host`.

    Args:
        hostname: Hostname or IPv6 address string.

    Returns:
        IPv6 address string, or *hostname* unchanged when resolution fails.

    """
    if _is_valid_ipv6(hostname):
        return hostname
    return get_ip_from_host(hostname)


def _get_linux_router_ip(*, ipv6: bool) -> str | None:
    """Retrieve the default gateway address on Linux via ``route -n``."""
    try:
        raw: str = check_output("route -n | grep UG", shell=True).decode().split()[1]
    except (CalledProcessError, IndexError, OSError):
        logger.exception("Failed to retrieve router IP on Linux")
        return None

    return check_ipv6(raw) if ipv6 else check_ipv4(raw)


def _get_windows_router_ip(*, ipv6: bool) -> str | None:
    """Retrieve the default gateway address on Windows via ``route PRINT``."""
    try:
        raw: str = (
            check_output(
                "route PRINT 0* -4 | findstr 0.0.0.0",
                shell=True,
            )
            .decode("cp866")
            .split()[-3]
        )
    except (CalledProcessError, IndexError, OSError, UnicodeDecodeError):
        logger.exception("Failed to retrieve router IP on Windows")
        return None

    return check_ipv6(raw) if ipv6 else check_ipv4(raw)


def router_ip(*, ipv6: bool = False) -> str | None:
    """
    Return the default router (gateway) IP address for the current system.

    Supports Linux (via ``route -n``) and Windows (via ``route PRINT``).
    The raw gateway value is validated and, if necessary, resolved from a
    hostname to an IP address.

    Args:
        ipv6: When ``True``, treat the gateway value as an IPv6 address.
            Defaults to ``False`` (IPv4).

    Returns:
        Gateway IP address string, or ``None`` when the gateway cannot be
        determined or the operating system is not supported.

    """
    os_name: str = system()

    if os_name == "Linux":
        return _get_linux_router_ip(ipv6=ipv6)

    if os_name == "Windows":
        return _get_windows_router_ip(ipv6=ipv6)

    logger.warning("Unsupported operating system for router IP detection: %s", os_name)
    return None
