"""DNS-related CLI commands."""

from logging import Logger
from typing import Any

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

_QUERYABLE_RECORD_TYPES: list[str] = [t for t in RECORD_TYPES if t != "PTR"]

_RECORD_TYPE_CHOICE: Choice[str] = click.Choice(
    ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "ALL"],
    case_sensitive=False,
)


def _expand_record_types(record_types: tuple[str, ...]) -> list[str]:
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
    return list(record_types)


def _make_pbar(
    total: int,
    desc: str,
    unit: str,
    *,
    quiet: bool,
) -> tqdm | None:
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


@dns_group.command(name="resolve")
@common_cli_options(include_quiet=True)
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
    *,
    quiet: bool,
    short: bool,
    show_ttl: bool,
) -> list[dict[str, Any]]:
    """Resolve DNS records for one or more domains."""
    types_to_query: list[str] = _expand_record_types(record_types)
    total: int = len(domains) * len(types_to_query)

    pbar: tqdm | None = _make_pbar(total, "Resolving DNS records", "query", quiet=quiet)

    results: list[dict[str, Any]] = []

    for domain in domains:
        domain_result: dict[str, Any] = {"domain": domain, "records": {}}

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
    pbar: tqdm | None = _make_pbar(
        len(ip_addresses), "Performing reverse lookups", "lookup", quiet=quiet
    )

    results: list[dict[str, Any]] = []

    for ip in ip_addresses:
        result: dict[str, Any] = reverse_dns(ip, nameserver)
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


@dns_group.command(name="check")
@common_cli_options(include_quiet=True)
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

    Returns:
        List of dicts with one entry per domain. Each entry contains the
        domain name and a column per record type with its resolved value
        or an error string.

    """
    types_to_check: list[str] = _expand_record_types(record_types)

    pbar: tqdm | None = _make_pbar(
        len(domains), "Performing DNS checks", "domain", quiet=quiet
    )

    results: list[dict[str, Any]] = []

    for domain in domains:
        result: DetailedCheckResult = check_dns(
            domain=domain,
            nameserver=nameserver,
            record_types=types_to_check,
            validate_mx=True,
            validate_txt=True,
        )

        row: dict[str, Any] = {"domain": domain}

        for rtype in types_to_check:
            if rtype in result["records"] and result["records"][rtype]:
                if rtype == "MX":
                    row[rtype] = "\n".join(
                        f"Priority {r}" for r in result["records"][rtype]
                    )
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
@common_cli_options(include_quiet=True)
@click.argument("domain", required=True)
@click.option("--nameserver", "-n", help="Starting nameserver to use.")
def trace_command(
    domain: str,
    nameserver: str | None,
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Trace the full DNS resolution path for a domain.

    Walks the DNS delegation chain from the specified (or root) nameserver
    down to the authoritative answer, recording each intermediate hop.

    Args:
        domain: Domain name to trace.
        nameserver: Optional starting nameserver; defaults to a root server.
        quiet: Suppress informational messages when ``True``.

    Returns:
        List of dicts representing each hop in the resolution path, with
        columns ``hop``, ``nameserver``, ``response_time``, ``records``,
        and ``next``.

    """
    if not quiet:
        click.echo(f"Tracing DNS for {domain}...", err=True)

    result: dict[str, Any] = trace_dns(domain, nameserver)
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
    """
    Compare DNS responses for a domain across multiple nameservers.

    Queries each listed server for the requested record types and flags
    any discrepancies in the returned records or response times.

    Args:
        domain: Domain name to compare.
        servers: DNS servers to query; defaults to Google, Cloudflare, and Quad9.
        record_types: Record types to compare; defaults to ``A``.
        quiet: Suppress progress bar output when ``True``.

    Returns:
        List of dicts with per-server, per-type results including
        ``server``, ``type``, ``response_time_ms``, ``records``, and
        ``differs`` flag.

    """
    types_to_query: list[str] = list(record_types) if record_types else ["A"]
    total: int = len(servers) * len(types_to_query)

    pbar: tqdm | None = _make_pbar(total, "Comparing DNS servers", "query", quiet=quiet)

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


@dns_group.command(name="health")
@common_cli_options(include_quiet=True)
@click.argument("domain", required=True)
@click.option("--nameserver", "-n", help="Nameserver to use for health checks.")
def health_command(
    domain: str,
    nameserver: str | None,
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Run a comprehensive DNS health check for a domain.

    Scores the domain's DNS configuration (0-100) by checking record
    presence, MX priority uniqueness, SPF completeness, DKIM key presence,
    and correct CNAME usage.

    Args:
        domain: Domain name to check.
        nameserver: Optional DNS server to use instead of the system default.
        quiet: Suppress informational messages when ``True``.

    Returns:
        List of dicts with the overall health score, status, issues, and
        warnings; followed by per-record-type score rows.

    """
    if not quiet:
        click.echo(f"Checking DNS health for {domain}...", err=True)

    result: HealthCheckResult = health_check_dns(domain, nameserver)
    return format_dns_health(result)


@dns_group.command(name="benchmark")
@common_cli_options(include_quiet=True)
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
    *,
    parallel: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Benchmark DNS server performance.

    Sends a configurable number of queries to each server and reports
    average, minimum, and maximum response times together with a success
    rate percentage.

    Args:
        domain: Domain used for each test query.
        servers: Servers to benchmark; when empty the default public
            resolvers are used.
        record_type: DNS record type to query.
        queries: Number of queries sent to each server.
        parallel: Run queries concurrently when ``True``.
        quiet: Suppress progress bar output when ``True``.

    Returns:
        List of dicts with ``server``, ``avg_ms``, ``min_ms``, ``max_ms``,
        and ``success_rate`` for each benchmarked server.

    """
    if not quiet:
        click.echo(f"Benchmarking DNS servers for {domain}...", err=True)

    servers_list: list[str] | None = list(servers) if servers else None
    total_servers: int = len(servers_list) if servers_list else 10

    pbar: tqdm | None = _make_pbar(
        total_servers, "Benchmarking servers", "server", quiet=quiet
    )

    def progress_callback(server: str, _index: int) -> None:
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


@dns_group.command(name="poisoning")
@common_cli_options(include_quiet=True)
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
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Detect DNS poisoning, censorship, or CDN routing variations for a domain.

    Compares the control server's response against multiple test servers and
    classifies any discrepancies by severity (INFO → CRITICAL). CDN and
    anycast patterns are recognised as legitimate and reported separately.

    Args:
        domain: Domain name to test.
        control_server: Trusted DNS server used as the reference baseline.
        test_servers: Additional servers to compare against the control.
        record_type: Primary record type to check.
        additional_types: Extra record types to query on the control server.
        quiet: Suppress informational messages when ``True``.

    Returns:
        Formatted list of analysis rows covering control server details,
        summary statistics, CDN detection, IP diversity, consensus data,
        and a final verdict.

    """
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
