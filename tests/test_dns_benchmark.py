import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from nadzoring.dns_lookup.benchmark import (
    _benchmark_single_server_async,
    benchmark_dns_servers,
    benchmark_dns_servers_async,
)
from nadzoring.dns_lookup.benchmark import _benchmark_single_server_async


def _result(server: str, avg: float, *, total: int = 2, failed: int = 0) -> dict:
    return {
        "server": server,
        "avg_response_time": avg,
        "min_response_time": avg,
        "max_response_time": avg,
        "success_rate": (
            round(((total - failed) / total) * 100, 2) if total > 0 else 0.0
        ),
        "total_queries": total,
        "failed_queries": failed,
        "responses": [] if failed == total else [avg],
    }


@patch(
    "nadzoring.dns_lookup.benchmark.resolve_with_timer_async", new_callable=AsyncMock
)
def test_benchmark_single_server_async_collects_success_and_failures(
    mock_resolve_async,
):
    mock_resolve_async.side_effect = [
        {
            "domain": "example.com",
            "record_type": "A",
            "records": ["1.1.1.1"],
            "ttl": None,
            "error": None,
            "response_time": 10.0,
        },
        {
            "domain": "example.com",
            "record_type": "A",
            "records": [],
            "ttl": None,
            "error": "Query timeout",
            "response_time": None,
        },
        {
            "domain": "example.com",
            "record_type": "A",
            "records": ["1.1.1.1"],
            "ttl": None,
            "error": None,
            "response_time": 20.0,
        },
    ]

    result = asyncio.run(
        _benchmark_single_server_async(
            "8.8.8.8",
            domain="example.com",
            record_type="A",
            queries=3,
            delay=0,
        )
    )

    assert result["server"] == "8.8.8.8"
    assert result["avg_response_time"] == 15.0
    assert result["min_response_time"] == 10.0
    assert result["max_response_time"] == 20.0
    assert result["success_rate"] == 66.67
    assert result["total_queries"] == 3
    assert result["failed_queries"] == 1
    assert result["responses"] == [10.0, 20.0]
    assert mock_resolve_async.await_count == 3


@patch(
    "nadzoring.dns_lookup.benchmark._benchmark_single_server_async",
    new_callable=AsyncMock,
)
def test_benchmark_dns_servers_parallel_returns_sorted_results(mock_single_async):
    async def _fake(
        server: str, domain: str, record_type: str, queries: int, delay: float = 0.1
    ):
        await asyncio.sleep(0)
        if server == "8.8.8.8":
            return _result(server, 25.0, total=queries)
        return _result(server, 10.0, total=queries)

    mock_single_async.side_effect = _fake

    results = benchmark_dns_servers(
        domain="example.com",
        servers=["8.8.8.8", "1.1.1.1"],
        queries=2,
        max_workers=2,
        parallel=True,
    )

    assert [r["server"] for r in results] == ["1.1.1.1", "8.8.8.8"]
    assert all("avg_response_time" in r for r in results)
    assert all("success_rate" in r for r in results)
    assert mock_single_async.await_count == 2


@patch(
    "nadzoring.dns_lookup.benchmark._benchmark_single_server_async",
    new_callable=AsyncMock,
)
@patch("nadzoring.dns_lookup.benchmark.get_public_dns_servers")
def test_benchmark_dns_servers_parallel_uses_default_servers(
    mock_get_servers, mock_single_async
):
    mock_get_servers.return_value = ["8.8.8.8", "1.1.1.1"]
    mock_single_async.side_effect = [
        _result("8.8.8.8", 20.0),
        _result("1.1.1.1", 10.0),
    ]

    results = benchmark_dns_servers(parallel=True, max_workers=2)

    mock_get_servers.assert_called_once_with()
    assert len(results) == 2
    assert [r["server"] for r in results] == ["1.1.1.1", "8.8.8.8"]


