"""DNS command orchestration, formatting, and log aggregation tests."""

from types import SimpleNamespace
from unittest.mock import Mock

import click
import pytest

from nadzoring.commands import dns_commands as commands
from nadzoring.utils.timeout import TimeoutConfig


def call(name, *args, **kwargs):
    """Invoke a command body without shared output handling."""
    return getattr(commands, name).callback.__wrapped__(*args, **kwargs)


@pytest.fixture(autouse=True)
def progress(monkeypatch):
    """Keep command progress reporting deterministic."""
    monkeypatch.setattr(commands, "tqdm", Mock(return_value=Mock()))


@pytest.mark.parametrize("quiet", [False, True])
def test_dns_queries(monkeypatch, quiet):
    """Expand types and forward query options and reverse lookup results."""
    assert "PTR" not in commands._expand_record_types(("ALL",))
    assert commands._expand_record_types(("A", "invalid")) == ["A"]
    monkeypatch.setattr(commands, "resolve_dns", Mock(return_value={"records": ["192.0.2.1"]}))
    formatter = Mock(return_value=[{"formatted": True}])
    monkeypatch.setattr(commands, "format_dns_record", formatter)
    assert call(
        "resolve_command",
        ("example.com",),
        ("A",),
        None,
        "standard",
        TimeoutConfig(),
        quiet=quiet,
        short=True,
        show_ttl=True,
    ) == [{"formatted": True}]
    assert formatter.call_args.kwargs["style"] == "short"
    monkeypatch.setattr(
        commands,
        "reverse_dns",
        Mock(
            return_value={
                "ip_address": "192.0.2.1",
                "hostname": None,
                "response_time": None,
            }
        ),
    )
    assert call("reverse_command", ("192.0.2.1",), None, quiet=quiet)[0]["hostname"] == "Not found"
    monkeypatch.setattr(
        commands,
        "check_dns",
        Mock(
            return_value={
                "records": {"A": ["192.0.2.1"], "MX": ["10 mail"]},
                "errors": {"TXT": "failed"},
            }
        ),
    )
    result = call(
        "check_command",
        ("example.com",),
        None,
        ("A", "MX", "TXT", "NS"),
        TimeoutConfig(),
        quiet=quiet,
    )
    assert result == [
        {
            "domain": "example.com",
            "A": "192.0.2.1",
            "MX": "Priority 10 mail",
            "TXT": "[failed]",
            "NS": "None",
        }
    ]


def test_dns_whois(monkeypatch):
    """Return registration data or translate a domain-layer error."""
    monkeypatch.setattr(
        commands,
        "whois_domain_lookup",
        Mock(side_effect=[[{"domain": "example.com"}], [{"error": "failed"}]]),
    )
    assert call("whois_command", "example.com", quiet=True) == [{"domain": "example.com"}]
    with pytest.raises(click.ClickException, match="failed"):
        call("whois_command", "example.com", quiet=True)


def test_dns_analysis_commands(monkeypatch):
    """Pass analysis results to their dedicated formatters."""
    for operation, formatter in [
        ("trace_dns", "format_dns_trace"),
        ("health_check_dns", "format_dns_health"),
        ("check_dns_poisoning", "format_dns_poisoning"),
    ]:
        monkeypatch.setattr(commands, operation, Mock(return_value={"domain": "example.com"}))
        monkeypatch.setattr(commands, formatter, lambda result: [result])
    assert call("trace_command", "example.com", None, TimeoutConfig(), quiet=False) == [{"domain": "example.com"}]
    assert call("health_command", "example.com", None, TimeoutConfig(), quiet=False) == [{"domain": "example.com"}]
    assert call("poisoning_command", "example.com", "8.8.8.8", (), "A", (), TimeoutConfig()) == [
        {"domain": "example.com"}
    ]


def test_dns_progress_callbacks(monkeypatch):
    """Update progress from comparison and benchmark callbacks."""

    def compare(*args, **kwargs):
        kwargs["progress_callback"]()
        return {"domain": "example.com"}

    def benchmark(**kwargs):
        kwargs["progress_callback"]("8.8.8.8", 0)
        return [
            {
                "server": "8.8.8.8",
                "avg_response_time": 1,
                "min_response_time": 1,
                "max_response_time": 1,
                "success_rate": 100,
            }
        ]

    monkeypatch.setattr(commands, "compare_dns_servers", compare)
    monkeypatch.setattr(commands, "format_dns_comparison", lambda result: [result])
    assert call("compare_command", "example.com", ("8.8.8.8",), (), quiet=False) == [{"domain": "example.com"}]
    monkeypatch.setattr(commands, "benchmark_dns_servers", benchmark)
    assert (
        call(
            "benchmark_command",
            "example.com",
            (),
            "A",
            1,
            TimeoutConfig(),
            parallel=True,
            quiet=False,
        )[0]["avg_ms"]
        == "1.00"
    )


@pytest.mark.parametrize("cycles,quiet", [(1, False), (0, True)])
def test_dns_monitor_command(monkeypatch, cycles, quiet):
    """Configure monitor defaults and support finite and indefinite runs."""
    result = Mock(to_dict=Mock(return_value={"cycle": 1}))
    monitor = Mock()
    monitor.run_cycles.return_value = [result]
    monitor.history.return_value = [result]
    monitor.report.return_value = "report"

    def make_monitor(config):
        config.alert_callback(SimpleNamespace(alert_type="failure", message="failed"))
        return monitor

    monkeypatch.setattr(commands, "DNSMonitor", make_monitor)
    assert call(
        "monitor_command",
        "example.com",
        (),
        1.0,
        "A",
        1,
        500,
        0.95,
        None,
        cycles,
        TimeoutConfig(),
        no_health=False,
        quiet=quiet,
    ) == [{"cycle": 1}]


def test_monitor_log_report(monkeypatch):
    """Aggregate samples and alerts with optional server filtering."""
    cycles = [
        {
            "samples": [
                {"server": "one", "avg_response_time_ms": 10, "success_rate": 1},
                {"server": "two", "avg_response_time_ms": None},
            ],
            "alerts": [{"server": "one"}, {"server": "two"}],
        }
    ]
    rows = commands._aggregate_log(cycles, None)
    assert rows[0]["avg_rt_ms"] == "10.00"
    assert rows[1]["avg_rt_ms"] == "N/A"
    assert len(commands._aggregate_log(cycles, "one")) == 1
    monkeypatch.setattr(commands, "load_log", Mock(side_effect=[cycles, [], FileNotFoundError()]))
    assert len(call("monitor_report_command", "log", None)) == 2
    with pytest.raises(click.ClickException, match="empty"):
        call("monitor_report_command", "log", None)
    with pytest.raises(click.ClickException, match="not found"):
        call("monitor_report_command", "log", None)
