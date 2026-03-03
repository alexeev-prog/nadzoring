# nadzoring/dns_lookup/benchmark.py
"""
DNS server benchmarking functionality for performance testing and comparison.

This module provides tools to benchmark DNS server performance by measuring
response times, success rates, and statistical metrics across multiple queries.
"""

import statistics
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from logging import Logger
from time import sleep

from nadzoring.dns_lookup.types import BenchmarkResult, DNSResult, RecordType
from nadzoring.dns_lookup.utils import get_public_dns_servers, resolve_with_timer
from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def benchmark_single_server(
    server: str,
    domain: str = "google.com",
    record_type: RecordType = "A",
    queries: int = 10,
    delay: float = 0.1,
) -> BenchmarkResult:
    """
    Benchmark the performance of a single DNS server.

    Performs multiple DNS queries to a specific server, measuring response times
    and calculating statistical metrics including average, minimum, maximum,
    and success rate.

    Args:
        server: IP address of the DNS server to benchmark (e.g., "8.8.8.8").
        domain: Domain name to query for benchmarking. Defaults to "google.com"
               as a stable, widely-resolvable domain.
        record_type: DNS record type to query. Defaults to "A" records.
        queries: Number of queries to perform for the benchmark. Defaults to 10.
                Higher numbers provide more accurate statistics but take longer.
        delay: Delay in seconds between queries to avoid rate limiting.
              Defaults to 0.1 seconds. Set to 0 for no delay.

    Returns:
        BenchmarkResult: Dictionary containing benchmark metrics:
            - server: The benchmarked server IP address
            - avg_response_time: Mean response time in milliseconds
            - min_response_time: Fastest response time in milliseconds
            - max_response_time: Slowest response time in milliseconds
            - success_rate: Percentage of successful queries (0-100)
            - total_queries: Total number of queries attempted
            - failed_queries: Number of queries that failed or timed out
            - responses: List of all successful response times in milliseconds

    Examples:
        >>> # Basic single server benchmark
        >>> result = benchmark_single_server("8.8.8.8")
        >>> print(f"Google DNS: {result['avg_response_time']:.2f}ms avg")
        >>> print(f"Success rate: {result['success_rate']}%")

        >>> # Custom benchmark with more queries
        >>> result = benchmark_single_server(
        ...     server="1.1.1.1", domain="example.com", queries=20, delay=0.2
        ... )
        >>> print(
        ...     f"MinMax: {result['min_response_time']}-{result['max_response_time']}ms"
        ... )

    Notes:
        - Failed queries (timeouts, errors) are excluded from response time statistics
          but count toward the success rate calculation
        - Response times are measured in milliseconds with 2 decimal precision
        - The delay between queries helps prevent rate limiting by DNS providers
        - Exceptions during individual queries are caught and logged as debug messages
          without stopping the benchmark

    """
    responses: list[float] = []
    failed = 0

    for i in range(queries):
        if i > 0 and delay > 0:
            sleep(delay)

        try:
            result: DNSResult = resolve_with_timer(domain, record_type, server)

            if result["response_time"] is not None and not result["error"]:
                responses.append(result["response_time"])
            else:
                failed += 1
        except Exception as e:
            logger.debug("Benchmark query failed for %s: %s", server, e)
            failed += 1

    success_rate: float = ((queries - failed) / queries) * 100 if queries > 0 else 0

    return {
        "server": server,
        "avg_response_time": statistics.mean(responses) if responses else 0.0,
        "min_response_time": min(responses) if responses else 0.0,
        "max_response_time": max(responses) if responses else 0.0,
        "success_rate": round(success_rate, 2),
        "total_queries": queries,
        "failed_queries": failed,
        "responses": responses,
    }


