# nadzoring/dns_lookup/utils.py
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
    """Create and configure DNS resolver."""
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = lifetime
    if nameserver:
        resolver.nameservers = [nameserver]
    return resolver


def extract_records(answers: Answer, record_type: str) -> list[str]:
    """Extract records from DNS answer."""
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
    """Resolve DNS with timing information."""
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
    """Get list of public DNS servers for testing."""
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
