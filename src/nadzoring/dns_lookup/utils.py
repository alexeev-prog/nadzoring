"""
Utility functions for the DNS lookup module.

This module provides the low-level building blocks used by the rest of
``nadzoring.dns_lookup``:

- :func:`create_resolver` — build a configured ``dnspython`` resolver
- :func:`extract_records` — format raw resolver answers into strings
- :func:`resolve_with_timer` — single-query entry point with timing and
  structured error handling
- :func:`get_public_dns_servers` — return the built-in list of well-known
  public resolvers

None of the functions in this module raise on DNS errors; all failures are
surfaced through the ``"error"`` field of the returned :class:`~.types.DNSResult`
dict.  Callers that prefer exceptions should wrap the result themselves or
use :mod:`nadzoring.utils.errors`.
"""

from collections.abc import Callable
from logging import Logger
from time import time

import dns.asyncresolver
import dns.exception
import dns.resolver
from dns.asyncresolver import Resolver as AsyncResolver
from dns.resolver import Answer, Resolver

from nadzoring.dns_lookup.types import DNSResult, RecordType
from nadzoring.logger import get_logger
from nadzoring.utils.timeout import (
    OperationTimeoutError,
    TimeoutConfig,
    timeout_context,
)

logger: Logger = get_logger(__name__)

_DEFAULT_TIMEOUT: float = 5.0
_DEFAULT_LIFETIME: float = 10.0

_PUBLIC_DNS_SERVERS: list[str] = [
    "8.8.8.8",  # Google
    "8.8.4.4",  # Google
    "1.1.1.1",  # Cloudflare
    "1.0.0.1",  # Cloudflare
    "208.67.222.222",  # OpenDNS
    "208.67.220.220",  # OpenDNS
    "9.9.9.9",  # Quad9
    "149.112.112.112",  # Quad9
    "64.6.64.6",  # Verisign
    "64.6.65.6",  # Verisign
]


def create_resolver(
    nameserver: str | None = None,
    timeout_config: TimeoutConfig | None = None,
) -> Resolver:
    """
    Create and configure a ``dnspython`` resolver instance.

    Args:
        nameserver: Optional nameserver IP address.  When ``None`` the
            system default resolvers are used.
        timeout_config: Unified timeout configuration. When ``None`` uses default.

    Returns:
        Configured :class:`dns.resolver.Resolver` ready for queries.

    Examples:
        >>> resolver = create_resolver("8.8.8.8", timeout_config)
        >>> answers = resolver.resolve("example.com", "A")

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig(connect=5.0, read=5.0, lifetime=10.0)

    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout_config.read
    resolver.lifetime = timeout_config.lifetime

    if nameserver:
        resolver.nameservers = [nameserver]
    return resolver


def create_async_resolver(
    nameserver: str | None = None,
    timeout_config: TimeoutConfig | None = None,
) -> AsyncResolver:
    """
    Create and configure an async ``dnspython`` resolver instance.

    Args:
        nameserver: Optional nameserver IP address. When ``None`` the
            system default resolvers are used.
        timeout_config: Unified timeout configuration. When ``None`` uses default.

    Returns:
        Configured :class:`dns.asyncresolver.Resolver` ready for async queries.

    Examples:
        >>> import asyncio
        >>> async def _run() -> None:
        ...     resolver = create_async_resolver("8.8.8.8", timeout_config)
        ...     answers = await resolver.resolve("example.com", "A")
        ...     print(len(answers) > 0)
        >>> asyncio.run(_run())
        True

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig(connect=5.0, read=5.0, lifetime=10.0)

    resolver = dns.asyncresolver.Resolver()
    resolver.timeout = timeout_config.read
    resolver.lifetime = timeout_config.lifetime
    if nameserver:
        resolver.nameservers = [nameserver]
    return resolver


def _extract_mx_records(answers: Answer) -> list[str]:
    """Extract and format MX records from a resolver answer."""
    return [f"{answer.preference} {str(answer.exchange).rstrip('.')}" for answer in answers]


def _extract_txt_records(answers: Answer) -> list[str]:
    """Extract and format TXT records, joining multi-part strings."""
    records: list[str] = []
    for answer in answers:
        parts: list[str] = [part.decode("utf-8") if isinstance(part, bytes) else str(part) for part in answer.strings]
        records.append("".join(parts))
    return records


def _extract_soa_records(answers: Answer) -> list[str]:
    """Extract and format SOA records into a single space-joined string."""
    return [
        (f"{soa.mname} {soa.rname} {soa.serial} {soa.refresh} {soa.retry} {soa.expire} {soa.minimum}")
        for soa in answers
    ]


def _extract_default_records(answers: Answer) -> list[str]:
    """Extract generic DNS records, stripping trailing dots."""
    return [str(answer).rstrip(".") for answer in answers]


_EXTRACTORS: dict[str, Callable[[Answer], list[str]]] = {
    "MX": _extract_mx_records,
    "TXT": _extract_txt_records,
    "SOA": _extract_soa_records,
}


