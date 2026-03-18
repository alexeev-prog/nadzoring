"""DNS server benchmarking for performance testing and comparison."""

import asyncio
import operator
import statistics
from collections.abc import Callable
from logging import Logger
from time import sleep

from nadzoring.dns_lookup.types import BenchmarkResult, DNSResult, RecordType
from nadzoring.dns_lookup.utils import (
    get_public_dns_servers,
    resolve_with_timer,
    resolve_with_timer_async,
)
from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

_DEFAULT_DOMAIN = "google.com"
_DEFAULT_DELAY = 0.1
_DEFAULT_MAX_WORKERS = 5


def benchmark_single_server(
    server: str,
    domain: str = _DEFAULT_DOMAIN,
    record_type: RecordType = "A",
    queries: int = 10,
    delay: float = _DEFAULT_DELAY,
) -> BenchmarkResult:
    """
    Benchmark the performance of a single DNS server.

    Performs *queries* DNS lookups against *server*, measuring response time
    and calculating average, minimum, maximum, and success rate statistics.

    Args:
        server: IP address of the DNS server to benchmark.
        domain: Domain to query. Defaults to ``"google.com"``.
        record_type: DNS record type to query. Defaults to ``"A"``.
        queries: Number of queries to perform. Defaults to ``10``.
        delay: Seconds to wait between queries to avoid rate limiting.
            Defaults to ``0.1``. Set to ``0`` to disable.

    Returns:
        :class:`BenchmarkResult` dict with ``server``, ``avg_response_time``,
        ``min_response_time``, ``max_response_time``, ``success_rate``,
        ``total_queries``, ``failed_queries``, and ``responses`` keys.

    Examples:
        >>> result = benchmark_single_server("8.8.8.8")
        >>> print(f"{result['avg_response_time']:.2f}ms avg")

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
        except Exception as exc:
            logger.debug("Benchmark query failed for %s: %s", server, exc)
            failed += 1

    success_rate: float = ((queries - failed) / queries) * 100 if queries > 0 else 0.0

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
    domain: str = _DEFAULT_DOMAIN,
    servers: list[str] | None = None,
    record_type: RecordType = "A",
    queries: int = 10,
    max_workers: int = _DEFAULT_MAX_WORKERS,
    progress_callback: Callable[[str, int], None] | None = None,
    *,
    parallel: bool = True,
) -> list[BenchmarkResult]:
    """
    Benchmark multiple DNS servers and compare their performance.

    This synchronous wrapper runs :func:`benchmark_dns_servers_async`
    in a fresh event loop.

    Tests each server either in parallel (with :mod:`asyncio`) or
    sequentially, then sorts results by average response time.

    Args:
        domain: Domain to query. Defaults to ``"google.com"``.
        servers: Server IPs to benchmark. ``None`` uses
            :func:`~nadzoring.dns_lookup.utils.get_public_dns_servers`.
        record_type: DNS record type to query. Defaults to ``"A"``.
        queries: Queries per server. Defaults to ``10``.
        max_workers: Maximum number of concurrently benchmarked servers
            when *parallel* is ``True``.
            Defaults to ``5``.
        progress_callback: Called after each server completes with
            ``(server_ip, 1-based_index)``.
        parallel: Run benchmarks concurrently when ``True`` (default).

    Returns:
        List of :class:`BenchmarkResult` dicts sorted by
        ``avg_response_time`` ascending (fastest first).

    Examples:
        >>> results = benchmark_dns_servers(servers=["8.8.8.8", "1.1.1.1"])
        >>> fastest = results[0]
        >>> print(f"{fastest['server']}: {fastest['avg_response_time']:.2f}ms")

    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        raise RuntimeError(
            "benchmark_dns_servers() cannot run inside an active event loop; "
            "use 'await benchmark_dns_servers_async(...)' instead."
        )

    return asyncio.run(
        benchmark_dns_servers_async(
            domain=domain,
            servers=servers,
            record_type=record_type,
            queries=queries,
            max_workers=max_workers,
            progress_callback=progress_callback,
            parallel=parallel,
        )
    )


