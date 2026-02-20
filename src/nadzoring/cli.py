import csv
import functools
import io
import json
from collections.abc import Callable
from csv import DictWriter
from io import StringIO
from logging import Logger
from pathlib import Path
from time import time
from typing import Any, Literal, TextIO, cast

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


def colorize_result(result: dict[str, Any]) -> dict[str, Any]:
    """Add color coding to results"""
    colored: dict[str, str] = {}
    for key, value in result.items():
        if key == "IsPinged":
            if value == "yes":
                colored[key] = click.style(str(value), fg="green", bold=True)
            else:
                colored[key] = click.style(str(value), fg="red", bold=True)
        elif "Check" in key:
            if value == "passed":
                colored[key] = click.style(str(value), fg="green")
            elif value == "failed":
                colored[key] = click.style(str(value), fg="red")
            else:
                colored[key] = str(value)
        else:
            colored[key] = str(value)
    return colored


def print_results_table(results: dict[str, any]) -> None:
    if results:
        colored_results: list[dict[str, Any]] = [colorize_result(r) for r in results]
        print(
            tabulate(
                colored_results,
                showindex="never",
                headers="keys",
                tablefmt="simple_grid",
            )
        )
    else:
        print("No results.")


def print_csv_table(data: list[dict[str, Any]], file: TextIO | None = None) -> None:
    """Print data as CSV to console or file"""
    if not data:
        click.echo("No data to display")
        return None

    output: StringIO | TextIO = io.StringIO() if file is None else file
    writer: DictWriter[str] = csv.DictWriter(output, fieldnames=data[0].keys())

    writer.writeheader()
    writer.writerows(data)

    if file is None:
        click.echo(output.getvalue())
    return output.getvalue() if file is None else None


def save_results(data: Any, filename: str, fileformat: str) -> None:
    """Save results to file in specified format using pathlib"""
    try:
        file_path = Path(filename)

        file_path.parent.mkdir(parents=True, exist_ok=True)

        if fileformat == "json":
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            click.secho(f"✓ JSON results saved to {file_path}", fg="green")

        elif fileformat == "csv":
            with file_path.open("w", encoding="utf-8", newline="") as f:
                if data:
                    writer: DictWriter = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            click.secho(f"✓ CSV results saved to {file_path}", fg="green")

        elif fileformat == "table":
            with file_path.open("w", encoding="utf-8") as f:
                if data:
                    f.write(tabulate(data, headers="keys", tablefmt="grid"))
            click.secho(f"✓ Table results saved to {file_path}", fg="green")

    except PermissionError:
        click.secho(
            f"✗ Permission denied: Cannot write to {filename}", fg="red", err=True
        )
    except OSError as e:
        click.secho(f"✗ OS error while saving results: {e}", fg="red", err=True)
    except Exception as e:
        click.secho(f"✗ Failed to save results: {e}", fg="red", err=True)


def common_logging_options[F: Callable[..., Any]](func: F) -> F:
    @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
    @click.option("--quiet", "-q", is_flag=True, help="Quiet mode")
    @click.option("--no-color", is_flag=True, help="Disable colored output")
    @click.option(
        "--output",
        "-o",
        type=click.Choice(["table", "json", "csv"]),
        default="table",
        help="Output format",
    )
    @click.option("--save", type=click.Path(), help="Save results to file")
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        verbose = kwargs.pop("verbose", False)
        quiet = kwargs.pop("quiet", False)
        no_color = kwargs.pop("no_color", False)
        output = kwargs.pop("output", False)
        save = kwargs.pop("save", False)
        setup_cli_logging(verbose=verbose, quiet=quiet, no_color=no_color)

        start_time: float = time()
        result = func(*args, **kwargs)
        elapsed: float = time() - start_time

        if output == "json":
            print(json.dumps(result))
        elif output == "table":
            print_results_table(result)
        elif output == "csv":
            print_csv_table(result)

        if save:
            save_results(result, save, output)

        if verbose:
            click.secho(
                f"\n⚡ Completed in {elapsed:.2f} seconds", fg="bright_black", dim=True
            )

        return result

    return cast(F, wrapper)


@click.group()
def cli() -> None:
    """FOSS tool for detecting website blocks, downdetecting and network analysis."""


@cli.group()
def network_base() -> None:
    """Network Base"""


@network_base.command()
@common_logging_options
@click.argument("addresses", type=str, nargs=-1, required=True)
def ping_address(addresses: tuple[str, ...]) -> list[dict[str, str]]:
    """Ping one or more addresses."""
    results: list[dict[str, str]] = []

    for address in addresses:
        is_pinged: Literal["no", "yes"] = "yes" if ping_addr(address) else "no"

        results.append({"Address": address, "IsPinged": is_pinged})

    return results


@network_base.command()
@common_logging_options
def get_network_params() -> list[dict[str, str | None] | None]:
    data: dict[str, str | None] | None = network_param()

    return [data]


@network_base.command()
@common_logging_options
@click.argument("hostnames", type=str, nargs=-1, required=True)
def get_ip_by_hostname(hostnames: tuple[str, ...]) -> list[dict[str, int | str]]:
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

    return results


@network_base.command()
@common_logging_options
@click.argument("ports", type=int, nargs=-1, required=True)
def get_service_by_port(ports: tuple[int, ...]) -> list[dict[str, int | str]]:
    """Get service names for one or more ports."""
    results: list[dict[str, str | int]] = []

    for port in ports:
        service: str = get_service_on_port(port)

        if service == "Unknown":
            logger.warning("Service is unknown for port %d; check port", port)

        results.append({"port": port, "service": service})

    return results


def main() -> None:
    """Entrypoint to CLI Application."""
    cli()
