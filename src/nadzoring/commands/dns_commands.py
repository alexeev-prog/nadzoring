"""DNS-related CLI commands."""

from __future__ import annotations

from logging import Logger
from typing import Any, Never

import click
from click import Choice
from tqdm import tqdm

from nadzoring.dns_lookup import (
    RECORD_TYPES,
    benchmark_dns_servers,
    check_dns,
    check_dns_poisoning,
    compare_dns_servers,
    health_check_dns,
    resolve_dns,
    reverse_dns,
    trace_dns,
)
from nadzoring.dns_lookup.compare import ServerComparisonResult
from nadzoring.dns_lookup.health import DetailedCheckResult, HealthCheckResult
from nadzoring.dns_lookup.monitor import AlertEvent, CycleResult, DNSMonitor, MonitorConfig, load_log
from nadzoring.dns_lookup.types import BenchmarkResult, DNSResult, PoisoningCheckResult, RecordType
from nadzoring.logger import get_logger
from nadzoring.network_base.whois_lookup import whois_domain_lookup
from nadzoring.utils.decorators import common_cli_options
from nadzoring.utils.formatters import (
    format_dns_comparison,
    format_dns_health,
    format_dns_poisoning,
    format_dns_record,
    format_dns_trace,
)
from nadzoring.utils.timeout import TimeoutConfig

logger: Logger = get_logger(__name__)

_QUERYABLE_RECORD_TYPES: list[RecordType] = [t for t in RECORD_TYPES if t != "PTR"]  # type: ignore

_DEFAULT_NAMESERVERS: tuple[str, str] = ("8.8.8.8", "1.1.1.1")

_RECORD_TYPE_CHOICE: Choice = click.Choice(
    ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "ALL"],
    case_sensitive=False,
)


def _expand_record_types(record_types: tuple[str, ...]) -> list[RecordType]:
    """
    Expand a tuple of CLI record type tokens into a concrete list.

    Replaces the special ``ALL`` token with every queryable record type
    (i.e. all types except ``PTR``).

    Args:
        record_types: Tuple of record type strings as received from Click.

    Returns:
        Flat list of concrete DNS record type strings.

    """
    if "ALL" in record_types:
        return _QUERYABLE_RECORD_TYPES

    valid_types: list[str] = [t for t in record_types if t in _QUERYABLE_RECORD_TYPES]
    return valid_types  # type: ignore[return-value]


def _make_pbar(
    total: int,
    desc: str,
    unit: str,
    *,
    quiet: bool,
) -> tqdm[Never] | None:
    """
    Create a tqdm progress bar or return ``None`` when in quiet mode.

    Args:
        total: Total number of steps.
        desc: Initial description label.
        unit: Unit label for the progress bar.
        quiet: When ``True``, no progress bar is created.

    Returns:
        A :class:`tqdm` instance, or ``None`` if *quiet* is ``True``.

    """
    if quiet:
        return None
    return tqdm(total=total, desc=desc, unit=unit)


@click.group(name="dns")
def dns_group() -> None:
    """DNS lookup and analysis commands."""


@dns_group.command(name="whois")
@click.argument("domain", required=True)
@common_cli_options(include_quiet=True)
def whois_command(domain: str, *, quiet: bool) -> list[dict[str, str]]:
    """Perform a WHOIS lookup for a domain."""
    _ = quiet
    result = whois_domain_lookup(domain)
    if result and "error" in result[0]:
        raise click.ClickException(result[0]["error"])
    return result


