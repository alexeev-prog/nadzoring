"""Comprehensive domain information aggregation."""

import contextlib
import socket
from logging import Logger
from socket import AddressFamily, SocketKind
from typing import Any

import dns.resolver
from dns.resolver import Answer

from nadzoring.logger import get_logger
from nadzoring.network_base.geolocation_ip import geo_ip
from nadzoring.network_base.whois_lookup import whois_lookup

logger: Logger = get_logger(__name__)

type _AddrInfo = list[tuple[AddressFamily, SocketKind, int, str, tuple[Any, ...]]]


def _resolve_domain(domain: str) -> dict[str, str | None]:
    """
    Resolve a domain to its IP addresses.

    Args:
        domain: The domain name to resolve.

    Returns:
        Dictionary with keys ``ipv4`` (str or None) and
        ``ipv6`` (str or None).

    """
    result: dict[str, str | None] = {"ipv4": None, "ipv6": None}
    try:
        info: _AddrInfo = socket.getaddrinfo(domain, None)
        for family, _, _, _, sockaddr in info:
            if family == socket.AF_INET and result["ipv4"] is None:
                result["ipv4"] = str(sockaddr[0])
            elif family == socket.AF_INET6 and result["ipv6"] is None:
                result["ipv6"] = str(sockaddr[0])
    except socket.gaierror:
        logger.warning("Failed to resolve domain: %s", domain)
    return result


def _get_dns_records(domain: str) -> dict[str, list[str]]:
    """
    Retrieve basic DNS records for a domain.

    Attempts to resolve A, AAAA, MX, NS, and TXT records using the
    system resolver via :mod:`socket` and :mod:`subprocess` fallbacks
    where available.

    Args:
        domain: The domain to query.

    Returns:
        Dictionary mapping record type strings to lists of record values.
        Missing record types are omitted.

    """
    records: dict[str, list[str]] = {}

    for rtype in ("A", "AAAA", "MX", "NS", "TXT"):
        try:
            answers: Answer = dns.resolver.resolve(domain, rtype, lifetime=5)
            records[rtype] = [str(r) for r in answers]
        except Exception:
            logger.exception("Raised exception when get dns records")

    if "A" not in records:
        try:
            a_records: _AddrInfo = socket.getaddrinfo(domain, None, socket.AF_INET)
            if a_records:
                records["A"] = list({str(s[4][0]) for s in a_records})
        except socket.gaierror:
            pass

    if "AAAA" not in records:
        try:
            aaaa_records: _AddrInfo = socket.getaddrinfo(domain, None, socket.AF_INET6)
            if aaaa_records:
                records["AAAA"] = list({str(s[4][0]) for s in aaaa_records})
        except socket.gaierror:
            pass

    return records


def get_domain_info(domain: str) -> dict[str, Any]:
    """
    Retrieve comprehensive information about a domain.

    Aggregates WHOIS registration data, DNS records, IP geolocation,
    and reverse DNS for the resolved IP address into a single structured
    response.

    Args:
        domain: The domain name to investigate (e.g. ``"example.com"``).

    Returns:
        Dictionary with the following top-level keys:

        - ``domain`` (str): The queried domain.
        - ``whois`` (dict): Parsed WHOIS fields; contains ``error`` key
          on failure.
        - ``dns`` (dict): Resolved IP addresses under ``ipv4``/``ipv6``
          and DNS record lists by type.
        - ``geolocation`` (dict): Geographic data for the resolved IP
          (``lat``, ``lon``, ``country``, ``city``), or empty dict on
          failure.
        - ``reverse_dns`` (str | None): Reverse DNS hostname for the
          primary IPv4 address, or ``None`` if unavailable.

    Examples:
        >>> info = get_domain_info("example.com")
        >>> info["whois"]["registrar"]
        'RESERVED-Internet Assigned Numbers Authority'
        >>> info["geolocation"]["country"]
        'United States'

    """
    whois_data: dict[str, str | None] = whois_lookup(domain)
    resolved: dict[str, str | None] = _resolve_domain(domain)
    dns_records: dict[str, list[str]] = _get_dns_records(domain)

    primary_ip: str | None = resolved.get("ipv4")
    geo: dict[str, str] = geo_ip(primary_ip) if primary_ip else {}

    reverse_dns: str | None = None
    if primary_ip:
        with contextlib.suppress(socket.herror, socket.gaierror):
            reverse_dns = socket.gethostbyaddr(primary_ip)[0]

    return {
        "domain": domain,
        "whois": whois_data,
        "dns": {
            "ipv4": resolved["ipv4"],
            "ipv6": resolved["ipv6"],
            "records": dns_records,
        },
        "geolocation": geo,
        "reverse_dns": reverse_dns,
    }
