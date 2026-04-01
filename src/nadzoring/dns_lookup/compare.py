"""DNS server comparison for analysing differences between resolvers."""

from collections.abc import Callable
from typing import Any, TypedDict

from nadzoring.dns_lookup.types import DNSResult, RecordType
from nadzoring.dns_lookup.utils import resolve_with_timer
from nadzoring.utils.timeout import TimeoutConfig


class ServerComparisonResult(TypedDict):
    """
    Result of comparing DNS responses from multiple servers.

    Attributes:
        domain: The domain name that was queried.
        servers: Nested dict mapping server IPs to per-record-type results.
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
        expected: Records expected (from the baseline server).
        got: Actual records received from this server.
        ttl_difference: Absolute TTL difference in seconds, or ``None`` when
            TTL data is unavailable for either server.

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
    timeout_config: TimeoutConfig | None = None,
) -> ServerComparisonResult:
    """
    Compare DNS responses from multiple servers for the same domain.

    Uses the first server in *servers* as the baseline. Each subsequent
    server's records are compared against the baseline; discrepancies are
    collected in ``differences``.

    Args:
        domain: Domain name to query (e.g. ``"example.com"``).
        servers: DNS server IPs to compare. The first entry is the baseline.
        record_types: Record types to query on every server.
        progress_callback: Called after each successful query. Useful for
            progress bars.
        timeout_config: Unified timeout configuration. If None, uses default.

    Returns:
        :class:`ServerComparisonResult` with ``domain``, ``servers``, and
        ``differences`` keys.

    Examples:
        >>> result = compare_dns_servers(
        ...     "example.com",
        ...     servers=["8.8.8.8", "1.1.1.1"],
        ...     record_types=["A", "MX"],
        ... )
        >>> result["differences"]
        []

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    result: ServerComparisonResult = {
        "domain": domain,
        "servers": {},
        "differences": [],
    }

    for i, server in enumerate(servers):
        server_results: dict[str, DNSResult] = {}
        is_baseline: bool = i == 0

        for rtype_str in record_types:
            rtype: RecordType = rtype_str  # type: ignore
            query_result: DNSResult = resolve_with_timer(
                domain,
                rtype,
                server,
                include_ttl=True,
                timeout_config=timeout_config,
            )

            if is_baseline:
                query_result["differs"] = False  # type: ignore
            else:
                base: DNSResult = result["servers"][servers[0]].get(rtype_str, {})
                differs: bool = query_result.get("records") != base.get("records")
                query_result["differs"] = differs  # type: ignore

                if differs:
                    result["differences"].append({
                        "server": server,
                        "type": rtype_str,
                        "expected": base.get("records", []),
                        "got": query_result.get("records", []),
                        "ttl_difference": _calculate_ttl_difference(base.get("ttl"), query_result.get("ttl")),
                    })

            server_results[rtype_str] = query_result

            if progress_callback:
                progress_callback()

        result["servers"][server] = server_results

    return result


def _calculate_ttl_difference(ttl1: int | None, ttl2: int | None) -> int | None:
    """
    Return the absolute difference between two TTL values.

    Args:
        ttl1: First TTL in seconds.
        ttl2: Second TTL in seconds.

    Returns:
        Absolute difference when both values are provided, ``None`` otherwise.

    """
    if ttl1 is None or ttl2 is None:
        return None
    return abs(ttl1 - ttl2)
