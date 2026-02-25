# src/nadzoring/cli/commands/network_commands.py
"""Network-related CLI commands."""

from logging import Logger

import click
from tqdm import tqdm

from nadzoring.logger import get_logger
from nadzoring.network_base.geolocation_ip import geo_ip
from nadzoring.network_base.ipv4_local_cli import get_local_ipv4
from nadzoring.network_base.network_params import network_param
from nadzoring.network_base.ping_address import ping_addr
from nadzoring.network_base.router_ip import (
    check_ipv4,
    check_ipv6,
    get_ip_from_host,
    router_ip,
)
from nadzoring.network_base.service_on_port import get_service_on_port
from nadzoring.utils.decorators import common_cli_options

logger: Logger = get_logger(__name__)


@click.group(name="network-base")
def network_base() -> None:
    """Network base commands for analysis and diagnostics."""


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
    data = network_param()
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
