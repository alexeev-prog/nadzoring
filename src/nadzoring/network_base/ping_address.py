"""
This script performs a standard ping of a specific address or domain name.
It works in the same way as the standard OS module. It does not ping addresses that
are protected from pinging, such as "codeby.net".
It can be used for a shallow check of addresses.
"""

from ipaddress import IPv4Address
from logging import Logger

from ping3 import ping

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def ping_addr(addr: str) -> bool:
    """A normal ping of a specific ip address or domain.

    The original function returns if the domain or address is unavailable None.
    If successful, the time for which ping is being performed.
    This function returns Boolean values in the case of
    success or failure.

    Args:
        addr (str): address

    Returns:
        bool: is pinged
    """
    try:
        IPv4Address(addr)
    except Exception:
        if addr.startswith("http"):
            addr = addr.split("/")[2]
            if len(addr.split(".")) > 2:
                addr = ".".join(addr.split(".")[1:])

    try:
        return ping(addr) is not None
    except Exception:
        logger.exception("Raised exception when ping address")
        return False
