"""Continuous DNS server health and performance monitoring."""

from __future__ import annotations

import json
import signal
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Any

from nadzoring.dns_lookup.benchmark import benchmark_single_server
from nadzoring.dns_lookup.health import health_check_dns
from nadzoring.dns_lookup.types import RecordType
from nadzoring.dns_lookup.utils import resolve_with_timer
from nadzoring.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_DOMAIN = "google.com"
_DEFAULT_INTERVAL = 60.0
_DEFAULT_MAX_HISTORY = 1440
_DEFAULT_MAX_RT_MS = 500.0
_DEFAULT_MIN_SUCCESS = 0.95
_DEFAULT_QUERIES = 3
_DEFAULT_NAMESERVERS: tuple[str, ...] = ("8.8.8.8", "1.1.1.1")
_HEALTHY_SCORE_THRESHOLD = 80.0


@dataclass
class MonitorConfig:
    """
    Configuration for a DNSMonitor instance.

    Attributes:
        domain: Domain name to query on every check cycle.
        nameservers: DNS server IPs to monitor.
        record_type: DNS record type to query.
        interval: Seconds between successive check cycles.
        queries_per_sample: Queries sent to each server per cycle.
        max_response_time_ms: Alert threshold for average response time
            in milliseconds.
        min_success_rate: Alert threshold for success rate (0.0-1.0).
        run_health_check: Whether to run a full health check each cycle.
            Set to ``False`` for high-frequency monitoring.
        max_history: Maximum cycle results kept in memory.
        log_file: Path to a JSONL file where results are appended.
            ``None`` disables file logging.
        alert_callback: Callable invoked with an :class:`AlertEvent` on
            every threshold breach.

    Example:
        >>> config = MonitorConfig(
        ...     domain="example.com",
        ...     nameservers=["8.8.8.8", "1.1.1.1"],
        ...     interval=30.0,
        ...     max_response_time_ms=200.0,
        ...     log_file="dns_monitor.jsonl",
        ... )

    """

    domain: str = _DEFAULT_DOMAIN
    nameservers: list[str] = field(
        default_factory=lambda: list(_DEFAULT_NAMESERVERS),
    )
    record_type: RecordType = "A"
    interval: float = _DEFAULT_INTERVAL
    queries_per_sample: int = _DEFAULT_QUERIES
    max_response_time_ms: float = _DEFAULT_MAX_RT_MS
    min_success_rate: float = _DEFAULT_MIN_SUCCESS
    run_health_check: bool = True
    max_history: int = _DEFAULT_MAX_HISTORY
    log_file: str | None = None
    alert_callback: Callable[[AlertEvent], None] | None = None


@dataclass
class ServerSample:
    """
    A single performance sample for one DNS server.

    Attributes:
        server: IP address of the queried DNS server.
        timestamp: UTC timestamp of the measurement.
        avg_response_time_ms: Average response time in milliseconds, or
            ``None`` when all queries failed.
        min_response_time_ms: Minimum observed response time, or ``None``.
        max_response_time_ms: Maximum observed response time, or ``None``.
        success_rate: Fraction of successful queries (0.0-1.0).
        records: DNS records returned by the server.
        error: Last error message, or ``None`` on success.

    """

    server: str
    timestamp: datetime
    avg_response_time_ms: float | None
    min_response_time_ms: float | None
    max_response_time_ms: float | None
    success_rate: float
    records: list[str]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Serialise to a JSON-compatible dictionary.

        Returns:
            Dictionary representation of this sample.

        """
        return {
            "server": self.server,
            "timestamp": self.timestamp.isoformat(),
            "avg_response_time_ms": self.avg_response_time_ms,
            "min_response_time_ms": self.min_response_time_ms,
            "max_response_time_ms": self.max_response_time_ms,
            "success_rate": self.success_rate,
            "records": self.records,
            "error": self.error,
        }


@dataclass
class AlertEvent:
    """
    A threshold breach detected during a monitoring cycle.

    Attributes:
        server: IP address or domain of the offending target.
        alert_type: One of ``"resolution_failure"``, ``"high_latency"``,
            ``"low_success_rate"``, or ``"health_degraded"``.
        message: Human-readable description of the breach.
        value: Measured value that triggered the alert, or ``None``.
        threshold: Configured threshold that was breached, or ``None``.
        timestamp: UTC time the alert was raised.

    """

    server: str
    alert_type: str
    message: str
    value: float | None
    threshold: float | None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """
        Serialise to a JSON-compatible dictionary.

        Returns:
            Dictionary representation of this alert.

        """
        return {
            "server": self.server,
            "alert_type": self.alert_type,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CycleResult:
    """
    Aggregated result of one monitoring cycle.

    Attributes:
        cycle: 1-based cycle counter.
        timestamp: UTC timestamp when the cycle started.
        domain: Domain that was queried.
        samples: Per-server performance samples.
        health_score: DNS health score 0-100, or ``None`` when disabled.
        health_status: One of ``"healthy"``, ``"degraded"``,
            ``"unhealthy"``, or ``None``.
        alerts: Alert events raised during this cycle.

    """

    cycle: int
    timestamp: datetime
    domain: str
    samples: list[ServerSample]
    health_score: int | None = None
    health_status: str | None = None
    alerts: list[AlertEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialise to a JSON-compatible dictionary.

        Returns:
            Dictionary representation of this cycle result.

        """
        return {
            "cycle": self.cycle,
            "timestamp": self.timestamp.isoformat(),
            "domain": self.domain,
            "samples": [s.to_dict() for s in self.samples],
            "health_score": self.health_score,
            "health_status": self.health_status,
            "alerts": [a.to_dict() for a in self.alerts],
        }


