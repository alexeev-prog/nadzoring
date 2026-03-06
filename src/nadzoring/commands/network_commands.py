"""Network base CLI commands."""

from collections.abc import Callable
from logging import Logger
from typing import Any

import click
from tqdm import tqdm

from nadzoring.logger import get_logger
from nadzoring.network_base.connections import ConnectionEntry, get_connections
from nadzoring.network_base.geolocation_ip import geo_ip
from nadzoring.network_base.http_ping import HttpPingResult, http_ping
from nadzoring.network_base.ipv4_local_cli import get_local_ipv4
from nadzoring.network_base.network_params import network_param
from nadzoring.network_base.ping_address import ping_addr
from nadzoring.network_base.port_scanner import (
    ScanConfig,
    ScanResult,
    get_ports_from_mode,
    scan_ports,
)
from nadzoring.network_base.route_table import RouteEntry, get_route_table
from nadzoring.network_base.router_ip import (
    check_ipv4,
    check_ipv6,
    get_ip_from_host,
    router_ip,
)
from nadzoring.network_base.service_on_port import get_service_on_port
from nadzoring.network_base.traceroute import TraceHop, traceroute
from nadzoring.network_base.whois_lookup import whois_lookup
from nadzoring.utils.decorators import common_cli_options
from nadzoring.utils.formatters import format_scan_results

logger: Logger = get_logger(__name__)


@click.group(name="network-base")
def network_group() -> None:
    """Network base commands for analysis and diagnostics."""


