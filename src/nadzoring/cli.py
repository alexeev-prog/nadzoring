"""Main CLI entry point."""

import click

from nadzoring.commands import (
    arp_group,
    completion_group,
    dns_group,
    network_group,
    security_group,
)
from nadzoring.shell import start_interactive


@click.group()
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=start_interactive,
    help="Start an interactive shell.",
)
def cli() -> None:
    """FOSS tool for detecting website blocks, downdetecting and network analysis."""


cli.add_command(network_group)
cli.add_command(dns_group)
cli.add_command(arp_group)
cli.add_command(security_group)
cli.add_command(completion_group)


def main() -> None:
    """Entrypoint to CLI Application."""
    cli()


if __name__ == "__main__":
    main()