class DNSMonitor:
    """
    Continuously monitor DNS servers for health and performance.

    Each cycle benchmarks every configured server, optionally runs a
    full health check, evaluates thresholds, dispatches alerts, and
    persists the result to a JSONL log file.

    ``SIGINT`` and ``SIGTERM`` are handled gracefully: the loop finishes
    the current cycle, then stops.

    Args:
        config: Monitoring configuration.

    Example:
        >>> config = MonitorConfig(
        ...     domain="example.com",
        ...     nameservers=["8.8.8.8", "1.1.1.1"],
        ...     interval=60.0,
        ...     log_file="dns_monitor.jsonl",
        ... )
        >>> monitor = DNSMonitor(config)
        >>> monitor.run()

    """

    def __init__(self, config: MonitorConfig) -> None:
        """
        Initialize a DNSMonitor.

        Args:
            config (MonitorConfig): dns monitoring configuration

        """
        self.config = config
        self._history: deque[CycleResult] = deque(maxlen=config.max_history)
        self._running = False
        self._cycle = 0
        self._log_path: Path | None = Path(config.log_file) if config.log_file else None
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def run(self) -> None:
        """
        Start the blocking monitoring loop.

        Runs until :meth:`stop` is called or the process receives
        ``SIGINT`` / ``SIGTERM``.
        """
        self._running = True
        logger.info(
            "DNS monitor starting: domain=%s servers=%s interval=%.0fs",
            self.config.domain,
            self.config.nameservers,
            self.config.interval,
        )
        print(
            f"[nadzoring] Monitoring {self.config.domain}"
            f" every {self.config.interval:.0f}s — Ctrl-C to stop",
            flush=True,
        )
        while self._running:
            self._tick()
            if self._running:
                self._interruptible_sleep(self.config.interval)
        logger.info("DNS monitor stopped after %d cycles.", self._cycle)

    def run_cycles(self, count: int) -> list[CycleResult]:
        """
        Run a fixed number of cycles and return the results.

        Useful for CI pipelines, tests, and cron-based scheduling where
        the caller controls the loop.

        Args:
            count: Number of cycles to execute.

        Returns:
            List of :class:`CycleResult` objects, one per executed cycle.

        Example:
            >>> results = monitor.run_cycles(10)
            >>> print(len(results))
            10

        """
        self._running = True
        for i in range(count):
            self._tick()
            if not self._running:
                break
            if i < count - 1:
                self._interruptible_sleep(self.config.interval)
        self._running = False
        return self.history()

    def stop(self) -> None:
        """Signal the monitoring loop to stop after the current cycle."""
        self._running = False

    def history(self) -> list[CycleResult]:
        """
        Return a snapshot of the in-memory monitoring history.

        Returns:
            List of :class:`CycleResult` objects, oldest first.

        """
        return list(self._history)

    def report(self) -> str:
        """
        Return a human-readable session summary.

        Computes per-server mean, stdev, min, and max response times,
        overall success rates, and health score trends across the full
        in-memory history.

        Returns:
            Multi-line string for printing or logging.

        Example:
            >>> monitor.run_cycles(5)
            >>> print(monitor.report())

        """
        if not self._history:
            return "No monitoring data collected yet."

        lines = [
            "=" * 60,
            f"DNS Monitor Report — {self.config.domain}",
            f"Cycles : {self._cycle}",
            (
                f"Range  : {self._history[0].timestamp.isoformat()}"
                f" → {self._history[-1].timestamp.isoformat()}"
            ),
            "=" * 60,
        ]
        for server in self.config.nameservers:
            lines.extend(self._server_report_lines(server))

        health_scores = [
            c.health_score for c in self._history if c.health_score is not None
        ]
        if health_scores:
            lines += [
                "",
                f"Health (last) : {health_scores[-1]}",
                f"Health (avg)  : {mean(health_scores):.1f}",
                f"Health (min)  : {min(health_scores)}",
            ]
        lines.append("=" * 60)
        return "\n".join(lines)

    def _tick(self) -> None:
        self._cycle += 1
        result = self._build_cycle_result()
        self._history.append(result)
        self._append_log(result)
        self._print_summary(result)

    def _build_cycle_result(self) -> CycleResult:
        ts = datetime.now(UTC)
        samples = [self._sample_server(srv, ts) for srv in self.config.nameservers]
        health_score, health_status = self._run_health_check()
        alerts = evaluate_thresholds(samples, health_score, health_status, self.config)
        self._dispatch_alerts(alerts)
        return CycleResult(
            cycle=self._cycle,
            timestamp=ts,
            domain=self.config.domain,
            samples=samples,
            health_score=health_score,
            health_status=health_status,
            alerts=alerts,
        )

    def _sample_server(self, server: str, ts: datetime) -> ServerSample:
        try:
            bench = benchmark_single_server(
                server=server,
                domain=self.config.domain,
                record_type=self.config.record_type,
                queries=self.config.queries_per_sample,
                delay=0.0,
            )
            resolved = resolve_with_timer(
                self.config.domain,
                self.config.record_type,
                server,
            )
            return ServerSample(
                server=server,
                timestamp=ts,
                avg_response_time_ms=(
                    bench["avg_response_time"] if bench["success_rate"] > 0 else None
                ),
                min_response_time_ms=bench["min_response_time"] or None,
                max_response_time_ms=bench["max_response_time"] or None,
                success_rate=bench["success_rate"] / 100.0,
                records=resolved.get("records", []),
                error=resolved.get("error"),
            )
        except Exception as exc:
            logger.exception("Sampling failed for server %s", server)
            return ServerSample(
                server=server,
                timestamp=ts,
                avg_response_time_ms=None,
                min_response_time_ms=None,
                max_response_time_ms=None,
                success_rate=0.0,
                records=[],
                error=str(exc),
            )

    def _run_health_check(self) -> tuple[int | None, str | None]:
        if not self.config.run_health_check:
            return None, None
        try:
            result = health_check_dns(
                self.config.domain,
                self.config.nameservers[0],
            )
            return result["score"], result["status"]
        except Exception:
            logger.warning("Health check failed on cycle %d", self._cycle)
            return None, None

    def _dispatch_alerts(self, alerts: list[AlertEvent]) -> None:
        if not self.config.alert_callback or not alerts:
            return
        for alert in alerts:
            try:
                self.config.alert_callback(alert)
            except Exception:
                logger.warning("Alert callback raised on cycle %d", self._cycle)

    def _append_log(self, result: CycleResult) -> None:
        if self._log_path is None:
            return
        try:
            with self._log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            logger.warning("Could not write to log file %s", self._log_path)

    def _print_summary(self, result: CycleResult) -> None:
        ts = result.timestamp.strftime("%H:%M:%S")
        for i, s in enumerate(result.samples):
            rt = f"{s.avg_response_time_ms:.1f}ms" if s.avg_response_time_ms else "N/A"
            health = (
                f"  health={result.health_score}/{result.health_status}"
                if i == 0 and result.health_score is not None
                else ""
            )
            print(
                f"[{ts}] #{result.cycle:4d}  {s.server:15s}"
                f"  rt={rt:8s}  ok={s.success_rate * 100:.0f}%{health}",
                flush=True,
            )
        for alert in result.alerts:
            print(f"  ⚠  [{alert.alert_type}] {alert.message}", flush=True)

    def _interruptible_sleep(self, seconds: float) -> None:
        deadline = time.monotonic() + seconds
        while self._running and time.monotonic() < deadline:
            time.sleep(min(1.0, deadline - time.monotonic()))

    def _handle_signal(self, _signum: int, _frame: object) -> None:
        print("\n[nadzoring] Stopping monitor…", flush=True)
        self._running = False

    def _server_report_lines(self, server: str) -> list[str]:
        samples = [s for c in self._history for s in c.samples if s.server == server]
        if not samples:
            return []

        rts = [s.avg_response_time_ms for s in samples if s.avg_response_time_ms]
        success_rates = [s.success_rate for s in samples]
        alert_count = sum(
            1 for c in self._history for a in c.alerts if a.server == server
        )
        lines = [f"\nServer : {server}", f"  Samples : {len(samples)}"]
        if rts:
            sd = f" ± {stdev(rts):.2f}" if len(rts) > 1 else ""
            lines += [
                f"  Avg RT  : {mean(rts):.2f}ms{sd}",
                f"  Min RT  : {min(rts):.2f}ms",
                f"  Max RT  : {max(rts):.2f}ms",
            ]
        lines += [
            f"  Success : {mean(success_rates) * 100:.1f}%",
            f"  Alerts  : {alert_count}",
        ]
        return lines


