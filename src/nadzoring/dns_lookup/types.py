"""Type definitions for DNS lookup module."""

from typing import Any, Literal, TypedDict

RecordType: type["RecordType"] = Literal[
    "A", "AAAA", "CNAME", "MX", "NS", "TXT", "PTR", "SOA", "DNSKEY"
]
"""Supported DNS record types for queries and validation.

Type Aliases:
    RecordType: Literal type restricting values to valid DNS record types:
        - A: IPv4 address records
        - AAAA: IPv6 address records
        - CNAME: Canonical name records (aliases)
        - MX: Mail exchange records
        - NS: Nameserver records
        - TXT: Text records (SPF, DKIM, etc.)
        - PTR: Pointer records (reverse DNS)
        - SOA: Start of authority records
        - DNSKEY: DNS key records (DNSSEC)
"""

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
"""List of all supported DNS record types as strings.

Useful for iterating over all record types or validating input.
Maintains the same order as the RecordType Literal for consistency.
"""


class DNSResult(TypedDict, total=False):
    """
    DNS resolution result for a single query.

    Represents the outcome of a DNS lookup operation, including resolved records,
    timing information, and any errors encountered. All fields are optional
    to accommodate partial results from failed queries.

    Attributes:
        domain: The domain name that was queried (e.g., "example.com").
        record_type: The type of DNS record that was requested.
        records: List of resolved record strings. Format varies by record type:
            - A/AAAA: IP addresses
            - MX: "priority mailserver" strings
            - TXT: Concatenated text strings
            - Others: String representations with trailing dots removed
        ttl: Time To Live in seconds for the records. None if not available
             or if include_ttl was False in the query.
        error: Error message string if resolution failed. None for successful
               resolutions.
        response_time: Query response time in milliseconds, rounded to 2 decimal
                      places. None if the query failed or timed out.

    Example:
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
    DNS benchmark results for a single nameserver.

    Comprehensive statistics from performing multiple DNS queries against
    a specific DNS server, measuring performance and reliability.

    Attributes:
        server: IP address of the tested DNS server.
        avg_response_time: Average response time in milliseconds across
                          all successful queries.
        min_response_time: Minimum (fastest) response time observed in
                          milliseconds.
        max_response_time: Maximum (slowest) response time observed in
                          milliseconds.
        success_rate: Percentage of successful queries as a float between
                     0.0 and 100.0.
        total_queries: Total number of queries attempted against the server.
        failed_queries: Number of queries that failed or timed out.
        responses: List of individual response times in milliseconds for
                  all successful queries, useful for distribution analysis.

    Example:
        >>> result: BenchmarkResult = {
        ...     "server": "8.8.8.8",
        ...     "avg_response_time": 42.5,
        ...     "min_response_time": 15.2,
        ...     "max_response_time": 156.8,
        ...     "success_rate": 98.5,
        ...     "total_queries": 100,
        ...     "failed_queries": 2,
        ...     "responses": [15.2, 23.4, 31.7, ...],
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


class PoisoningCheckResult(TypedDict):
    """
    DNS cache poisoning detection result.

    Results from comparing DNS responses from multiple resolvers to detect
    potential DNS poisoning or spoofing attacks. Identifies inconsistencies
    between a control resolver (trusted) and test resolvers.

    Attributes:
        domain: The domain name that was checked for poisoning.
        control_result: DNS resolution result from a trusted control resolver
                       (e.g., 8.8.8.8) used as baseline for comparison.
        test_results: Dictionary mapping test resolver IP addresses to their
                     DNS resolution results for the same domain.
        inconsistencies: List of detected inconsistencies between control and
                        test resolvers. Each item contains details about the
                        discrepancy.
        poisoned: Boolean flag indicating whether poisoning was detected
                 (True if inconsistencies exceed threshold).
        confidence: Confidence score as a float between 0.0 and 1.0,
                   representing the certainty of poisoning detection based
                   on the number and severity of inconsistencies.

    Example:
        >>> result: PoisoningCheckResult = {
        ...     "domain": "example.com",
        ...     "control_result": {...},
        ...     "test_results": {"1.1.1.1": {...}, "9.9.9.9": {...}},
        ...     "inconsistencies": [
        ...         {
        ...             "resolver": "1.1.1.1",
        ...             "type": "ip_mismatch",
        ...             "expected": "93.184.216.34",
        ...             "got": "192.168.1.1",
        ...         }
        ...     ],
        ...     "poisoned": True,
        ...     "confidence": 0.95,
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

    domain: str
    control_result: DNSResult
    test_results: dict[str, DNSResult]
    inconsistencies: list[dict[str, Any]]
    poisoned: bool
    confidence: float
