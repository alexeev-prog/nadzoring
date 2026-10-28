"""Entrypoint, logging, and benchmark edge cases."""

import asyncio
import importlib
import logging
import runpy
from unittest.mock import AsyncMock, Mock

import click
import pytest

from nadzoring.dns_lookup import benchmark
from nadzoring.logger import ColoredFormatter, get_logger


@pytest.mark.parametrize("asynchronous", [False, True])
def test_single_server_benchmark(monkeypatch, asynchronous):
    """Count successful, failed, and exceptional benchmark samples."""
    results = [
        {"response_time": 2.0, "error": None},
        {"response_time": None, "error": "failed"},
        RuntimeError("failed"),
    ]
    if asynchronous:
        monkeypatch.setattr(benchmark, "resolve_with_timer_async", AsyncMock(side_effect=results))
        monkeypatch.setattr(benchmark.asyncio, "sleep", AsyncMock())
        result = asyncio.run(benchmark._benchmark_single_server_async("192.0.2.53", "example.com", "A", 3))
    else:
        monkeypatch.setattr(benchmark, "resolve_with_timer", Mock(side_effect=results))
        monkeypatch.setattr(benchmark, "sleep", Mock())
        result = benchmark.benchmark_single_server("192.0.2.53", queries=3)
    assert result["failed_queries"] == 2
    assert result["responses"] == [2.0]
    assert result["success_rate"] == 33.33


def test_parallel_benchmark_progress(monkeypatch):
    """Notify the caller after a parallel benchmark finishes."""
    monkeypatch.setattr(
        benchmark,
        "_benchmark_single_server_async",
        AsyncMock(return_value={"avg_response_time": 1}),
    )
    progress = Mock()
    asyncio.run(benchmark.benchmark_dns_servers_async(servers=["192.0.2.53"], progress_callback=progress))
    progress.assert_called_once_with("192.0.2.53", 1)


@pytest.mark.parametrize("colors,simple", [(True, False), (False, True), (False, False)])
def test_logging_formats(colors, simple):
    """Render every detailed and plain formatter configuration."""
    record = logging.LogRecord("test", logging.WARNING, __file__, 1, "message", (), None)
    assert "message" in ColoredFormatter(use_colors=colors, simple=simple).format(record)
    assert isinstance(get_logger(), logging.Logger)


def test_module_entrypoints(monkeypatch):
    """Run both module entrypoints without starting an actual CLI session."""
    cli_module = importlib.import_module("nadzoring.cli")
    invoke = Mock()
    monkeypatch.setattr(cli_module, "cli", invoke)
    cli_module.main()
    invoke.assert_called_once_with()
    main = Mock()
    monkeypatch.setattr(cli_module, "main", main)
    runpy.run_module("nadzoring.__main__", run_name="__main__")
    main.assert_called_once_with()
    monkeypatch.setattr(click.core.Command, "__call__", Mock())
    runpy.run_path(cli_module.__file__, run_name="__main__")