def evaluate_thresholds(
    samples: list[ServerSample],
    health_score: int | None,
    health_status: str | None,
    config: MonitorConfig,
) -> list[AlertEvent]:
    """
    Evaluate samples against configured thresholds.

    Args:
        samples: Per-server samples from the current cycle.
        health_score: DNS health score 0-100, or ``None``.
        health_status: Health status string, or ``None``.
        config: Monitor configuration holding the threshold values.

    Returns:
        List of :class:`AlertEvent` objects; empty when all metrics are
        within configured thresholds.

    """
    alerts: list[AlertEvent] = []
    ts = datetime.now(UTC)

    for s in samples:
        if s.success_rate == 0.0:
            alerts.append(
                AlertEvent(
                    server=s.server,
                    alert_type="resolution_failure",
                    message=(
                        f"[{s.server}] Complete failure for {config.domain}: {s.error}"
                    ),
                    value=0.0,
                    threshold=config.min_success_rate,
                    timestamp=ts,
                )
            )
            continue

        if (
            s.avg_response_time_ms is not None
            and s.avg_response_time_ms > config.max_response_time_ms
        ):
            alerts.append(
                AlertEvent(
                    server=s.server,
                    alert_type="high_latency",
                    message=(
                        f"[{s.server}] Latency {s.avg_response_time_ms:.1f}ms"
                        f" > {config.max_response_time_ms:.0f}ms"
                    ),
                    value=s.avg_response_time_ms,
                    threshold=config.max_response_time_ms,
                    timestamp=ts,
                )
            )

        if s.success_rate < config.min_success_rate:
            alerts.append(
                AlertEvent(
                    server=s.server,
                    alert_type="low_success_rate",
                    message=(
                        f"[{s.server}] Success {s.success_rate * 100:.1f}%"
                        f" < {config.min_success_rate * 100:.0f}%"
                    ),
                    value=s.success_rate,
                    threshold=config.min_success_rate,
                    timestamp=ts,
                )
            )

    if health_status in ("degraded", "unhealthy"):
        alerts.append(
            AlertEvent(
                server=config.domain,
                alert_type="health_degraded",
                message=(
                    f"Health for {config.domain} is {health_status}"
                    f" (score={health_score})"
                ),
                value=float(health_score) if health_score is not None else None,
                threshold=_HEALTHY_SCORE_THRESHOLD,
                timestamp=ts,
            )
        )

    return alerts


def load_log(path: str | Path) -> list[dict[str, Any]]:
    """
    Load a JSONL monitoring log written by :class:`DNSMonitor`.

    Args:
        path: Path to the ``.jsonl`` file.

    Returns:
        List of cycle-result dictionaries, one per non-empty line.

    Raises:
        FileNotFoundError: If *path* does not exist.

    Example:
        >>> cycles = load_log("dns_monitor.jsonl")
        >>> rts = [
        ...     s["avg_response_time_ms"]
        ...     for c in cycles
        ...     for s in c["samples"]
        ...     if s["avg_response_time_ms"] is not None
        ... ]
        >>> print(f"Mean RT: {sum(rts) / len(rts):.2f}ms")

    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Log file not found: {path}")
    results: list[dict[str, Any]] = []
    with p.open(encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning("Skipping malformed line %d in %s", lineno, p)
    return results
