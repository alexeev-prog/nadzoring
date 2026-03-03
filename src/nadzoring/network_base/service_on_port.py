"""Service name resolution for port numbers."""

from socket import getservbyport


def get_service_on_port(port: int) -> str:
    """
    Get the service name associated with a given port number.

    Attempts to determine the standard service name (e.g., 'http', 'https', 'ssh')
    for the specified port number using the system's service database.

    Args:
        port: The port number to look up. Must be in range 0-65535.

    Returns:
        The service name if found, otherwise returns "unknown".
        Service names are typically lowercase strings like 'http', 'ssh', etc.

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
        common_services: dict[int, str] = {
            80: "http",
            443: "https",
            22: "ssh",
            21: "ftp",
            25: "smtp",
            53: "dns",
            110: "pop3",
            143: "imap",
            993: "imaps",
            995: "pop3s",
            3306: "mysql",
            5432: "postgresql",
            6379: "redis",
            27017: "mongodb",
            8080: "http-alt",
            8443: "https-alt",
        }
        return common_services.get(port, "Unknown")
