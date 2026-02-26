# nadzoring/commands/dns_commands.py
"""DNS-related CLI commands."""

from logging import Logger
from typing import Any, NoReturn

import click
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
from nadzoring.dns_lookup.types import BenchmarkResult, DNSResult, PoisoningCheckResult
from nadzoring.logger import get_logger
from nadzoring.utils.decorators import common_cli_options
from nadzoring.utils.formatters import (
    format_dns_comparison,
    format_dns_health,
    format_dns_poisoning,
    format_dns_record,
    format_dns_trace,
)

logger: Logger = get_logger(__name__)


@click.group(name="dns")
def dns() -> None:
    """DNS lookup and analysis commands."""


@dns.command(name="resolve")
@common_cli_options(include_quiet=True)
@click.argument("domains", nargs=-1, required=True)
@click.option(
    "--type",
    "-t",
    "record_types",
    multiple=True,
    type=click.Choice(
        ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "ALL"], case_sensitive=False
    ),
    default=["A"],
    help="DNS record type to query (can be used multiple times, use ALL for all types)",
)
@click.option("--nameserver", "-n", help="Specific nameserver to use")
@click.option("--short", is_flag=True, help="Compact output (like host command style)")
@click.option("--show-ttl", is_flag=True, help="Show TTL for each record")
@click.option(
    "--format-style",
    type=click.Choice(["standard", "bind", "host", "dig"]),
    default="standard",
    help="Output format style",
)
def resolve_command(
    domains: tuple[str, ...],
    record_types: tuple[str, ...],
    nameserver: str | None,
    format_style: str,
    *,
    quiet: bool,
    short: bool,
    show_ttl: bool,
) -> list[dict]:
    """Resolve DNS records for one or more domains."""
    types_to_query: list[str] = list(record_types)
    if "ALL" in types_to_query:
        types_to_query: list[str] = [t for t in RECORD_TYPES if t != "PTR"]

    results: list[dict[str, dict[str, DNSResult] | str]] = []
    total = len(domains) * len(types_to_query)

    pbar: tqdm[NoReturn] | None = (
        None if quiet else tqdm(total=total, desc="Resolving DNS records", unit="query")
    )

    for domain in domains:
        domain_result: dict[str, dict[str, DNSResult] | str] = {
            "domain": domain,
            "records": {},
        }
        for rtype in types_to_query:
            result: DNSResult = resolve_dns(
                domain=domain,
                record_type=rtype,
                nameserver=nameserver,
                include_ttl=show_ttl,
            )
            domain_result["records"][rtype] = result
            if pbar:
                pbar.set_description(f"Resolving {domain} {rtype}")
                pbar.update(1)
        results.append(domain_result)

    if pbar:
        pbar.close()

    if short:
        return format_dns_record(results, style="short")
    return format_dns_record(results, style=format_style, show_ttl=show_ttl)


