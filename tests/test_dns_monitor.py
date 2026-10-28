"""DNS monitor lifecycle, thresholds, persistence, and signal tests."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from nadzoring.dns_lookup import monitor as monitoring


@pytest.fixture
def monitor(monkeypatch):
    """Build a monitor without changing process signal handlers."""
    monkeypatch.setattr(monitoring.signal, "signal", Mock())
    monkeypatch.setattr(
        monitoring,
        "benchmark_single_server",
        Mock(
            return_value={
                "avg_response_time": 600,
                "min_response_time": 500,
                "max_response_time": 700,
                "success_rate": 50,
            }
        ),
    )
    monkeypatch.setattr(monitoring, "resolve_with_timer", Mock(return_value={"records": ["192.0.2.1"], "error": None}))
    monkeypatch.setattr(monitoring, "health_check_dns", Mock(return_value={"score": 60, "status": "degraded"}))
    return monitoring.DNSMonitor(monitoring.MonitorConfig(nameservers=["192.0.2.53"], interval=0))


def test_monitor_cycles_and_report(monitor, tmp_path, capsys):
    """Collect samples, dispatch alerts, persist JSONL, and summarize history."""
    assert monitor.report() == "No monitoring data collected yet."
    monitor._log_path = tmp_path / "monitor.jsonl"
    callback = Mock()
    monitor.config.alert_callback = callback
    results = monitor.run_cycles(2)
    assert len(results) == 2
    assert callback.call_count == 6
    assert len(monitoring.load_log(monitor._log_path)) == 2
    assert results[0].to_dict()["samples"][0]["success_rate"] == 0.5
    assert results[0].to_dict()["alerts"][0]["alert_type"] == "high_latency"
    report = monitor.report()
    assert "Health (avg)  : 60.0" in report
    assert "Avg RT" in report
    assert "±" in report
    assert monitor._server_report_lines("absent") == []
    assert "health=60/degraded" in capsys.readouterr().out
    monitor.config.alert_callback = None
    monitor._log_path = None
    monitor.run_cycles(1)


def test_monitor_error_paths(monitor, monkeypatch, tmp_path):
    """Keep sampling and logging failures isolated to their own results."""
    monkeypatch.setattr(monitoring, "benchmark_single_server", Mock(side_effect=RuntimeError("failed")))
    monkeypatch.setattr(monitoring, "health_check_dns", Mock(side_effect=RuntimeError("failed")))
    monitor.config.alert_callback = Mock(side_effect=RuntimeError("callback"))
    monitor._log_path = tmp_path / "missing" / "monitor.jsonl"
    result = monitor.run_cycles(1)[0]
    assert result.samples[0].error == "failed"
    assert result.samples[0].avg_response_time_ms is None
    assert result.health_score is None
    assert [alert.alert_type for alert in result.alerts] == ["resolution_failure"]
    assert "Success : 0.0%" in monitor.report()
    monitor.config.run_health_check = False
    assert monitor._run_health_check() == (None, None)
    monkeypatch.setattr(
        monitoring,
        "benchmark_single_server",
        Mock(
            return_value={
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "success_rate": 0,
            }
        ),
    )
    sample = monitor._sample_server("192.0.2.53", datetime.now(UTC))
    assert sample.avg_response_time_ms is None


def test_monitor_run_stop_and_signal(monitor, monkeypatch):
    """Stop indefinite loops after a completed cycle without real signals."""

    def step():
        if tick.call_count == 2:
            monitor.stop()

    tick = Mock(side_effect=step)
    monkeypatch.setattr(monitor, "_tick", tick)
    sleep = Mock()
    monkeypatch.setattr(monitor, "_interruptible_sleep", sleep)
    monitor.run()
    assert tick.call_count == 2
    sleep.assert_called_once_with(0)
    monkeypatch.setattr(monitor, "_tick", Mock(side_effect=lambda: monitor._handle_signal(15, None)))
    assert monitor.run_cycles(5) == []
    assert not monitor._running


def test_interruptible_sleep(monitor, monkeypatch):
    """Sleep in short increments and honor a stop request."""
    monitor._running = True
    monkeypatch.setattr(monitoring.time, "monotonic", Mock(side_effect=[0, 0, 0, 2]))
    sleep = Mock()
    monkeypatch.setattr(monitoring.time, "sleep", sleep)
    monitor._interruptible_sleep(1)
    sleep.assert_called_once_with(1)


def test_thresholds_and_log_loading(tmp_path):
    """Handle empty thresholds, null health scores, and malformed log lines."""
    config = monitoring.MonitorConfig()
    assert monitoring.evaluate_thresholds([], None, None, config) == []
    alert = monitoring.evaluate_thresholds([], None, "unhealthy", config)[0]
    assert alert.value is None
    assert alert.to_dict()["threshold"] == 80
    path = tmp_path / "monitor.jsonl"
    with pytest.raises(FileNotFoundError, match="Log file not found"):
        monitoring.load_log(path)
    path.write_text('\n{"cycle": 1}\ninvalid\n', encoding="utf-8")
    assert monitoring.load_log(path) == [{"cycle": 1}]
