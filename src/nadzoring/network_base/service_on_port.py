"""Service name resolution for port numbers."""

from socket import getservbyport

_FALLBACK_SERVICES: dict[int, str] = {
    21: "ftp",
    22: "ssh",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    143: "imap",
    443: "https",
    993: "imaps",
    995: "pop3s",
    3306: "mysql",
    5432: "postgresql",
    6379: "redis",
    8080: "http-alt",
    8443: "https-alt",
    27017: "mongodb",
}


def get_service_on_port(port: int) -> str:
    """
    Return the service name associated with a given port number.

    First queries the system service database via ``socket.getservbyport``.
    Falls back to a built-in mapping of common ports when the system lookup
    fails, and returns ``"unknown"`` if the port is not recognised by either.

    Args:
        port: Port number to look up. Expected range is 0-65535.

    Returns:
        Lowercase service name (e.g. ``"http"``, ``"ssh"``), or
        ``"unknown"`` when the port is not recognised.

    Examples:
        >>> get_service_on_port(80)
        'http'
        >>> get_service_on_port(22)
        'ssh'
        >>> get_service_on_port(9999)
        'unknown'

    """
    try:
        return getservbyport(port)
    except (OSError, OverflowError, TypeError):
        return _FALLBACK_SERVICES.get(port, "unknown")
