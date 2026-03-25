"""
Type definitions for the DNS lookup module.

All public ``TypedDict`` classes and type aliases used across
``nadzoring.dns_lookup`` are defined here so that consumers can import
types from a single stable location.

Usage example::

    from nadzoring.dns_lookup.types import DNSResult, RecordType

    result: DNSResult = {
        "domain": "example.com",
        "record_type": "A",
        "records": ["93.184.216.34"],
        "ttl": 3600,
        "error": None,
        "response_time": 45.67,
    }

"""

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
        records: List of resolved record strings.  Format varies by type:

            - ``A`` / ``AAAA`` — IP address strings
            - ``MX`` — ``"priority mailserver"`` strings
            - ``TXT`` — concatenated text chunks
            - ``SOA`` — space-joined SOA fields
            - others — ``str()`` with trailing dot stripped

        ttl: Time To Live in seconds, or ``None`` when not requested or
            unavailable.
        error: Human-readable error message if resolution failed;
            ``None`` on success.  Possible values:

            - ``"Domain does not exist"`` — NXDOMAIN
            - ``"No <type> records"`` — no records of this type
            - ``"Query timeout"`` — per-query timeout exceeded
            - arbitrary string — unexpected resolver error

        response_time: Query round-trip time in milliseconds (2 d.p.), or
            ``None`` on timeout.

    Examples:
        Check for errors before using records::

            from nadzoring.dns_lookup.utils import resolve_with_timer

            result = resolve_with_timer("example.com", "A")
            if result["error"]:
                print("DNS error:", result["error"])
            else:
                for record in result["records"]:
                    print(record)
                print(f"RTT: {result['response_time']} ms")

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
        Iterate over benchmark results sorted fastest-first::

            from nadzoring.dns_lookup.benchmark import benchmark_dns_servers

            results = benchmark_dns_servers(
                servers=["8.8.8.8", "1.1.1.1"],
                queries=5,
            )
            for r in results:
                print(f"{r['server']}: avg={r['avg_response_time']:.1f}ms  ok={r['success_rate']}%")

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

    Comprehensive analysis comparing responses from multiple resolvers
    against a trusted control server to detect poisoning, censorship, or
    manipulation.

    Attributes:
        domain: The domain name tested for poisoning.
        record_type: DNS record type queried.
        control_server: IP address of the trusted control resolver.
        control_name: Provider name of the control server.
        control_country: Country code of the control server.
        control_result: DNS resolution result from the control resolver.
        control_analysis: IP pattern analysis of control server records.
        control_owner: Inferred owner of control server IPs.
        additional_records: Optional extra record types from the control.
        test_results: Dict mapping test resolver IPs to their DNS results.
        test_servers_count: Number of test servers queried.
        inconsistencies: Detected discrepancies between resolvers.
        poisoned: ``True`` when poisoning indicators exceed the threshold.
        poisoning_level: Severity string —
            ``NONE`` / ``LOW`` / ``MEDIUM`` / ``HIGH`` / ``CRITICAL`` /
            ``SUSPICIOUS``.
        confidence: Confidence score from 0.0 to 100.0.
        mismatches: Count of record mismatches across test servers.
        cdn_variations: Count of CDN-related IP variations.
        cdn_detected: Whether CDN usage was identified.
        cdn_owner: Name of the detected CDN provider.
        cdn_percentage: Percentage of IPs belonging to the CDN.
        severity: Dict mapping severity labels to inconsistency counts.
        unique_ips_seen: Distinct IP count across all test results.
        ip_diversity: IPs not present in the control result.
        control_ip_count: IPs returned by the control server.
        consensus_top: Top-3 most common IPs with count, percentage, owner.
        consensus_rate: Percentage of servers returning the most common IP.
        geo_diversity: Unique country count among test servers.
        anycast_likely: ``True`` when anycast routing is probable.
        cdn_likely: ``True`` when CDN usage is probable.
        poisoning_likely: ``True`` when deliberate poisoning pattern found.

    Examples:
        Interpreting severity levels::

            from nadzoring.dns_lookup.poisoning import check_dns_poisoning

            result = check_dns_poisoning("example.com")

            level = result.get("poisoning_level", "NONE")
            # NONE     — everything looks consistent
            # LOW      — minor variations, likely CDN/anycast
            # MEDIUM   — notable inconsistencies, worth investigating
            # HIGH     — strong signs of manipulation
            # CRITICAL — near-certain poisoning or censorship
            # SUSPICIOUS — unusual patterns that don't fit CDN

            if result.get("poisoned"):
                for inc in result.get("inconsistencies", []):
                    print(inc)

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