async def benchmark_dns_servers_async(
    domain: str = _DEFAULT_DOMAIN,
    servers: list[str] | None = None,
    record_type: RecordType = "A",
    queries: int = 10,
    max_workers: int = _DEFAULT_MAX_WORKERS,
    progress_callback: Callable[[str, int], None] | None = None,
    *,
    parallel: bool = True,
) -> list[BenchmarkResult]:
    """
    Benchmark multiple DNS servers and compare their performance.

    Async variant of :func:`benchmark_dns_servers` for environments that
    already have an active event loop (e.g. async applications, notebooks).

    Args:
        domain: Domain to query. Defaults to ``"google.com"``.
        servers: Server IPs to benchmark. ``None`` uses
            :func:`~nadzoring.dns_lookup.utils.get_public_dns_servers`.
        record_type: DNS record type to query. Defaults to ``"A"``.
        queries: Queries per server. Defaults to ``10``.
        max_workers: Maximum number of concurrently benchmarked servers
            when *parallel* is ``True``.
            Defaults to ``5``.
        progress_callback: Called after each server completes with
            ``(server_ip, 1-based_index)``.
        parallel: Run benchmarks concurrently when ``True`` (default).

    Returns:
        List of :class:`BenchmarkResult` dicts sorted by
        ``avg_response_time`` ascending (fastest first).

    Examples:
        >>> import asyncio
        >>> results = asyncio.run(benchmark_dns_servers_async(servers=["8.8.8.8", "1.1.1.1"]))
        >>> fastest = results[0]
        >>> print(f"{fastest['server']}: {fastest['avg_response_time']:.2f}ms")

    """
    if servers is None:
        servers = get_public_dns_servers()

    if parallel:
        results_list: list[BenchmarkResult] = await _benchmark_parallel_async(
            servers,
            domain,
            record_type,
            queries,
            max_workers,
            progress_callback,
        )
    else:
        results_list = await _benchmark_sequential_async(
            servers,
            domain,
            record_type,
            queries,
            progress_callback,
        )

    results_list.sort(key=operator.itemgetter("avg_response_time"))
    return results_list


async def _benchmark_single_server_async(
    server: str,
    domain: str,
    record_type: RecordType,
    queries: int,
    delay: float = _DEFAULT_DELAY,
) -> BenchmarkResult:
    """Async variant of :func:`benchmark_single_server`."""
    responses: list[float] = []
    failed = 0

    for i in range(queries):
        if i > 0 and delay > 0:
            await asyncio.sleep(delay)

        try:
            result: DNSResult = await resolve_with_timer_async(domain, record_type, server)
            if result["response_time"] is not None and not result["error"]:
                responses.append(result["response_time"])
            else:
                failed += 1
        except Exception as exc:
            logger.debug("Benchmark query failed for %s: %s", server, exc)
            failed += 1

    success_rate: float = ((queries - failed) / queries) * 100 if queries > 0 else 0.0

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


async def _benchmark_parallel_async(
    servers: list[str],
    domain: str,
    record_type: RecordType,
    queries: int,
    max_workers: int,
    progress_callback: Callable[[str, int], None] | None,
) -> list[BenchmarkResult]:
    """
    Run server benchmarks concurrently using asyncio tasks.

    Args:
        servers: Server IP addresses to benchmark.
        domain: Domain to query.
        record_type: DNS record type.
        queries: Queries per server.
        max_workers: Maximum concurrently running benchmark tasks.
        progress_callback: Optional progress callback.

    Returns:
        List of benchmark results (unsorted).

    """
    if max_workers <= 0:
        raise ValueError("max_workers must be greater than 0")

    semaphore = asyncio.Semaphore(max_workers)
    results: list[BenchmarkResult] = []

    async def _safe_benchmark(server: str) -> tuple[str, BenchmarkResult]:
        try:
            async with semaphore:
                return (
                    server,
                    await _benchmark_single_server_async(server, domain, record_type, queries),
                )
        except Exception:
            logger.exception("Benchmark failed for %s", server)
            return (server, _make_failed_benchmark_result(server, queries))

    tasks: list[asyncio.Task[tuple[str, BenchmarkResult]]] = [
        asyncio.create_task(_safe_benchmark(server)) for server in servers
    ]

    for i, task in enumerate(asyncio.as_completed(tasks)):
        server, result = await task
        results.append(result)
        if progress_callback:
            progress_callback(server, i + 1)

    return results


async def _benchmark_sequential_async(
    servers: list[str],
    domain: str,
    record_type: RecordType,
    queries: int,
    progress_callback: Callable[[str, int], None] | None,
) -> list[BenchmarkResult]:
    """
    Run server benchmarks one at a time using async DNS queries.

    Args:
        servers: Server IP addresses to benchmark.
        domain: Domain to query.
        record_type: DNS record type.
        queries: Queries per server.
        progress_callback: Optional progress callback.

    Returns:
        List of benchmark results (unsorted).

    """
    results: list[BenchmarkResult] = []

    for i, server in enumerate(servers):
        try:
            result: BenchmarkResult = await _benchmark_single_server_async(server, domain, record_type, queries)
        except Exception:
            logger.exception("Benchmark failed for %s", server)
            result = _make_failed_benchmark_result(server, queries)
        results.append(result)

        if progress_callback:
            progress_callback(server, i + 1)

    return results


def _make_failed_benchmark_result(server: str, queries: int) -> BenchmarkResult:
    """Create a deterministic fallback result for a failed server benchmark."""
    return {
        "server": server,
        "avg_response_time": 0.0,
        "min_response_time": 0.0,
        "max_response_time": 0.0,
        "success_rate": 0.0,
        "total_queries": queries,
        "failed_queries": queries,
        "responses": [],
    }