@patch(
    "nadzoring.dns_lookup.benchmark._benchmark_single_server_async",
    new_callable=AsyncMock,
)
def test_benchmark_dns_servers_sequential_calls_progress_in_order(mock_single_async):
    mock_single_async.side_effect = [
        _result("8.8.8.8", 10.0),
        _result("1.1.1.1", 20.0),
    ]
    progress: list[tuple[str, int]] = []

    def _progress(server: str, index: int) -> None:
        progress.append((server, index))

    results = benchmark_dns_servers(
        domain="example.com",
        servers=["8.8.8.8", "1.1.1.1"],
        queries=2,
        parallel=False,
        progress_callback=_progress,
    )

    assert progress == [("8.8.8.8", 1), ("1.1.1.1", 2)]
    assert [r["server"] for r in results] == ["8.8.8.8", "1.1.1.1"]
    assert mock_single_async.await_count == 2


def test_benchmark_dns_servers_parallel_rejects_zero_workers():
    with pytest.raises(ValueError, match="max_workers must be greater than 0"):
        benchmark_dns_servers(
            servers=["8.8.8.8"],
            queries=1,
            parallel=True,
            max_workers=0,
        )


def test_benchmark_dns_servers_sync_raises_with_active_event_loop():
    async def _run() -> None:
        with pytest.raises(RuntimeError, match="active event loop"):
            benchmark_dns_servers(
                servers=["8.8.8.8"],
                queries=1,
                parallel=False,
            )

    asyncio.run(_run())


@patch(
    "nadzoring.dns_lookup.benchmark._benchmark_single_server_async",
    new_callable=AsyncMock,
)
def test_benchmark_dns_servers_async_works_inside_running_loop(mock_single_async):
    mock_single_async.side_effect = [
        _result("8.8.8.8", 12.0),
        _result("1.1.1.1", 8.0),
    ]

    async def _run() -> list[dict]:
        return await benchmark_dns_servers_async(
            servers=["8.8.8.8", "1.1.1.1"],
            queries=2,
            parallel=True,
            max_workers=2,
        )

    results = asyncio.run(_run())
    assert [r["server"] for r in results] == ["1.1.1.1", "8.8.8.8"]
    assert mock_single_async.await_count == 2


@patch(
    "nadzoring.dns_lookup.benchmark._benchmark_single_server_async",
    new_callable=AsyncMock,
)
def test_benchmark_dns_servers_parallel_returns_fallback_on_unexpected_error(
    mock_single_async,
):
    async def _fake(
        server: str, domain: str, record_type: str, queries: int, delay: float = 0.1
    ):
        await asyncio.sleep(0)
        if server == "8.8.8.8":
            raise RuntimeError("boom")
        return _result(server, 10.0, total=queries)

    mock_single_async.side_effect = _fake

    results = benchmark_dns_servers(
        servers=["8.8.8.8", "1.1.1.1"],
        queries=3,
        parallel=True,
        max_workers=2,
    )

    assert len(results) == 2
    failed = next(r for r in results if r["server"] == "8.8.8.8")
    assert failed["avg_response_time"] == 0.0
    assert failed["min_response_time"] == 0.0
    assert failed["max_response_time"] == 0.0
    assert failed["success_rate"] == 0.0
    assert failed["total_queries"] == 3
    assert failed["failed_queries"] == 3
    assert failed["responses"] == []


@patch(
    "nadzoring.dns_lookup.benchmark._benchmark_single_server_async",
    new_callable=AsyncMock,
)
def test_benchmark_dns_servers_sequential_returns_fallback_on_unexpected_error(
    mock_single_async,
):
    mock_single_async.side_effect = [
        RuntimeError("boom"),
        _result("1.1.1.1", 11.0, total=3),
    ]
    progress: list[tuple[str, int]] = []

    def _progress(server: str, index: int) -> None:
        progress.append((server, index))

    results = benchmark_dns_servers(
        servers=["8.8.8.8", "1.1.1.1"],
        queries=3,
        parallel=False,
        progress_callback=_progress,
    )

    assert len(results) == 2
    failed = next(r for r in results if r["server"] == "8.8.8.8")
    assert failed["success_rate"] == 0.0
    assert failed["failed_queries"] == 3
    assert progress == [("8.8.8.8", 1), ("1.1.1.1", 2)]
