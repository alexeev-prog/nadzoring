"""DNS server comparison functionality for analyzing differences between resolvers.

This module provides tools to compare DNS responses from multiple servers,
identifying discrepancies in records, TTLs, and response characteristics.
"""

from collections.abc import Callable
from typing import Any, TypedDict

from nadzoring.dns_lookup.types import DNSResult
from nadzoring.dns_lookup.utils import resolve_with_timer


class ServerComparisonResult(TypedDict):
    """
    Result of comparing DNS responses from multiple servers.

    Attributes:
        domain: The domain name that was queried.
        servers: Dictionary mapping server IPs to their per-record-type results.
        differences: List of detected differences between servers.
    """

    domain: str
    servers: dict[str, dict[str, DNSResult]]
    differences: list[dict[str, Any]]


class DifferenceDetail(TypedDict):
    """
    Detailed information about a detected difference between DNS servers.

    Attributes:
        server: IP address of the server that returned a different response.
        type: DNS record type where the difference was detected.
        expected: Records expected (from the first/baseline server).
        got: Actual records received from this server.
        ttl_difference: Optional TTL difference if significant.
    """

    server: str
    type: str
    expected: list[str]
    got: list[str]
    ttl_difference: int | None


def compare_dns_servers(
    domain: str,
    servers: list[str],
    record_types: list[str],
    progress_callback: Callable[[], None] | None = None,
) -> ServerComparisonResult:
    """
    Compare DNS responses from multiple servers for the same domain.

    Queries multiple DNS servers for the same set of record types and identifies
    differences in responses. Uses the first server in the list as the baseline
    for comparison.

    Args:
        domain: Domain name to query (e.g., "example.com").
        servers: List of DNS server IP addresses to compare.
                The first server in the list is used as the baseline.
        record_types: List of DNS record types to query for each server
                     (e.g., ["A", "MX", "TXT"]).
        progress_callback: Optional callback function called after each
                          successful query to report progress. Useful for
                          UI progress bars.

    Returns:
        ServerComparisonResult: Dictionary containing comparison results:
            - domain: The domain that was queried
            - servers: Nested dictionary mapping server IPs to their results:
                {
                    "server_ip": {
                        "A": DNSResult,
                        "MX": DNSResult,
                        ...
                    },
                    ...
                }
            - differences: List of detected differences, each containing:
                - server: IP of the differing server
                - type: Record type that differs
                - expected: Records from baseline server
                - got: Records from this server
                - ttl_difference: TTL difference if applicable

    Examples:
        >>> # Basic comparison
        >>> result = compare_dns_servers(
        ...     "example.com",
        ...     servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
        ...     record_types=["A", "MX"],
        ... )
        >>> for diff in result["differences"]:
        ...     print(f"{diff['server']}: {diff['type']} differs")
        ...     print(f"  Expected: {diff['expected']}")
        ...     print(f"  Got: {diff['got']}")

        >>> # With progress tracking
        >>> def update_progress():
        ...     print(".", end="", flush=True)
        >>>
        >>> result = compare_dns_servers(
        ...     "example.com",
        ...     servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
        ...     record_types=["A", "AAAA", "MX"],
        ...     progress_callback=update_progress,
        ... )

        >>> # Check if all servers agree
        >>> if not result["differences"]:
        ...     print("All servers returned identical results")
        >>> else:
        ...     print(f"Found {len(result['differences'])} differences")

    Notes:
        - The first server in the list serves as the baseline for all comparisons
        - TTL values are included in the DNSResult objects but not compared by default
        - Differences are recorded only when the actual records differ, not TTLs
        - Each query includes TTL information (include_ttl=True)
        - The progress callback is called after each successful query,
          allowing for accurate progress tracking in UIs
        - Empty responses (no records) are considered valid and compared normally
        - Error responses are included in the comparison and may cause differences
    """
    result: ServerComparisonResult = {
        "domain": domain,
        "servers": {},
        "differences": [],
    }

    for i, server in enumerate(servers):
        server_results: dict[str, DNSResult] = {}

        for rtype in record_types:
            query_result: DNSResult = resolve_with_timer(
                domain, rtype, server, include_ttl=True
            )

            if i == 0:
                query_result["differs"] = False
            else:
                base: DNSResult = result["servers"][servers[0]].get(rtype, {})
                differs: bool = query_result.get("records") != base.get("records")
                query_result["differs"] = differs

                if differs:
                    result["differences"].append(
                        {
                            "server": server,
                            "type": rtype,
                            "expected": base.get("records", []),
                            "got": query_result.get("records", []),
                            "ttl_difference": (
                                _calculate_ttl_difference(
                                    base.get("ttl"), query_result.get("ttl")
                                )
                                if base.get("ttl") and query_result.get("ttl")
                                else None
                            ),
                        }
                    )

            server_results[rtype] = query_result

            if progress_callback:
                progress_callback()

        result["servers"][server] = server_results

    return result


def _calculate_ttl_difference(ttl1: int | None, ttl2: int | None) -> int | None:
    """
    Calculate the absolute difference between two TTL values.

    Args:
        ttl1: First TTL value in seconds.
        ttl2: Second TTL value in seconds.

    Returns:
        Optional[int]: Absolute difference between TTLs if both are provided,
                      None otherwise.
    """
    if ttl1 is None or ttl2 is None:
        return None
    return abs(ttl1 - ttl2)
