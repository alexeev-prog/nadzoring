from socket import getservbyport


def get_service_on_port(port: int) -> str:
    """
    Get the service name associated with a given port number.

    Attempts to determine the standard service name (e.g., 'http', 'https', 'ssh')
    for the specified port number using the system's service database.

    Args:
        port (int): The port number to look up. Must be in range 0-65535.

    Returns:
        str: The service name if found, otherwise returns "Unknown".
             Service names are typically lowercase strings like 'http', 'ssh', etc.

    Examples:
        >>> get_service_on_port(80)
        'http'
        >>> get_service_on_port(22)
        'ssh'
        >>> get_service_on_port(9999)
        'Unknown'

    Notes:
        This function wraps socket.getservbyport() and handles any exceptions
        gracefully by returning "Unknown" instead of raising errors.
        The service mapping depends on the local system's /etc/services file
        or equivalent.
    """
    try:
        return getservbyport(port)
    except (OSError, OverflowError, TypeError):
        return "Unknown"
