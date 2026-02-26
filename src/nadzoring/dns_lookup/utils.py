"""Utility functions for DNS lookup module."""

from time import time

import dns.exception
import dns.name
import dns.resolver
import dns.reversename
from dns.resolver import Answer, Resolver

from nadzoring.dns_lookup.types import DNSResult, RecordType
from nadzoring.logger import get_logger

logger = get_logger(__name__)


def create_resolver(
    nameserver: str | None = None,
    timeout: float = 5.0,
    lifetime: float = 10.0,
) -> Resolver:
    """
    Create and configure a DNS resolver instance.

    Initializes a DNS resolver with specified timeout parameters and optional
    custom nameserver.

    Args:
        nameserver: Optional specific nameserver IP address to use for queries.
                   If None, uses system default nameservers.
        timeout: Query timeout in seconds for each individual nameserver.
                Defaults to 5.0 seconds.
        lifetime: Total lifetime in seconds for the entire query operation.
                 This includes retries across multiple nameservers.
                 Defaults to 10.0 seconds.

    Returns:
        Resolver: Configured dns.resolver.Resolver instance ready for queries.

    Example:
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
    Extract and format DNS records from a resolution answer.

    Processes DNS answers based on record type, handling special formatting
    for complex record types like MX, TXT, and SOA.

    Args:
        answers: DNS answer object from resolver.resolve() containing the
                resolved records.
        record_type: Type of DNS record being processed (e.g., 'A', 'MX', 'TXT').
                    Used to determine special formatting rules.

    Returns:
        List[str]: List of formatted record strings. Format varies by record type:
            - MX: "priority mailserver" (e.g., "10 mail.example.com")
            - TXT: Concatenated string parts (e.g., "v=spf1 include:...")
            - SOA: fields: "mname rname serial refresh retry expire minimum"
            - Others: Simple string representation with trailing dots removed

    Example:
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
    Perform DNS resolution with timing information and error handling.

    Resolves a domain name for a specific record type, measuring response time
    and optionally capturing TTL information. Handles common DNS errors gracefully.

    Args:
        domain: Domain name to resolve (e.g., "example.com").
        record_type: DNS record type to query (e.g., "A", "MX", "TXT").
                    Defaults to "A".
        nameserver: Optional specific nameserver IP to use for resolution.
                   If None, uses system default.
        include_ttl: Whether to include TTL (Time To Live) value in result.
                    Defaults to False.
        timeout: Query timeout in seconds for each nameserver.
                Defaults to 5.0.
        lifetime: Total query lifetime in seconds, including retries.
                 Defaults to 10.0.

    Returns:
        DNSResult: Dictionary containing resolution results with structure:
            - domain: The queried domain name
            - record_type: The queried record type
            - records: List of resolved records (empty if resolution failed)
            - ttl: TTL in seconds if include_ttl=True and available, else None
            - error: Error message string if resolution failed, else None
            - response_time: Query response time in milliseconds, rounded to 2 decimals

    Example:
        >>> result = resolve_with_timer("example.com", "MX", include_ttl=True)
        >>> if not result["error"]:
        ...     print(f"Records: {result['records']}, TTL: {result['ttl']}")
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
        resolver = create_resolver(nameserver, timeout, lifetime)
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
        logger.debug("DNS query timeout for %s", domain)
    except Exception as e:
        result["error"] = str(e)
        logger.debug("DNS resolution failed for %s: %s", domain, e)

    return result


def get_public_dns_servers() -> list[str]:
    """
    Get a list of well-known public DNS server IP addresses.

    Returns a curated list of reliable public DNS resolvers from various providers
    suitable for testing or fallback scenarios.

    Returns:
        List[str]: List of DNS server IP addresses including:
            - Google Public DNS (8.8.8.8, 8.8.4.4)
            - Cloudflare DNS (1.1.1.1, 1.0.0.1)
            - OpenDNS (208.67.222.222, 208.67.220.220)
            - Quad9 (9.9.9.9, 149.112.112.112)
            - Verisign Public DNS (64.6.64.6, 64.6.65.6)

    Example:
        >>> servers = get_public_dns_servers()
        >>> for server in servers[:3]:
        ...     print(f"Testing DNS server: {server}")
    """
    return [
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