@dns_group.command(name="monitor")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("domain", required=True)
@click.option(
    "--nameservers",
    "-n",
    multiple=True,
    help="DNS server IP to monitor (repeatable).",
)
@click.option(
    "--interval",
    "-i",
    type=float,
    default=60.0,
    show_default=True,
    help="Seconds between monitoring cycles.",
)
@click.option(
    "--type",
    "-t",
    "record_type",
    default="A",
    show_default=True,
    type=click.Choice(["A", "AAAA", "MX", "NS", "TXT"]),
    help="DNS record type to query each cycle.",
)
@click.option(
    "--queries",
    "-q",
    type=int,
    default=3,
    show_default=True,
    help="Queries sent to each server per cycle.",
)
@click.option(
    "--max-rt",
    type=float,
    default=500.0,
    show_default=True,
    help="Alert threshold: max average response time (ms).",
)
@click.option(
    "--min-success",
    type=float,
    default=0.95,
    show_default=True,
    help="Alert threshold: minimum success rate (0-1).",
)
@click.option(
    "--no-health",
    is_flag=True,
    help="Skip DNS health check each cycle (faster for high-frequency use).",
)
@click.option(
    "--log-file",
    "-l",
    default=None,
    help="JSONL file to append all cycle results to.",
)
@click.option(
    "--cycles",
    "-c",
    type=int,
    default=0,
    show_default=True,
    help="Stop after N cycles (0 = run indefinitely).",
)
def monitor_command(
    domain: str,
    nameservers: tuple[str, ...],
    interval: float,
    record_type: str,
    queries: int,
    max_rt: float,
    min_success: float,
    log_file: str | None,
    cycles: int,
    timeout_config: TimeoutConfig,
    *,
    no_health: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    r"""
    Continuously monitor DNS server health and performance over time.

    Runs periodic check cycles against one or more DNS servers, tracking
    response times, success rates, and DNS health scores. Fires alerts
    when thresholds are breached and optionally persists all results to a
    JSONL log file.

    Args:
        domain: Domain name to query on every cycle.
        nameservers: DNS server IPs to monitor.
        interval: Seconds between monitoring cycles.
        record_type: DNS record type to query.
        queries: Queries sent to each server per cycle.
        max_rt: Alert threshold for average response time in ms.
        min_success: Alert threshold for success rate (0-1).
        log_file: Path to JSONL log file, or ``None``.
        cycles: Number of cycles to run (0 = indefinite).
        no_health: When ``True``, skip the DNS health check each cycle.
        quiet: When ``True``, suppress all console output.
        timeout_config: unified timeout configuration.

    Returns:
        List of cycle-result dictionaries for ``--output`` formatting.

    Example:
        .. code-block:: bash

            nadzoring dns monitor example.com \\
                -n 8.8.8.8 -n 1.1.1.1 \\
                --interval 30 \\
                --log-file dns_monitor.jsonl

    """
    servers = list(nameservers) if nameservers else list(_DEFAULT_NAMESERVERS)

    def _alert_cb(alert: AlertEvent) -> None:
        if not quiet:
            click.secho(
                f"  ⚠  [{alert.alert_type.upper()}] {alert.message}",
                fg="red",
                err=True,
            )

    record_type_literal: RecordType = record_type  # type: ignore
    config = MonitorConfig(
        domain=domain,
        nameservers=servers,
        record_type=record_type_literal,
        interval=interval,
        queries_per_sample=queries,
        max_response_time_ms=max_rt,
        min_success_rate=min_success,
        run_health_check=not no_health,
        log_file=log_file,
        alert_callback=_alert_cb,
        timeout_config=timeout_config,
    )
    monitor = DNSMonitor(config)

    if cycles > 0:
        results: list[CycleResult] = monitor.run_cycles(cycles)
    else:
        monitor.run()
        results = monitor.history()

    if not quiet:
        click.echo("\n" + monitor.report(), err=True)

    return [c.to_dict() for c in results]


@dns_group.command(name="monitor-report")
@common_cli_options()
@click.argument("log_file", required=True)
@click.option(
    "--server",
    "-s",
    default=None,
    help="Filter statistics to a specific server IP.",
)
def monitor_report_command(
    log_file: str,
    server: str | None,
) -> list[dict[str, Any]]:
    r"""
    Analyse a JSONL monitoring log and return aggregated statistics.

    Args:
        log_file: Path to the JSONL file produced by ``dns monitor``.
        server: Optional server IP to filter statistics to.

    Returns:
        List of per-server statistic rows for ``--output`` formatting.

    Raises:
        click.ClickException: If the log file is missing or empty.

    Example:
        .. code-block:: bash

            nadzoring dns monitor-report dns_monitor.jsonl
            nadzoring dns monitor-report dns_monitor.jsonl -s 8.8.8.8
            nadzoring dns monitor-report dns_monitor.jsonl \\
                -o json --save report.json

    """
    try:
        cycles: list[dict[str, Any]] = load_log(log_file)
    except FileNotFoundError:
        raise click.ClickException(f"Log file not found: {log_file}") from None

    if not cycles:
        raise click.ClickException("Log file is empty.")

    return _aggregate_log(cycles, server)


def _aggregate_log(
    cycles: list[dict[str, Any]],
    server_filter: str | None,
) -> list[dict[str, Any]]:
    """
    Aggregate per-server statistics from raw cycle dictionaries.

    Args:
        cycles: List of cycle-result dictionaries from :func:`load_log`.
        server_filter: When set, only include data for this server IP.

    Returns:
        List of aggregated per-server statistic rows.

    """
    rts: dict[str, list[float]] = {}
    successes: dict[str, list[float]] = {}
    alert_counts: dict[str, int] = {}

    for cycle in cycles:
        for s in cycle.get("samples", []):
            srv: str = s.get("server", "unknown")
            if server_filter and srv != server_filter:
                continue
            rts.setdefault(srv, [])
            successes.setdefault(srv, [])
            alert_counts.setdefault(srv, 0)
            rt: float | None = s.get("avg_response_time_ms")
            if rt is not None:
                rts[srv].append(rt)
            successes[srv].append(s.get("success_rate", 0.0))

        for alert in cycle.get("alerts", []):
            srv = alert.get("server", "unknown")
            if server_filter and srv != server_filter:
                continue
            alert_counts[srv] = alert_counts.get(srv, 0) + 1

    rows: list[dict[str, Any]] = []
    for srv, rt_list in rts.items():
        ok_list: list[float] = successes.get(srv, [])
        rows.append({
            "server": srv,
            "samples": len(rt_list),
            "avg_rt_ms": f"{sum(rt_list) / len(rt_list):.2f}" if rt_list else "N/A",
            "min_rt_ms": f"{min(rt_list):.2f}" if rt_list else "N/A",
            "max_rt_ms": f"{max(rt_list):.2f}" if rt_list else "N/A",
            "avg_success_pct": (f"{sum(ok_list) / len(ok_list) * 100:.1f}" if ok_list else "N/A"),
            "total_alerts": alert_counts.get(srv, 0),
        })
    return rows


@dns_group.command(name="resolve")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("domains", nargs=-1, required=True)
@click.option(
    "--type",
    "-t",
    "record_types",
    multiple=True,
    type=_RECORD_TYPE_CHOICE,
    default=["A"],
    help="DNS record type to query (repeatable; use ALL for every type).",
)
@click.option("--nameserver", "-n", help="Specific nameserver to use.")
@click.option("--short", is_flag=True, help="Compact output (like host command style).")
@click.option("--show-ttl", is_flag=True, help="Include TTL value for each record.")
@click.option(
    "--format-style",
    type=click.Choice(["standard", "bind", "host", "dig"]),
    default="standard",
    help="Output format style.",
)
def resolve_command(
    domains: tuple[str, ...],
    record_types: tuple[str, ...],
    nameserver: str | None,
    format_style: str,
    timeout_config: TimeoutConfig,
    *,
    quiet: bool,
    short: bool,
    show_ttl: bool,
) -> list[dict[str, Any]]:
    """Resolve DNS records for one or more domains."""
    types_to_query: list[RecordType] = _expand_record_types(record_types)
    total: int = len(domains) * len(types_to_query)

    pbar: tqdm[Never] | None = _make_pbar(total, "Resolving DNS records", "query", quiet=quiet)

    results: list[dict[str, Any]] = []

    for domain in domains:
        domain_result: dict[str, Any] = {"domain": domain, "records": {}}

        for rtype in types_to_query:
            result: DNSResult = resolve_dns(
                domain=domain,
                record_type=rtype,
                nameserver=nameserver,
                include_ttl=show_ttl,
                timeout_config=timeout_config,
            )
            domain_result["records"][rtype] = result

            if pbar:
                pbar.set_description(f"Resolving {domain} {rtype}")
                pbar.update(1)

        results.append(domain_result)

    if pbar:
        pbar.close()

    style: str = "short" if short else format_style
    return format_dns_record(results, style=style, show_ttl=show_ttl)


@dns_group.command(name="reverse")
@common_cli_options(include_quiet=True)
@click.argument("ip_addresses", nargs=-1, required=True)
@click.option("--nameserver", "-n", help="Specific nameserver to use.")
def reverse_command(
    ip_addresses: tuple[str, ...],
    nameserver: str | None,
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Perform a reverse DNS lookup for one or more IP addresses.

    Queries PTR records to resolve each IP address to its associated
    hostname. Results include the original IP, resolved hostname, and
    query response time.

    Args:
        ip_addresses: One or more IP addresses to look up.
        nameserver: Optional DNS server to use instead of the system default.
        quiet: Suppress progress bar output when ``True``.

    Returns:
        List of dicts with keys ``ip_address``, ``hostname``, and
        ``response_time_ms`` for each queried address.

    """
    pbar: tqdm[Never] | None = _make_pbar(len(ip_addresses), "Performing reverse lookups", "lookup", quiet=quiet)

    results: list[dict[str, Any]] = []

    for ip in ip_addresses:
        result: dict[str, Any] = reverse_dns(ip, nameserver)
        results.append({
            "ip_address": result["ip_address"],
            "hostname": result["hostname"] or "Not found",
            "response_time_ms": result["response_time"] or "N/A",
        })

        if pbar:
            pbar.set_description(f"Looking up {ip}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@dns_group.command(name="check")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("domains", nargs=-1, required=True)
@click.option("--nameserver", "-n", help="Specific nameserver to use.")
@click.option(
    "--types",
    "-t",
    "record_types",
    multiple=True,
    type=_RECORD_TYPE_CHOICE,
    default=["ALL"],
    help="DNS record types to check (repeatable; default: ALL).",
)
def check_command(
    domains: tuple[str, ...],
    nameserver: str | None,
    record_types: tuple[str, ...],
    timeout_config: TimeoutConfig,
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Perform a comprehensive DNS check for one or more domains.

    Validates MX priorities, SPF/DKIM TXT records, and reports any
    resolution errors per record type.

    Args:
        domains: One or more domain names to check.
        nameserver: Optional DNS server to use instead of the system default.
        record_types: Record types to query; ``ALL`` expands to every
            supported type except PTR.
        quiet: Suppress progress bar output when ``True``.
        timeout_config: unified timeout configuration.

    Returns:
        List of dicts with one entry per domain. Each entry contains the
        domain name and a column per record type with its resolved value
        or an error string.

    """
    types_to_check: list[RecordType] = _expand_record_types(record_types)

    pbar: tqdm[Never] | None = _make_pbar(len(domains), "Performing DNS checks", "domain", quiet=quiet)

    results: list[dict[str, Any]] = []

    for domain in domains:
        result: DetailedCheckResult = check_dns(
            domain=domain,
            nameserver=nameserver,
            record_types=types_to_check,
            validate_mx=True,
            validate_txt=True,
            timeout_config=timeout_config,
        )

        row: dict[str, Any] = {"domain": domain}

        for rtype in types_to_check:
            if rtype in result["records"] and result["records"][rtype]:
                if rtype == "MX":
                    row[rtype] = "\n".join(f"Priority {r}" for r in result["records"][rtype])
                else:
                    row[rtype] = "\n".join(result["records"][rtype])
            elif rtype in result["errors"]:
                row[rtype] = f"[{result['errors'][rtype]}]"
            else:
                row[rtype] = "None"

        results.append(row)

        if pbar:
            pbar.set_description(f"Checking {domain}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@dns_group.command(name="trace")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("domain", required=True)
@click.option("--nameserver", "-n", help="Starting nameserver to use.")
def trace_command(
    domain: str,
    nameserver: str | None,
    timeout_config: TimeoutConfig,
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Trace the full DNS resolution path for a domain."""
    if not quiet:
        click.echo(f"Tracing DNS for {domain}...", err=True)

    result: dict[str, Any] = trace_dns(
        domain,
        nameserver,
        timeout_config=timeout_config,
    )
    return format_dns_trace(result)


@dns_group.command(name="compare")
@common_cli_options(include_quiet=True)
@click.argument("domain", required=True)
@click.option(
    "--servers",
    "-s",
    multiple=True,
    default=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
    help="DNS servers to compare (repeatable).",
)
@click.option(
    "--type",
    "-t",
    "record_types",
    multiple=True,
    default=["A"],
    help="Record types to compare (repeatable).",
)
def compare_command(
    domain: str,
    servers: tuple[str, ...],
    record_types: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Compare DNS responses for a domain across multiple nameservers."""
    types_to_query: list[str] = list(record_types) if record_types else ["A"]
    total: int = len(servers) * len(types_to_query)

    pbar: tqdm[Never] | None = _make_pbar(total, "Comparing DNS servers", "query", quiet=quiet)

    def progress_callback() -> None:
        if pbar:
            pbar.update(1)

    result: ServerComparisonResult = compare_dns_servers(
        domain,
        list(servers),
        types_to_query,
        progress_callback=progress_callback if not quiet else None,
    )

    if pbar:
        pbar.close()

    return format_dns_comparison(dict(result))


@dns_group.command(name="health")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("domain", required=True)
@click.option("--nameserver", "-n", help="Nameserver to use for health checks.")
def health_command(
    domain: str,
    nameserver: str | None,
    timeout_config: TimeoutConfig,
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Run a comprehensive DNS health check for a domain."""
    if not quiet:
        click.echo(f"Checking DNS health for {domain}...", err=True)

    result: HealthCheckResult = health_check_dns(
        domain,
        nameserver,
        timeout_config=timeout_config,
    )
    return format_dns_health(dict(result))


@dns_group.command(name="benchmark")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.option(
    "--domain",
    "-d",
    default="google.com",
    show_default=True,
    help="Domain to use for benchmarking.",
)
@click.option(
    "--servers",
    "-s",
    multiple=True,
    help="DNS servers to benchmark (repeatable; defaults to public resolvers).",
)
@click.option(
    "--type",
    "-t",
    "record_type",
    default="A",
    show_default=True,
    type=click.Choice(["A", "AAAA", "MX", "NS", "TXT"]),
    help="Record type to query.",
)
@click.option(
    "--queries",
    "-q",
    default=10,
    show_default=True,
    type=int,
    help="Number of queries per server.",
)
@click.option(
    "--parallel/--sequential",
    default=True,
    help="Run benchmarks in parallel (default) or sequentially.",
)
def benchmark_command(
    domain: str,
    servers: tuple[str, ...],
    record_type: str,
    queries: int,
    timeout_config: TimeoutConfig,
    *,
    parallel: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Benchmark DNS server performance."""
    if not quiet:
        click.echo(f"Benchmarking DNS servers for {domain}...", err=True)

    servers_list: list[str] | None = list(servers) if servers else None
    total_servers: int = len(servers_list) if servers_list else 10

    pbar: tqdm[Never] | None = _make_pbar(total_servers, "Benchmarking servers", "server", quiet=quiet)

    def progress_callback(server: str, _index: int) -> None:
        if pbar:
            pbar.set_description(f"Benchmarking {server}")
            pbar.update(1)

    record_type_literal: RecordType = record_type  # type: ignore
    results: list[BenchmarkResult] = benchmark_dns_servers(
        domain=domain,
        servers=servers_list,
        record_type=record_type_literal,
        queries=queries,
        parallel=parallel,
        progress_callback=progress_callback if not quiet else None,
        timeout_config=timeout_config,
    )

    if pbar:
        pbar.close()

    return [
        {
            "server": r["server"],
            "avg_ms": f"{r['avg_response_time']:.2f}",
            "min_ms": f"{r['min_response_time']:.2f}",
            "max_ms": f"{r['max_response_time']:.2f}",
            "success_rate": f"{r['success_rate']}%",
        }
        for r in results
    ]


@dns_group.command(name="poisoning")
@common_cli_options(include_timeout=True)
@click.argument("domain", required=True)
@click.option(
    "--control-server",
    "-c",
    default="8.8.8.8",
    show_default=True,
    help="Trusted control server used as reference.",
)
@click.option(
    "--test-servers",
    "-t",
    multiple=True,
    help="Servers to test against the control.",
)
@click.option(
    "--type",
    "-T",
    "record_type",
    default="A",
    show_default=True,
    help="Record type to check.",
)
@click.option(
    "--additional-types",
    "-a",
    multiple=True,
    help="Extra record types to query on the control server.",
)
def poisoning_command(
    domain: str,
    control_server: str,
    test_servers: tuple[str, ...],
    record_type: str,
    additional_types: tuple[str, ...],
    timeout_config: TimeoutConfig,
) -> list[dict[str, Any]]:
    """Detect DNS poisoning, censorship, or CDN routing variations for a domain."""
    test_servers_list: list[str] | None = list(test_servers) if test_servers else None
    additional: list[str] | None = list(additional_types) if additional_types else None

    result: PoisoningCheckResult = check_dns_poisoning(
        domain,
        control_server,
        test_servers_list,
        record_type,
        additional,
        timeout_config=timeout_config,
    )

    return format_dns_poisoning(dict(result))
