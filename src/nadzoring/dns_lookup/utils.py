"""Utility functions for DNS lookup module."""

from logging import Logger
from time import time

import dns.exception
import dns.name
import dns.resolver
import dns.reversename
from dns.resolver import Answer, Resolver

from nadzoring.dns_lookup.types import DNSResult, RecordType
from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

_PUBLIC_DNS_SERVERS: list[str] = [
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1",
    "1.0.0.1",
    "208.67.222.222",
    "208.67.220.220",
    "9.9.9.9",
    "149.112.112.112",
    "64.6.64.6",
    "64.6.65.6",
]


def create_resolver(
    nameserver: str | None = None,
    timeout: float = 5.0,
    lifetime: float = 10.0,
) -> Resolver:
    """
    Create and configure a DNS resolver instance.

    Args:
        nameserver: Optional nameserver IP address. When ``None`` the system
            default resolvers are used.
        timeout: Per-nameserver query timeout in seconds. Defaults to ``5.0``.
        lifetime: Total query lifetime in seconds, including retries across
            nameservers. Defaults to ``10.0``.

    Returns:
        Configured :class:`dns.resolver.Resolver` ready for queries.

    Examples:
        >>> resolver = create_resolver("8.8.8.8", timeout=3.0, lifetime=8.0)
        >>> answers = resolver.resolve("example.com", "A")

    """
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = lifetime
    if nameserver:
        resolver.nameservers = [nameserver]
    return resolver


def extract_records(answers: Answer, record_type: str) -> list[str]:
    """
    Extract and format DNS records from a resolver answer.

    Applies record-type-specific formatting:

    * **MX** — ``"priority mailserver"``
    * **TXT** — all string parts joined into one string
    * **SOA** — space-joined SOA fields
    * **other** — plain ``str()`` with trailing dot stripped

    Args:
        answers: :class:`dns.resolver.Answer` returned by
            :meth:`Resolver.resolve`.
        record_type: DNS record type string (e.g. ``"A"``, ``"MX"``).

    Returns:
        List of formatted record strings.

    Examples:
        >>> answers = resolver.resolve("example.com", "MX")
        >>> extract_records(answers, "MX")
        ['10 mail.example.com', '20 backup.example.com']

    """
    records: list[str] = []

    for answer in answers:
        if record_type == "MX":
            records.append(f"{answer.preference} {answer.exchange}".rstrip("."))
        elif record_type == "TXT":
            txt_parts: list[str] = [
                part.decode("utf-8") if isinstance(part, bytes) else str(part)
                for part in answer.strings
            ]
            records.append("".join(txt_parts))
        elif record_type == "SOA":
            soa = answer
            records.append(
                f"{soa.mname} {soa.rname} {soa.serial} {soa.refresh} "
                f"{soa.retry} {soa.expire} {soa.minimum}",
            )
        else:
            records.append(str(answer).rstrip("."))

    return records


def resolve_with_timer(
    domain: str,
    record_type: RecordType = "A",
    nameserver: str | None = None,
    *,
    include_ttl: bool = False,
    timeout: float = 5.0,
    lifetime: float = 10.0,
) -> DNSResult:
    """
    Perform DNS resolution with timing and structured error handling.

    Resolves *domain* for *record_type*, measuring response time and optionally
    capturing TTL. All DNS errors are surfaced through the ``error`` field rather
    than raised.

    Args:
        domain: Domain name to resolve (e.g. ``"example.com"``).
        record_type: DNS record type to query. Defaults to ``"A"``.
        nameserver: Optional nameserver IP; ``None`` uses the system default.
        include_ttl: Include TTL value in result. Defaults to ``False``.
        timeout: Per-nameserver query timeout in seconds. Defaults to ``5.0``.
        lifetime: Total query lifetime in seconds. Defaults to ``10.0``.

    Returns:
        :class:`DNSResult` dict with ``domain``, ``record_type``, ``records``,
        ``ttl``, ``error``, and ``response_time`` keys.

    Examples:
        >>> result = resolve_with_timer("example.com", "MX", include_ttl=True)
        >>> if not result["error"]:
        ...     print(result["records"], result["ttl"])

    """
    result: DNSResult = {
        "domain": domain,
        "record_type": record_type,
        "records": [],
        "ttl": None,
        "error": None,
        "response_time": None,
    }

    try:
        resolver: Resolver = create_resolver(nameserver, timeout, lifetime)
        start_time: float = time()
        answers: Answer = resolver.resolve(domain, record_type)
        result["response_time"] = round((time() - start_time) * 1000, 2)

        if answers.rrset and include_ttl:
            result["ttl"] = answers.rrset.ttl

        result["records"] = extract_records(answers, record_type)

    except dns.resolver.NoAnswer:
        result["error"] = f"No {record_type} records"
    except dns.resolver.NXDOMAIN:
        result["error"] = "Domain does not exist"
    except dns.exception.Timeout:
        result["error"] = "Query timeout"
        logger.debug("DNS query timeout for %s %s", domain, record_type)
    except Exception as exc:
        result["error"] = str(exc)
        logger.debug("DNS resolution failed for %s %s: %s", domain, record_type, exc)

    return result


def get_public_dns_servers() -> list[str]:
    """
    Return a list of well-known public DNS server IP addresses.

    Includes resolvers from Google, Cloudflare, OpenDNS, Quad9, and Verisign.

    Returns:
        List of DNS server IP address strings.

    Examples:
        >>> servers = get_public_dns_servers()
        >>> "8.8.8.8" in servers
        True

    """
    return list(_PUBLIC_DNS_SERVERS)