def benchmark_dns_servers(
    domain: str = "google.com",
    servers: list[str] | None = None,
    record_type: RecordType = "A",
    queries: int = 10,
    max_workers: int = 5,
    progress_callback: Callable[[str, int], None] | None = None,
    *,
    parallel: bool = True,
) -> list[BenchmarkResult]:
    """
    Benchmark multiple DNS servers and compare their performance.

    Tests multiple DNS servers either in parallel or sequentially, measuring
    response times and success rates. Results are sorted by average response time
    for easy comparison.

    Args:
        domain: Domain name to query for benchmarking. Defaults to "google.com".
        servers: List of DNS server IP addresses to benchmark. If None, uses
                get_public_dns_servers() for a comprehensive list of public
                DNS providers.
        record_type: DNS record type to query. Defaults to "A" records.
        queries: Number of queries to perform per server. Defaults to 10.
        max_workers: Maximum number of parallel threads when parallel=True.
                    Defaults to 5. Ignored when parallel=False.
        progress_callback: Optional callback function called after each server
                          completes benchmarking. Receives the server IP and
                          the completion index (1-based). Useful for UI progress bars.
        parallel: If True, benchmarks servers in parallel using multiple threads.
                 If False, benchmarks sequentially. Defaults to True.

    Returns:
        List[BenchmarkResult]: List of benchmark results for each server,
            sorted by average response time (fastest first). Each result
            contains the same fields as benchmark_single_server().

    Examples:
        >>> # Basic parallel benchmark of all public DNS servers
        >>> results = benchmark_dns_servers()
        >>> for i, r in enumerate(results[:5], 1):
        ...     print(f"{i}. {r['server']}: {r['avg_response_time']:.2f}ms")

        >>> # Benchmark specific servers sequentially with progress tracking
        >>> def progress(server: str, index: int):
        ...     print(f"[{index}] Completed {server}")
        >>>
        >>> results = benchmark_dns_servers(
        ...     servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
        ...     parallel=False,
        ...     progress_callback=progress,
        ... )

        >>> # Custom benchmark with more queries
        >>> results = benchmark_dns_servers(
        ...     domain="example.com",
        ...     servers=["8.8.8.8", "1.1.1.1"],
        ...     queries=20,
        ...     max_workers=2,
        ... )
        >>> fastest = results[0]
        >>> slowest = results[-1]
        >>> print(
        ...     f"Fastest: {fastest['server']} ({fastest['avg_response_time']:.2f}ms)"
        ... )
        >>> print(
        ...     f"Slowest: {slowest['server']} ({slowest['avg_response_time']:.2f}ms)"
        ... )

    Notes:
        - Parallel benchmarking uses ThreadPoolExecutor for concurrent queries
        - Results are always sorted by average response time (fastest first)
        - Failed servers are still included in results with 0 response times
        - The progress callback receives both server IP and completion index
        - Logging at debug level captures individual server failures
        - Consider rate limiting when using parallel=True with many servers
        - Default server list includes major public DNS providers:
            Google, Cloudflare, OpenDNS, Quad9, Verisign, and others

    """
    if servers is None:
        servers = get_public_dns_servers()

    results: list[BenchmarkResult] = []

    if parallel:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_server: dict[Future[BenchmarkResult], str] = {
                executor.submit(
                    benchmark_single_server,
                    server,
                    domain,
                    record_type,
                    queries,
                ): server
                for server in servers
            }

            for i, future in enumerate(as_completed(future_to_server)):
                server: str = future_to_server[future]
                try:
                    result: BenchmarkResult = future.result()
                    results.append(result)
                    if progress_callback:
                        progress_callback(server, i + 1)
                except Exception:
                    logger.exception("Benchmark failed for %s", server)
    else:
        for i, server in enumerate(servers):
            try:
                result = benchmark_single_server(server, domain, record_type, queries)
                results.append(result)
                if progress_callback:
                    progress_callback(server, i + 1)
            except Exception:
                logger.exception("Benchmark failed for %s", server)

    results.sort(key=lambda x: x["avg_response_time"])
    return results
