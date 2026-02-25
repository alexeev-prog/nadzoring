# nadzoring/dns_lookup/benchmark.py
"""DNS server benchmarking functionality."""

import statistics
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from logging import Logger
from time import sleep
from typing import Literal

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
    """Benchmark a single DNS server performance."""
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

    success_rate: Literal[0] | float = (
        ((queries - failed) / queries) * 100 if queries > 0 else 0
    )

    return {
        "server": server,
        "avg_response_time": statistics.mean(responses) if responses else 0,
        "min_response_time": min(responses) if responses else 0,
        "max_response_time": max(responses) if responses else 0,
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
    """Benchmark the performance of DNS servers."""
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
