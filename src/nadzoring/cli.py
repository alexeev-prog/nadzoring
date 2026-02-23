# src/nadzoring/cli.py
"""Main CLI entry point."""

import click

from nadzoring.commands import dns_commands, network_commands


@click.group()
def cli() -> None:
    """FOSS tool for detecting website blocks, downdetecting and network analysis."""


# Register command groups
cli.add_command(dns_commands.dns)
cli.add_command(network_commands.network_base)


def main() -> None:
    """Entrypoint to CLI Application."""
    cli()


if __name__ == "__main__":
    main()
