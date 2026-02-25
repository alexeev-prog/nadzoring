# nadzoring/dns_lookup/types.py
"""Type definitions for DNS lookup module."""

from typing import Any, Literal, TypedDict

RecordType = Literal["A", "AAAA", "CNAME", "MX", "NS", "TXT", "PTR", "SOA", "DNSKEY"]
RECORD_TYPES: list[str] = [
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "NS",
    "TXT",
    "PTR",
    "SOA",
    "DNSKEY",
]


class DNSResult(TypedDict, total=False):
    """DNS resolution result."""

    domain: str
    record_type: str
    records: list[str]
    ttl: int | None
    error: str | None
    response_time: float | None


class BenchmarkResult(TypedDict):
    """DNS benchmark result for a single server."""

    server: str
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    success_rate: float
    total_queries: int
    failed_queries: int
    responses: list[float]


class PoisoningCheckResult(TypedDict):
    """DNS poisoning check result."""

    domain: str
    control_result: DNSResult
    test_results: dict[str, DNSResult]
    inconsistencies: list[dict[str, Any]]
    poisoned: bool
    confidence: float
