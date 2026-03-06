"""Type definitions for DNS lookup module."""

from typing import Any, Literal, TypedDict

type RecordType = Literal[
    "A", "AAAA", "CNAME", "MX", "NS", "TXT", "PTR", "SOA", "DNSKEY"
]
"""Supported DNS record types for queries and validation."""

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
"""List of all supported DNS record type strings."""


class DNSResult(TypedDict, total=False):
    """
    DNS resolution result for a single query.

    All fields are optional to accommodate partial results from failed queries.

    Attributes:
        domain: The domain name that was queried.
        record_type: The type of DNS record that was requested.
        records: List of resolved record strings. Format varies by record type:
            A/AAAA — IP addresses; MX — ``"priority mailserver"`` strings;
            TXT — concatenated text; others — string repr without trailing dots.
        ttl: Time To Live in seconds, or ``None`` when not requested or unavailable.
        error: Error message if resolution failed; ``None`` on success.
        response_time: Query response time in milliseconds (2 d.p.), or ``None``
            on timeout.

    Examples:
        >>> result: DNSResult = {
        ...     "domain": "example.com",
        ...     "record_type": "A",
        ...     "records": ["93.184.216.34"],
        ...     "ttl": 3600,
        ...     "error": None,
        ...     "response_time": 45.67,
        ... }

    """

    domain: str
    record_type: str
    records: list[str]
    ttl: int | None
    error: str | None
    response_time: float | None


class BenchmarkResult(TypedDict):
    """
    DNS benchmark statistics for a single nameserver.

    Attributes:
        server: IP address of the tested DNS server.
        avg_response_time: Average response time in milliseconds.
        min_response_time: Fastest observed response time in milliseconds.
        max_response_time: Slowest observed response time in milliseconds.
        success_rate: Percentage of successful queries (0.0-100.0).
        total_queries: Total number of queries attempted.
        failed_queries: Number of queries that failed or timed out.
        responses: Individual response times for successful queries.

    Examples:
        >>> result: BenchmarkResult = {
        ...     "server": "8.8.8.8",
        ...     "avg_response_time": 42.5,
        ...     "min_response_time": 15.2,
        ...     "max_response_time": 156.8,
        ...     "success_rate": 98.5,
        ...     "total_queries": 100,
        ...     "failed_queries": 2,
        ...     "responses": [15.2, 23.4, 31.7],
        ... }

    """

    server: str
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    success_rate: float
    total_queries: int
    failed_queries: int
    responses: list[float]


class PoisoningCheckResult(TypedDict, total=False):
    """
    DNS cache poisoning detection result.

    Comprehensive analysis comparing responses from multiple resolvers against
    a trusted control server to detect poisoning, censorship, or manipulation.

    Attributes:
        domain: The domain name tested for poisoning.
        record_type: DNS record type queried.
        control_server: IP address of the trusted control resolver.
        control_name: Provider name of the control server.
        control_country: Country code of the control server.
        control_result: DNS resolution result from the control resolver.
        control_analysis: IP pattern analysis of control server records.
        control_owner: Inferred owner of control server IPs.
        additional_records: Optional extra record types from the control server.
        test_results: Dict mapping test resolver IPs to their DNS results.
        test_servers_count: Number of test servers queried.
        inconsistencies: Detected discrepancies between resolvers.
        poisoned: ``True`` when poisoning indicators exceed the threshold.
        poisoning_level: Severity — NONE/LOW/MEDIUM/HIGH/CRITICAL/SUSPICIOUS.
        confidence: Confidence score (0-100).
        mismatches: Count of record mismatches.
        cdn_variations: Count of CDN-related IP variations.
        cdn_detected: Whether CDN usage was identified.
        cdn_owner: Name of the detected CDN provider.
        cdn_percentage: Percentage of IPs belonging to the CDN.
        severity: Dict mapping severity levels to inconsistency counts.
        unique_ips_seen: Distinct IPs across all test results.
        ip_diversity: IPs not present in the control result.
        control_ip_count: IPs returned by the control server.
        consensus_top: Top-3 most common IPs with count, percentage, and owner.
        consensus_rate: Percentage of servers returning the most common IP.
        geo_diversity: Unique countries among test servers.
        anycast_likely: ``True`` when anycast routing is probable.
        cdn_likely: ``True`` when CDN usage is probable.
        poisoning_likely: ``True`` when deliberate poisoning pattern is probable.

    Examples:
        >>> result: PoisoningCheckResult = {
        ...     "domain": "example.com",
        ...     "poisoned": False,
        ...     "confidence": 0.0,
        ...     "poisoning_level": "NONE",
        ... }

    """

    domain: str
    record_type: str
    control_server: str
    control_name: str
    control_country: str
    control_result: DNSResult
    control_analysis: dict[str, Any]
    control_owner: str
    additional_records: dict[str, DNSResult] | None
    test_results: dict[str, DNSResult]
    test_servers_count: int
    inconsistencies: list[dict[str, Any]]
    poisoned: bool
    poisoning_level: str
    confidence: float
    mismatches: int
    cdn_variations: int
    cdn_detected: bool
    cdn_owner: str
    cdn_percentage: float
    severity: dict[str, int]
    unique_ips_seen: int
    ip_diversity: int
    control_ip_count: int
    consensus_top: list[dict[str, Any]]
    consensus_rate: float
    geo_diversity: int
    anycast_likely: bool
    cdn_likely: bool
    poisoning_likely: bool