@network_group.command(name="port-scan")
@common_cli_options(include_quiet=True)
@click.argument("targets", nargs=-1, required=True)
@click.option(
    "--mode",
    type=click.Choice(["fast", "full", "custom"], case_sensitive=False),
    default="fast",
    help="Scan mode: fast (common ports), full (1-65535), or custom",
)
@click.option(
    "--ports",
    help="Custom ports or range (e.g., '22,80,443' or '1-1024')",
)
@click.option(
    "--protocol",
    type=click.Choice(["tcp", "udp"], case_sensitive=False),
    default="tcp",
    help="Protocol to scan",
)
@click.option(
    "--timeout",
    type=float,
    default=2.0,
    help="Socket timeout in seconds",
)
@click.option(
    "--workers",
    type=int,
    default=50,
    help="Maximum number of concurrent workers per target",
)
@click.option(
    "--show-closed",
    is_flag=True,
    help="Show closed ports in results",
)
@click.option(
    "--no-banner",
    is_flag=True,
    help="Disable banner grabbing",
)
def port_scan_command(
    targets: tuple[str, ...],
    mode: str,
    ports: str | None,
    protocol: str,
    timeout: float,
    workers: int,
    *,
    show_closed: bool,
    no_banner: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Scan for open ports on one or more targets."""
    parsed_ports: tuple[list[int] | None, tuple[int, int] | None] = (
        _parse_port_specification(mode, ports)
    )

    base_config = ScanConfig(
        targets=list(targets),
        mode=mode,
        protocol=protocol,
        custom_ports=parsed_ports[0],
        port_range=parsed_ports[1],
        timeout=timeout,
        max_workers=workers,
        grab_banner=not no_banner,
    )

    ports_to_scan: list[int] = get_ports_from_mode(base_config)
    if not ports_to_scan:
        click.secho("No ports to scan. Check your configuration.", fg="red", err=True)
        return []

    total_ports_per_target: int = len(ports_to_scan)
    batch_size: int = workers
    num_batches: int = (total_ports_per_target + batch_size - 1) // batch_size

    if not quiet:
        click.echo(
            f"Scanning {len(targets)} target(s) | "
            f"{total_ports_per_target} ports each | "
            f"{num_batches} batches of {batch_size} workers",
            err=True,
        )

    scan_results: list[ScanResult] = []

    for target_idx, target in enumerate(targets, 1):
        target_config = ScanConfig(
            targets=[target],
            mode=mode,
            protocol=protocol,
            custom_ports=parsed_ports[0],
            port_range=parsed_ports[1],
            timeout=timeout,
            max_workers=workers,
            grab_banner=not no_banner,
        )

        if quiet:
            result = scan_ports(target_config)
            if result:
                scan_results.extend(result)
            continue

        with tqdm(
            total=total_ports_per_target,
            desc=f"[{target_idx}/{len(targets)}] {target}",
            unit="ports",
            dynamic_ncols=True,
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} "
            "[{elapsed}<{remaining}, {rate_fmt}]",
        ) as pbar:

            def _make_callback(
                pbar: tqdm,
                target_idx: int,
                target: str,
                total_targets: int,
            ) -> Callable[[str, int, int], None]:
                def progress_callback(desc: str, completed: int, total: int) -> None:
                    pbar.desc = f"[{target_idx}/{total_targets}] {target} | {desc}"
                    if pbar.total != total:
                        pbar.total = total
                    pbar.n = completed
                    pbar.refresh()

                return progress_callback

            target_config.progress_callback = _make_callback(
                pbar, target_idx, target, len(targets)
            )
            result: list[ScanResult] = scan_ports(target_config)
            if result:
                scan_results.extend(result)

    return format_scan_results(scan_results, show_closed=show_closed)


def _parse_port_specification(
    mode: str, ports: str | None
) -> tuple[list[int] | None, tuple[int, int] | None]:
    """Parse port specification from CLI arguments."""
    if mode != "custom" or not ports:
        return None, None

    if "-" in ports and "," not in ports:
        try:
            start, end = map(int, ports.split("-"))
        except ValueError as err:
            raise click.BadParameter(
                "Port range must be in format 'start-end' (e.g., '1-1024')"
            ) from err
        return None, (start, end)

    try:
        custom_ports: list[int] = [int(p.strip()) for p in ports.split(",")]
    except ValueError as err:
        raise click.BadParameter("Ports must be comma-separated integers") from err

    return custom_ports, None


@network_group.command(name="ping")
@common_cli_options(include_quiet=True)
@click.argument("addresses", type=str, nargs=-1, required=True)
def ping_command(
    addresses: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict]:
    """Ping one or more addresses."""
    results = []
    total = len(addresses)

    pbar = None if quiet else tqdm(total=total, desc="Pinging addresses", unit="ping")

    for address in addresses:
        is_pinged = ping_addr(address)
        results.append(
            {
                "address": address,
                "is_pinged": "yes" if is_pinged else "no",
                "status": "up" if is_pinged else "down",
            }
        )
        if pbar:
            pbar.set_description(f"Pinging {address}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@network_group.command(name="geolocation")
@common_cli_options(include_quiet=True)
@click.argument("ips", type=str, nargs=-1, required=True)
def geolocation_command(
    ips: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict]:
    """Get geolocation for one or more IPs."""
    results = []
    total = len(ips)

    pbar = None if quiet else tqdm(total=total, desc="Getting geolocation", unit="ip")

    for ip in ips:
        geolocation = geo_ip(ip)
        results.append(
            {
                "ip_address": ip,
                "latitude": geolocation.get("lat", "Unknown"),
                "longitude": geolocation.get("lon", "Unknown"),
                "country": geolocation.get("country", "Unknown"),
                "city": geolocation.get("city", "Unknown"),
            }
        )
        if pbar:
            pbar.set_description(f"Locating {ip}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@network_group.command(name="params")
@common_cli_options(include_quiet=True)
def params_command(*, quiet: bool = False) -> list[dict]:
    """Display network configuration parameters for the current system."""
    data = network_param() or {}
    data["local_ipv4"] = get_local_ipv4()
    return [data]


@network_group.command(name="host-to-ip")
@common_cli_options(include_quiet=True)
@click.argument("hostnames", type=str, nargs=-1, required=True)
def host_to_ip_command(
    hostnames: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict]:
    """Get IPs for one or more hostname addresses."""
    results = []
    total = len(hostnames)

    pbar = None if quiet else tqdm(total=total, desc="Resolving hostnames", unit="host")

    router_ipv4 = router_ip(ipv6=False)
    router_ipv6 = router_ip(ipv6=True)

    for hostname in hostnames:
        ip = get_ip_from_host(hostname)
        ipv4_check = check_ipv4(hostname)
        ipv6_check = check_ipv6(hostname)

        results.append(
            {
                "hostname": hostname,
                "ip_address": ip,
                "ipv4_check": ipv4_check,
                "ipv6_check": ipv6_check,
                "router_ipv4": router_ipv4 or "Not found",
                "router_ipv6": router_ipv6 or "Not found",
            }
        )
        if pbar:
            pbar.set_description(f"Resolving {hostname}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@network_group.command(name="port-service")
@common_cli_options(include_quiet=True)
@click.argument("ports", type=int, nargs=-1, required=True)
def port_service_command(
    ports: tuple[int, ...],
    *,
    quiet: bool,
) -> list[dict]:
    """Get service names for one or more ports."""
    results = []
    total = len(ports)

    pbar = None if quiet else tqdm(total=total, desc="Looking up ports", unit="port")

    for port in ports:
        service = get_service_on_port(port)
        results.append(
            {
                "port": port,
                "service": service,
                "protocol": "tcp/udp",
            }
        )
        if pbar:
            pbar.set_description(f"Port {port}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@network_group.command(name="http-ping")
@common_cli_options(include_quiet=True)
@click.argument("urls", nargs=-1, required=True)
@click.option(
    "--timeout",
    type=float,
    default=10.0,
    help="Request timeout in seconds",
)
@click.option(
    "--no-ssl-verify",
    is_flag=True,
    help="Disable SSL certificate verification",
)
@click.option(
    "--no-redirects",
    is_flag=True,
    help="Do not follow HTTP redirects",
)
@click.option(
    "--show-headers",
    is_flag=True,
    help="Include response headers in output",
)
def http_ping_command(
    urls: tuple[str, ...],
    timeout: float,
    *,
    no_ssl_verify: bool,
    no_redirects: bool,
    show_headers: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Check HTTP/HTTPS response timing and headers for one or more URLs.

    Measures DNS resolution time, time-to-first-byte (TTFB), total download
    time, HTTP status code and optional response headers.
    """
    results: list[dict[str, Any]] = []
    total = len(urls)

    pbar = None if quiet else tqdm(total=total, desc="Probing URLs", unit="url")

    for url in urls:
        result: HttpPingResult = http_ping(
            url,
            timeout=timeout,
            verify_ssl=not no_ssl_verify,
            follow_redirects=not no_redirects,
            include_headers=show_headers,
        )

        row: dict[str, Any] = {
            "url": result.url,
            "status": result.status_code or result.error or "error",
            "dns_ms": result.dns_ms if result.dns_ms is not None else "n/a",
            "ttfb_ms": result.ttfb_ms if result.ttfb_ms is not None else "n/a",
            "total_ms": result.total_ms if result.total_ms is not None else "n/a",
            "size_bytes": (
                result.content_length if result.content_length is not None else "n/a"
            ),
        }

        if result.final_url:
            row["redirected_to"] = result.final_url

        if show_headers and result.headers:
            for header_key in (
                "Content-Type",
                "Server",
                "Cache-Control",
                "X-Powered-By",
            ):
                value = result.headers.get(header_key) or result.headers.get(
                    header_key.lower()
                )
                if value:
                    row[f"header_{header_key.lower().replace('-', '_')}"] = value

        results.append(row)

        if pbar:
            pbar.set_description(f"Probing {url}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@network_group.command(name="whois")
@common_cli_options(include_quiet=True)
@click.argument("targets", nargs=-1, required=True)
def whois_command(
    targets: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Look up WHOIS registration info for one or more domains or IPs.

    Requires the system 'whois' utility to be installed
    (apt install whois / brew install whois).
    """
    results: list[dict[str, Any]] = []
    total = len(targets)

    pbar = None if quiet else tqdm(total=total, desc="Running WHOIS", unit="target")

    for target in targets:
        info = whois_lookup(target)
        # Flatten to flat dict, drop None values for cleaner table output
        row: dict[str, Any] = {k: v for k, v in info.items() if v is not None}
        results.append(row)

        if pbar:
            pbar.set_description(f"WHOIS {target}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@network_group.command(name="connections")
@common_cli_options(include_quiet=True)
@click.option(
    "--protocol",
    "-p",
    type=click.Choice(["tcp", "udp", "all"], case_sensitive=False),
    default="all",
    help="Filter by protocol",
)
@click.option(
    "--state",
    "-s",
    "state_filter",
    default=None,
    help="Filter by state substring, e.g. LISTEN or ESTABLISHED",
)
@click.option(
    "--no-process",
    is_flag=True,
    help="Skip process/PID info (avoids permission errors)",
)
def connections_command(
    protocol: str,
    state_filter: str | None,
    *,
    no_process: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    List active network connections (TCP/UDP).

    Shows local/remote addresses, connection state and, where available,
    the PID and process name. Analogous to 'ss' or 'netstat'.
    """
    entries: list[ConnectionEntry] = get_connections(
        protocol=protocol,
        state_filter=state_filter,
        include_process=not no_process,
    )

    results: list[dict[str, Any]] = []
    for entry in entries:
        row: dict[str, Any] = {
            "protocol": entry.protocol,
            "local_address": entry.local_address,
            "remote_address": entry.remote_address,
            "state": entry.state or "—",
        }
        if entry.pid is not None:
            row["pid"] = entry.pid
        if entry.process is not None:
            row["process"] = entry.process
        results.append(row)

    if not quiet and not results:
        click.echo("No connections found matching the given filters.", err=True)

    return results


@network_group.command(name="traceroute")
@common_cli_options(include_quiet=True)
@click.argument("targets", nargs=-1, required=True)
@click.option(
    "--max-hops",
    type=int,
    default=30,
    help="Maximum number of hops",
)
@click.option(
    "--timeout",
    type=float,
    default=2.0,
    help="Per-hop timeout in seconds (default: 2)",
)
@click.option(
    "--sudo",
    "use_sudo",
    is_flag=True,
    help="Run traceroute with sudo (required on some Linux systems)",
)
def traceroute_command(
    targets: tuple[str, ...],
    max_hops: int,
    timeout: float,
    *,
    use_sudo: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Trace the network path to one or more hosts.

    Uses 'traceroute' (Linux) or 'tracert' (Windows). On Linux, raw-socket
    access is needed: run with --sudo, as root, or grant the capability with
    'sudo setcap cap_net_raw+ep $(which traceroute)'.
    tracepath is tried automatically as a root-free fallback.
    """
    results: list[dict[str, Any]] = []
    total = len(targets)

    pbar = None if quiet else tqdm(total=total, desc="Tracing routes", unit="target")

    for target in targets:
        if not quiet:
            click.echo(f"\nTraceroute to {target}:", err=True)

        hops: list[TraceHop] = traceroute(
            target,
            max_hops=max_hops,
            per_hop_timeout=timeout,
            use_sudo=use_sudo,
        )

        for hop in hops:
            rtt_values = [f"{r:.1f} ms" if r is not None else "*" for r in hop.rtt_ms]
            results.append(
                {
                    "target": target,
                    "hop": hop.hop,
                    "host": hop.host or "*",
                    "ip": hop.ip or "*",
                    "rtt": " / ".join(rtt_values),
                }
            )

        if not hops and not quiet:
            click.echo(f"No hops returned for {target}.", err=True)

        if pbar:
            pbar.set_description(f"Tracing {target}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@network_group.command(name="route")
@common_cli_options(include_quiet=True)
def route_command(*, quiet: bool = False) -> list[dict[str, Any]]:
    """
    Display the system IP routing table.

    Uses 'ip route' on Linux and 'route PRINT' on Windows.
    """
    entries: list[RouteEntry] = get_route_table()

    if not entries and not quiet:
        click.echo(
            "Could not retrieve routing table. "
            "Check that 'ip' (Linux) or 'route' (Windows) is available.",
            err=True,
        )
        return []

    return [
        {
            "destination": entry.destination,
            "gateway": entry.gateway,
            "netmask": entry.netmask or "—",
            "interface": entry.interface or "—",
            "metric": entry.metric or "—",
        }
        for entry in entries
    ]
