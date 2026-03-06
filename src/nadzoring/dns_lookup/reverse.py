"""Reverse DNS lookup functionality for IP-address-to-hostname resolution."""

from logging import Logger
from time import time

import dns.exception
import dns.resolver
import dns.reversename
from dns.name import Name
from dns.resolver import Answer

from nadzoring.dns_lookup.utils import create_resolver
from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def reverse_dns(
    ip_address: str,
    nameserver: str | None = None,
) -> dict[str, str | float | None]:
    """
    Perform a reverse DNS lookup to resolve an IP address to a hostname.

    Queries the PTR record for *ip_address* using
    :func:`dns.reversename.from_address` for automatic in-addr.arpa /
    ip6.arpa name construction.

    Args:
        ip_address: IPv4 or IPv6 address to look up (e.g. ``"8.8.8.8"``).
        nameserver: Optional nameserver IP. ``None`` uses the system default.

    Returns:
        Dict with the following keys:

        * ``ip_address`` — the original address queried
        * ``hostname`` — resolved hostname (trailing dot stripped), or
          ``None`` if lookup failed
        * ``error`` — error message string on failure, ``None`` on success
        * ``response_time`` — query time in milliseconds (2 d.p.), or
          ``None`` when the query timed out

    Examples:
        >>> result = reverse_dns("8.8.8.8")
        >>> result["hostname"]
        'dns.google'

        >>> result = reverse_dns("192.168.1.1")
        >>> result["error"]
        'No PTR record'

    """
    result: dict[str, str | float | None] = {
        "ip_address": ip_address,
        "hostname": None,
        "error": None,
        "response_time": None,
    }

    try:
        resolver = create_resolver(nameserver)
        reverse_name: Name = dns.reversename.from_address(ip_address)
        start_time: float = time()
        answers: Answer = resolver.resolve(reverse_name, "PTR")
        result["response_time"] = round((time() - start_time) * 1000, 2)

        if answers:
            result["hostname"] = str(answers[0]).rstrip(".")

    except dns.resolver.NoAnswer:
        result["error"] = "No PTR record"
    except dns.resolver.NXDOMAIN:
        result["error"] = "No reverse DNS"
    except dns.exception.Timeout:
        result["error"] = "Query timeout"
        logger.debug("Reverse DNS timeout for %s", ip_address)
    except ValueError as exc:
        result["error"] = f"Invalid IP address: {exc}"
        logger.debug("Invalid IP for reverse lookup: %s", ip_address)
    except Exception as exc:
        result["error"] = str(exc)
        logger.debug("Reverse DNS failed for %s: %s", ip_address, exc)

    return result
