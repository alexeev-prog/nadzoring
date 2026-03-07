"""
Reverse DNS lookup: IP address → hostname (PTR record).

Typical usage::

    from nadzoring.dns_lookup.reverse import reverse_dns

    result = reverse_dns("8.8.8.8")
    if result["error"]:
        print("Lookup failed:", result["error"])
    else:
        print("Hostname:", result["hostname"])
        print("RTT:", result["response_time"], "ms")

"""

from logging import Logger
from time import time

import dns.exception
import dns.resolver
import dns.reversename
from dns.name import Name
from dns.resolver import Answer, Resolver

from nadzoring.dns_lookup.utils import create_resolver
from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def _make_result(ip_address: str) -> dict[str, str | float | None]:
    """Return a zeroed reverse-lookup result dict."""
    return {
        "ip_address": ip_address,
        "hostname": None,
        "error": None,
        "response_time": None,
    }


def reverse_dns(
    ip_address: str,
    nameserver: str | None = None,
) -> dict[str, str | float | None]:
    """
    Perform a reverse DNS lookup to resolve an IP address to a hostname.

    Queries the PTR record for *ip_address* using
    :func:`dns.reversename.from_address` for automatic ``in-addr.arpa`` /
    ``ip6.arpa`` name construction.  Both IPv4 and IPv6 are supported.

    The function never raises; all failures are returned in the ``"error"``
    field so that callers can handle them uniformly::

        result = reverse_dns("192.168.1.1")
        hostname = result["hostname"] or f"[{result['error']}]"

    Args:
        ip_address: IPv4 or IPv6 address to look up (e.g. ``"8.8.8.8"``).
        nameserver: Optional nameserver IP address.  ``None`` uses the
            system default resolvers.

    Returns:
        Dict with the following keys:

        ``ip_address``
            The original address queried (always present).
        ``hostname``
            Resolved hostname with trailing dot stripped, or ``None``
            when the lookup failed.
        ``error``
            Error message string on failure; ``None`` on success.
            Possible values:

            - ``"No PTR record"`` — the IP has no reverse entry
            - ``"No reverse DNS"`` — NXDOMAIN on the reverse zone
            - ``"Query timeout"`` — resolver timed out
            - ``"Invalid IP address: …"`` — *ip_address* is malformed
            - arbitrary string — unexpected resolver error

        ``response_time``
            Query round-trip time in milliseconds (2 d.p.), or ``None``
            when the query timed out.

    Examples:
        Successful lookup::

            result = reverse_dns("8.8.8.8")
            assert result["hostname"] == "dns.google"
            assert result["error"] is None

        Missing PTR record::

            result = reverse_dns("192.168.1.1")
            assert result["hostname"] is None
            assert result["error"] == "No PTR record"

        IPv6 address::

            result = reverse_dns("2001:4860:4860::8888")
            print(result["hostname"])  # dns.google

        Using a custom nameserver::

            result = reverse_dns("8.8.8.8", nameserver="1.1.1.1")

    """
    result = _make_result(ip_address)

    try:
        resolver: Resolver = create_resolver(nameserver)
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