@dns.command(name="reverse")
@common_cli_options(include_quiet=True)
@click.argument("ip_addresses", nargs=-1, required=True)
@click.option("--nameserver", "-n", help="Specific nameserver to use")
def reverse_command(
    ip_addresses: tuple[str, ...],
    nameserver: str | None,
    *,
    quiet: bool,
) -> list[dict]:
    """Perform reverse DNS lookup for one or more IP addresses."""
    results: list[dict[str, float | str | None]] = []
    total: int = len(ip_addresses)

    pbar: tqdm[NoReturn] | None = (
        None
        if quiet
        else tqdm(total=total, desc="Performing reverse lookups", unit="lookup")
    )

    for ip in ip_addresses:
        result: dict[str, float | str | None] = reverse_dns(ip, nameserver)
        results.append(
            {
                "ip_address": result["ip_address"],
                "hostname": result["hostname"] or "Not found",
                "response_time_ms": result["response_time"] or "N/A",
            }
        )
        if pbar:
            pbar.set_description(f"Looking up {ip}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@dns.command(name="check")
@common_cli_options(include_quiet=True)
@click.argument("domains", nargs=-1, required=True)
@click.option("--nameserver", "-n", help="Specific nameserver to use")
@click.option(
    "--types",
    "-t",
    "record_types",
    multiple=True,
    type=click.Choice(
        ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "ALL"], case_sensitive=False
    ),
    default=["ALL"],
    help="DNS record types to check (can be used multiple times, default ALL)",
)
def check_command(
    domains: tuple[str, ...],
    nameserver: str | None,
    record_types: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict]:
    """Perform comprehensive DNS check for one or more domains."""
    types_to_check: list[str] = list(record_types)
    if "ALL" in types_to_check:
        types_to_check: list[str] = [t for t in RECORD_TYPES if t != "PTR"]

    results: list[dict[str, str]] = []
    total: int = len(domains)

    pbar: tqdm[NoReturn] | None = (
        None
        if quiet
        else tqdm(total=total, desc="Performing DNS checks", unit="domain")
    )

    for domain in domains:
        result: DetailedCheckResult = check_dns(
            domain=domain,
            nameserver=nameserver,
            record_types=types_to_check,
            validate_mx=True,
            validate_txt=True,
        )

        formatted_result: dict[str, str] = {"domain": domain}
        for rtype in types_to_check:
            if rtype in result["records"] and result["records"][rtype]:
                if rtype == "MX":
                    formatted: list[str] = [
                        f"Priority {r}" for r in result["records"][rtype]
                    ]
                    formatted_result[rtype] = "\n".join(formatted)
                else:
                    formatted_result[rtype] = "\n".join(result["records"][rtype])
            elif rtype in result["errors"]:
                formatted_result[rtype] = f"[{result['errors'][rtype]}]"
            else:
                formatted_result[rtype] = "None"

        results.append(formatted_result)
        if pbar:
            pbar.set_description(f"Checking {domain}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@dns.command(name="trace")
@common_cli_options(include_quiet=True)
@click.argument("domain", required=True)
@click.option("--nameserver", "-n", help="Starting nameserver to use")
def trace_command(
    domain: str,
    nameserver: str | None,
    *,
    quiet: bool,
) -> list[dict]:
    """Trace the DNS resolution path for a domain."""
    if not quiet:
        click.echo(f"Tracing DNS for {domain}...", err=True)

    result: dict[str, Any] = trace_dns(domain, nameserver)
    return format_dns_trace(result)


@dns.command(name="compare")
@common_cli_options(include_quiet=True)
@click.argument("domain", required=True)
@click.option(
    "--servers",
    "-s",
    multiple=True,
    default=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
    help="DNS servers to compare (can be used multiple times)",
)
@click.option(
    "--type",
    "-t",
    "record_types",
    multiple=True,
    default=["A"],
    help="Record types to compare",
)
def compare_command(
    domain: str,
    servers: tuple[str, ...],
    record_types: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict]:
    """Compare DNS responses from different servers."""
    types_to_query: list[str] = list(record_types) if record_types else ["A"]
    total: int = len(servers) * len(types_to_query)

    pbar: tqdm[NoReturn] | None = (
        None if quiet else tqdm(total=total, desc="Comparing DNS servers", unit="query")
    )

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

    return format_dns_comparison(result)


@dns.command(name="health")
@common_cli_options(include_quiet=True)
@click.argument("domain", required=True)
@click.option("--nameserver", "-n", help="Nameserver to use for checks")
def health_command(
    domain: str,
    nameserver: str | None,
    *,
    quiet: bool,
) -> list[dict]:
    """Perform comprehensive DNS health check for a domain."""
    if not quiet:
        click.echo(f"Checking DNS health for {domain}...", err=True)

    result: HealthCheckResult = health_check_dns(domain, nameserver)
    return format_dns_health(result)


@dns.command(name="benchmark")
@common_cli_options(include_quiet=True)
@click.option(
    "--domain",
    "-d",
    default="google.com",
    help="Domain to use for benchmarking",
)
@click.option(
    "--servers",
    "-s",
    multiple=True,
    help="DNS servers to benchmark (default: public DNS servers)",
)
@click.option(
    "--type",
    "-t",
    "record_type",
    default="A",
    type=click.Choice(["A", "AAAA", "MX", "NS", "TXT"]),
    help="Record type to query",
)
@click.option(
    "--queries",
    "-q",
    default=10,
    type=int,
    help="Number of queries per server",
)
@click.option(
    "--parallel/--sequential",
    default=True,
    help="Run benchmarks in parallel or sequentially",
)
def benchmark_command(
    domain: str,
    servers: tuple[str, ...],
    record_type: str,
    queries: int,
    *,
    parallel: bool,
    quiet: bool,
) -> list[dict]:
    """Benchmark the performance of DNS servers."""
    if not quiet:
        click.echo(f"Benchmarking DNS servers for {domain}...", err=True)

    servers_list: list[str] | None = list(servers) if servers else None
    total_servers: int = len(servers_list) if servers_list else 10

    pbar: tqdm[NoReturn] | None = (
        None
        if quiet
        else tqdm(total=total_servers, desc="Benchmarking servers", unit="server")
    )

    def progress_callback(server: str, index: int) -> None:
        if pbar:
            pbar.set_description(f"Benchmarking {server}")
            pbar.update(1)

    results: list[BenchmarkResult] = benchmark_dns_servers(
        domain=domain,
        servers=servers_list,
        record_type=record_type,
        queries=queries,
        parallel=parallel,
        progress_callback=progress_callback if not quiet else None,
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


@dns.command(name="poisoning")
@common_cli_options(include_quiet=True)
@click.argument("domain", required=True)
@click.option(
    "--control-server",
    "-c",
    default="8.8.8.8",
    help="Control server to compare against",
)
@click.option(
    "--test-servers",
    "-t",
    multiple=True,
    help="Test servers to check (default: all public DNS servers)",
)
@click.option(
    "--type",
    "-T",
    "record_type",
    default="A",
    help="Record type to check",
)
@click.option(
    "--additional-types",
    "-a",
    multiple=True,
    help="Additional record types to check on control server",
)
def poisoning_command(
    domain: str,
    control_server: str,
    test_servers: tuple[str, ...],
    record_type: str,
    additional_types: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict]:
    """Check for signs of DNS poisoning or censorship."""

    test_servers_list: list[str] | None = list(test_servers) if test_servers else None
    additional: list[str] | None = list(additional_types) if additional_types else None

    result: PoisoningCheckResult = check_dns_poisoning(
        domain,
        control_server,
        test_servers_list,
        record_type,
        additional,
    )

    return format_dns_poisoning(result)
