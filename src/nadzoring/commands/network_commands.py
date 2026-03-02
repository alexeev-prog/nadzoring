from collections.abc import Callable
from logging import Logger
from typing import Any

import click
from tqdm import tqdm

from nadzoring.logger import get_logger
from nadzoring.network_base.geolocation_ip import geo_ip
from nadzoring.network_base.ipv4_local_cli import get_local_ipv4
from nadzoring.network_base.network_params import network_param
from nadzoring.network_base.ping_address import ping_addr
from nadzoring.network_base.port_scanner import (
    ScanConfig,
    ScanResult,
    get_ports_from_mode,
    scan_ports,
)
from nadzoring.network_base.router_ip import (
    check_ipv4,
    check_ipv6,
    get_ip_from_host,
    router_ip,
)
from nadzoring.network_base.service_on_port import get_service_on_port
from nadzoring.utils.decorators import common_cli_options
from nadzoring.utils.formatters import _format_scan_results

logger: Logger = get_logger(__name__)


@click.group(name="network-base")
def network_base() -> None:
    """Network base commands for analysis and diagnostics."""


@network_base.command(name="port-scan")
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

    return _format_scan_results(scan_results, show_closed=show_closed)


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


@network_base.command(name="ping")
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


@network_base.command(name="geolocation")
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


@network_base.command(name="params")
@common_cli_options(include_quiet=True)
def params_command(*, quiet: bool = False) -> list[dict]:
    """Get network parameters for the current system."""
    data = network_param() or {}
    data["local_ipv4"] = get_local_ipv4()
    return [data]


@network_base.command(name="host-to-ip")
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


@network_base.command(name="port-service")
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
