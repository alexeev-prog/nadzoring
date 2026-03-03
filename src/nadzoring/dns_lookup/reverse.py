"""Reverse DNS lookup functionality for IP address to hostname resolution."""

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

    Queries the PTR (Pointer) record for a given IP address to find the
    associated domain name. This is the reverse of a forward DNS lookup.

    Args:
        ip_address: IPv4 or IPv6 address to look up (e.g., "8.8.8.8" or
                   "2001:4860:4860::8888").
        nameserver: Optional specific nameserver IP address to use for the
                   query. If None, uses the system default resolvers.

    Returns:
        Dict[str, Union[str, float, None]]: A dictionary containing:
            - ip_address (str): The original IP address that was queried.
            - hostname (Optional[str]): The resolved hostname if found,
              with trailing dot removed. None if resolution failed.
            - error (Optional[str]): Error message if lookup failed,
              None for successful lookups.
            - response_time (Optional[float]): Query response time in
              milliseconds, rounded to 2 decimal places. None if the
              query failed before timing could be recorded.

    Examples:
        >>> # Successful reverse lookup
        >>> result = reverse_dns("8.8.8.8")
        >>> print(result["hostname"])
        'dns.google'
        >>> print(f"Resolved in {result['response_time']}ms")

        >>> # Failed reverse lookup
        >>> result = reverse_dns("192.168.1.1")
        >>> print(result["error"])
        'No PTR record'

        >>> # Using specific nameserver
        >>> result = reverse_dns("1.1.1.1", nameserver="9.9.9.9")

    Notes:
        - The function handles both IPv4 and IPv6 addresses automatically
          using dns.reversename.from_address().
        - Common errors include:
            - "No PTR record": IP exists but has no reverse DNS configured
            - "No reverse DNS": IP range has no reverse delegation
            - "Query timeout": DNS server didn't respond in time
        - Trailing dots are automatically removed from hostnames for
          consistency with forward lookup formats.
        - Debug logs are generated for failed lookups to aid troubleshooting.

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
    except Exception as e:
        result["error"] = str(e)
        logger.debug("Reverse DNS failed for %s: %s", ip_address, e)

    return result
