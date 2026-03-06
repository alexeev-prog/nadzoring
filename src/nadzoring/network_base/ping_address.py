"""ICMP ping utility using the ping3 library."""

from logging import Logger

from ping3 import ping

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def _normalize_address(addr: str) -> str:
    """
    Normalise a raw address or URL into a bare hostname / IP string.

    Strips ``http://`` and ``https://`` scheme prefixes and removes any
    leading ``www.`` subdomain so that ``ping3`` receives a plain hostname.

    Args:
        addr: Raw address, URL, or hostname to normalise.

    Returns:
        Bare hostname or IP address string.

    """
    if addr.startswith(("http://", "https://")):
        host = addr.split("//", 1)[1].split("/")[0]
    else:
        host = addr

    parts = host.split(".")
    if len(parts) > 2 and parts[0] == "www":
        host = ".".join(parts[1:])

    return host


def ping_addr(addr: str) -> bool:
    """
    Check reachability of an IP address or hostname using ICMP ping.

    Normalises URLs before pinging so that values like
    ``https://example.com`` are handled transparently.

    Note:
        Some hosts block ICMP requests and will always return ``False``
        regardless of their actual availability.

    Args:
        addr: IP address, hostname, or URL to ping.

    Returns:
        ``True`` if the host replied within the default timeout,
        ``False`` otherwise (unreachable, blocked, or error).

    """
    target = _normalize_address(addr)

    try:
        return ping(target) is not None
    except Exception:
        logger.exception("Unexpected error while pinging %s", target)
        return False
