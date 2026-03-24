# src/nadzoring/cli.py
"""Main CLI entry point."""

import click

from nadzoring.commands import arp_group, dns_group, network_group, security_group


@click.group()
def cli() -> None:
    """FOSS tool for detecting website blocks, downdetecting and network analysis."""


cli.add_command(network_group)
cli.add_command(dns_group)
cli.add_command(arp_group)
cli.add_command(security_group)


def main() -> None:
    """Entrypoint to CLI Application."""
    try:
        cli()
    except Exception as e:
        raise click.ClickException(
            f"Unexpected error: {e!s}\n\n"
            "Possible fixes:\n"
            "  • Run the command with --help\n"
            "  • Check if required tools are installed\n"
            "  • Ensure proper permissions (try sudo if needed)"
        ) from e


if __name__ == "__main__":
    main()