def extract_records(answers: Answer, record_type: str) -> list[str]:
    """
    Extract and format DNS records from a resolver answer.

    Applies record-type-specific formatting:

    - **MX** — ``"priority mailserver"``
    - **TXT** — all string parts joined into one string
    - **SOA** — space-joined SOA fields
    - **other** — plain ``str()`` with trailing dot stripped

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
    extractor: Callable[[Answer], list[str]] = _EXTRACTORS.get(record_type, _extract_default_records)
    return extractor(answers)


def _make_empty_result(
    domain: str,
    record_type: RecordType,
) -> DNSResult:
    """Return a zeroed :class:`~.types.DNSResult` dict."""
    return {
        "domain": domain,
        "record_type": record_type,
        "records": [],
        "ttl": None,
        "error": None,
        "response_time": None,
    }


def resolve_with_timer(
    domain: str,
    record_type: RecordType = "A",
    nameserver: str | None = None,
    timeout_config: TimeoutConfig | None = None,
    *,
    include_ttl: bool = False,
) -> DNSResult:
    """
    Perform DNS resolution with timing and structured error handling.

    Resolves *domain* for *record_type*, measuring response time and
    optionally capturing TTL.  All DNS errors are surfaced through the
    ``"error"`` field rather than raised as exceptions, making this safe
    to call in automated scripts without try/except.

    Args:
        domain: Domain name to resolve (e.g. ``"example.com"``).
        record_type: DNS record type to query.  Defaults to ``"A"``.
        timeout_config: Unified timeout configuration.
        nameserver: Optional nameserver IP; ``None`` uses the system
            default.
        include_ttl: Include TTL value in result.  Defaults to
            ``False``.

    Returns:
        :class:`~.types.DNSResult` dict.  Always check
        ``result["error"]`` before using ``result["records"]``::

            result = resolve_with_timer("example.com", "A")
            if result["error"]:
                # Possible values:
                # "Domain does not exist"  — NXDOMAIN
                # "No A records"           — NoAnswer
                # "Query timeout"          — Timeout
                # <arbitrary string>       — unexpected error
                print("DNS error:", result["error"])
            else:
                print(result["records"])  # ['93.184.216.34']
                print(result["response_time"])  # e.g. 42.5

    Examples:
        Basic A record lookup::

            result = resolve_with_timer("example.com")
            if not result["error"]:
                print(result["records"])

        MX lookup with TTL::

            result = resolve_with_timer("example.com", "MX", include_ttl=True)
            if not result["error"]:
                print(result["records"], result["ttl"])

        Using a custom nameserver::

            result = resolve_with_timer("example.com", nameserver="1.1.1.1")

    """
    result: DNSResult = _make_empty_result(domain, record_type)

    if timeout_config is None:
        timeout_config = TimeoutConfig(connect=5.0, read=5.0, lifetime=10.0)

    try:
        with timeout_context(timeout_config):
            try:
                resolver: Resolver = create_resolver(nameserver, timeout_config)
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
    except OperationTimeoutError:
        result["error"] = "Operation exceeded lifetime timeout"

    return result


async def resolve_with_timer_async(
    domain: str,
    record_type: RecordType = "A",
    nameserver: str | None = None,
    *,
    include_ttl: bool = False,
    timeout_config: TimeoutConfig | None = None,
) -> DNSResult:
    """
    Async variant of :func:`resolve_with_timer` with identical output shape.

    Args:
        domain: Domain name to resolve (e.g. ``"example.com"``).
        record_type: DNS record type to query. Defaults to ``"A"``.
        nameserver: Optional nameserver IP; ``None`` uses the system
            default.
        include_ttl: Include TTL value in result. Defaults to
            ``False``.
        timeout_config: Unified timeout configuration. If None, uses default.

    Returns:
        :class:`~.types.DNSResult` dict using the same keys and error
        semantics as :func:`resolve_with_timer`.

    Examples:
        Basic A record lookup::

            import asyncio


            async def _run() -> None:
                result = await resolve_with_timer_async("example.com")
                if not result["error"]:
                    print(result["records"])


            asyncio.run(_run())

        Using a custom nameserver::

            import asyncio


            async def _run() -> None:
                result = await resolve_with_timer_async(
                    "example.com",
                    nameserver="1.1.1.1",
                )
                print(result["response_time"])


            asyncio.run(_run())

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig(connect=5.0, read=5.0, lifetime=10.0)

    result: DNSResult = _make_empty_result(domain, record_type)

    try:
        resolver: AsyncResolver = create_async_resolver(nameserver, timeout_config)
        start_time: float = time()
        answers: Answer = await resolver.resolve(domain, record_type)
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

    Includes resolvers from Google, Cloudflare, OpenDNS, Quad9, and
    Verisign.

    Returns:
        A new list of DNS server IP address strings (copy of internal
        constant, safe to mutate).

    Examples:
        >>> servers = get_public_dns_servers()
        >>> "8.8.8.8" in servers
        True
        >>> "1.1.1.1" in servers
        True

    """
    return list(_PUBLIC_DNS_SERVERS)
