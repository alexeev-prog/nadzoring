import functools
from collections.abc import Callable
from logging import Logger
from typing import Any, Literal, cast

import click
from tabulate import tabulate

from nadzoring.logger import get_logger, setup_cli_logging
from nadzoring.network_base.network_params import network_param
from nadzoring.network_base.ping_address import ping_addr
from nadzoring.network_base.router_ip import (
    check_ipv4,
    check_ipv6,
    get_ip_from_host,
    router_ip,
)
from nadzoring.network_base.service_on_port import get_service_on_port

logger: Logger = get_logger("cli")


def common_logging_options[F: Callable[..., Any]](func: F) -> F:
    @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
    @click.option("--quiet", "-q", is_flag=True, help="Quiet mode")
    @click.option("--no-color", is_flag=True, help="Disable colored output")
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        verbose = kwargs.pop("verbose", False)
        quiet = kwargs.pop("quiet", False)
        no_color = kwargs.pop("no_color", False)
        setup_cli_logging(verbose=verbose, quiet=quiet, no_color=no_color)
        return func(*args, **kwargs)

    return cast(F, wrapper)


def print_results_table(results: dict[str, any]) -> None:
    if results:
        print(
            tabulate(
                results,
                showindex="never",
                headers="keys",
                tablefmt="simple_grid",
            )
        )
    else:
        print("No results.")


@click.group()
def cli() -> None:
    """FOSS tool for detecting website blocks, downdetecting and network analysis."""


@cli.group()
def network_base() -> None:
    """Network Base"""


@network_base.command()
@common_logging_options
@click.argument("addresses", type=str, nargs=-1, required=True)
def ping_address(addresses: tuple[str, ...]) -> None:
    """Ping one or more addresses."""
    results: list[dict[str, str]] = []

    for address in addresses:
        is_pinged: Literal["no", "yes"] = "yes" if ping_addr(address) else "no"

        results.append({"Address": address, "IsPinged": is_pinged})

    print_results_table(results)


@network_base.command()
@common_logging_options
def get_network_params() -> None:
    data: dict[str, str | None] | None = network_param()

    print_results_table([data])


@network_base.command()
@common_logging_options
@click.argument("hostnames", type=str, nargs=-1, required=True)
def get_ip_by_hostname(hostnames: tuple[str, ...]) -> None:
    """Get IPs for one or more hostname addresses."""
    results: list[dict[str, str | int]] = []

    router_ipv4: str | None = router_ip(ipv6=False)
    router_ipv6: str | None = router_ip(ipv6=True)

    for hostname in hostnames:
        ip: str = get_ip_from_host(hostname)
        ipv4_check: str = check_ipv4(hostname)
        ipv6_check: str = check_ipv6(hostname)

        if ip == hostname:
            logger.warning("Hostname %s is invalid", ip)

        results.append(
            {
                "Hostname": hostname,
                "IP Address": ip,
                "IPv4 Check": ipv4_check,
                "IPv6 Check": ipv6_check,
                "Router IPv4": router_ipv4 or "Not found",
                "Router IPv6": router_ipv6 or "Not found",
            }
        )

    print_results_table(results)


@network_base.command()
@common_logging_options
@click.argument("ports", type=int, nargs=-1, required=True)
def get_service_by_port(ports: tuple[int, ...]) -> None:
    """Get service names for one or more ports."""
    results: list[dict[str, str | int]] = []

    for port in ports:
        service: str = get_service_on_port(port)

        if service == "Unknown":
            logger.warning("Service is unknown for port %d; check port", port)

        results.append({"port": port, "service": service})

    print_results_table(results)


def main() -> None:
    """Entrypoint to CLI Application."""
    cli()
