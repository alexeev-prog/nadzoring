"""
Returns the default router(gateway) ip address on Linux and Windows machines.

On some Linux machines, it requires the net-tools package to be installed, as the
`route` command does not work without it (example: Ubuntu):
 $ sudo apt install net-tools
"""

from ipaddress import IPv4Address, IPv6Address
from logging import Logger
from platform import system
from socket import gethostbyname
from subprocess import check_output

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def get_ip_from_host(hostname: str) -> str:
    """Attempts to retrieve an IP address from a domain name.

    If unsuccessful, returns the value passed to the function.

    Args:
        hostname (str): hostname address

    Returns:
        str: host
    """
    try:
        sock: str = gethostbyname(hostname)
    except Exception:
        return hostname
    else:
        return sock


def check_ipv4(hostname: str) -> str:
    """Checking whether the received value is an ip address.

    If the received value is not an ip address, an exception is thrown and the received
    value is passed to the function to obtain the address from the domain name. If the
    check is successful, the address is returned from the function.

    Args:
        ip (str): hostname address

    Returns:
        str: hostname
    """
    try:
        IPv4Address(hostname)
    except Exception:
        return get_ip_from_host(hostname)
    else:
        return hostname


def check_ipv6(hostname: str) -> str:
    """Checking whether the received value is an ip address.

    If the received value is not an ip address, an exception is thrown and the received
    value is passed to the function to obtain the address from the domain name. If the
    check is successful, the address is returned from the function.

    Args:
        ip (str): hostname address

    Returns:
        str: hostname
    """
    try:
        IPv6Address(hostname)
    except Exception:
        return get_ip_from_host(hostname)
    else:
        return hostname


def router_ip(*, ipv6: bool = False) -> str | None:
    """The OS version is determined, then, using the subprocess library,
    a command specific to each OS is executed to determine the router address.

    Then the received value is sent to check if it matches the address. If the received
    address is IPv4, it is returned from the function.
    If the address is a domain name, and there may be such cases,
    the received name is passed to the function where the attempt is performed.
    getting an ip address by domain name. For example, if the system
    uses pfsence.

    Args:
        ipv6 (bool, optional): use IPv6 instead of IPv4. Defaults to False.

    Returns:
        str | None: ip route result or None
    """

    if system() == "Linux":
        try:
            ip_route: str = str(
                check_output("route -n | grep UG", shell=True).decode().split()[1]  # noqa: S602, S607
            )
            return check_ipv4(ip_route) if not ipv6 else check_ipv6(ip_route)
        except Exception:
            logger.exception("Raised exception when router IP for Linux")
            return None
    elif system() == "Windows":
        try:
            ip_route: str = (
                check_output("route PRINT 0* -4 | findstr 0.0.0.0", shell=True)  # noqa: S602, S607
                .decode("cp866")
                .split()[-3]
            )
            return check_ipv4(ip_route) if not ipv6 else check_ipv6(ip_route)
        except Exception:
            logger.exception("Raised exception when router IP for Windows")
            return None
    else:
        logger.warning("System does not supported", extra=system())
    return None
