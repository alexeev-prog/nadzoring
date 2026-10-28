"""CLI adapters for package self-management and diagnostics."""

import ipaddress

import click

from nadzoring import core
from nadzoring.core.models import CheckResult, exit_code
from nadzoring.utils.decorators import common_cli_options
from nadzoring.utils.timeout import TimeoutConfig


@click.group(name="core")
@click.option("--quiet", is_flag=True, help="Suppress diagnostic logging, not results.")
@click.option("--no-color", is_flag=True, help="Disable colored output for this group.")
@click.pass_context
def core_group(ctx: click.Context, *, quiet: bool, no_color: bool) -> None:
    """Diagnose the installation, inspect releases, and explicitly update it."""
    ctx.default_map = {name: {"quiet": quiet, "no_color": no_color} for name in core_group.commands}


@core_group.result_callback()
@click.pass_context
def _finish(ctx: click.Context, rows: list[CheckResult], *, quiet: bool, no_color: bool) -> None:
    ctx.exit(exit_code(rows))


def _target(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate a host, rejecting URL paths, ports, credentials, and whitespace."""
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        host = value.rstrip(".")
        if (
            not host
            or len(host) > 253
            or any(
                not label
                or len(label) > 63
                or label.startswith("-")
                or label.endswith("-")
                or not all(char.isascii() and (char.isalnum() or char == "-") for char in label)
                for label in host.split(".")
            )
        ):
            raise click.BadParameter("Expected a hostname or IP address, not a URL", ctx, param) from None
        return host


@core_group.command(name="doctor")
@common_cli_options(format_alias=True, include_timeout=True)
def doctor_command(timeout_config: TimeoutConfig) -> list[CheckResult]:
    """Run all environment diagnostics and report a summary score."""
    return core.doctor(timeout_config=timeout_config)


@core_group.command(name="check-deps")
@common_cli_options(format_alias=True)
@click.option(
    "--strict",
    is_flag=True,
    help="Treat unrelated installed distributions as warnings.",
)
def check_deps_command(*, strict: bool) -> list[CheckResult]:
    """Validate dependency versions against installed package requirements."""
    return core.check_dependencies(strict=strict)


@core_group.command(name="check-permissions")
@common_cli_options(format_alias=True, include_verbose=True)
def check_permissions_command(*, verbose: bool) -> list[CheckResult]:
    """Probe config/cache access, executable bits, and socket permissions."""
    return core.check_permissions(verbose=verbose)


@core_group.command(name="check-network")
@common_cli_options(format_alias=True, include_timeout=True)
@click.option("--target", default="pypi.org", show_default=True, callback=_target)
def check_network_command(target: str, timeout_config: TimeoutConfig) -> list[CheckResult]:
    """Probe DNS, HTTPS and optional ICMP connectivity to a host."""
    return core.check_network(target, timeout_config=timeout_config)


@core_group.command(name="version")
@common_cli_options(format_alias=True, include_timeout=True)
@click.option("--check", is_flag=True, help="Check PyPI for a newer version.")
def version_command(timeout_config: TimeoutConfig, *, check: bool) -> list[CheckResult]:
    """Show the installed version and optionally check for updates."""
    return core.version_info(check=check, timeout_config=timeout_config)


@core_group.command(name="changelog")
@common_cli_options(format_alias=True, include_timeout=True)
@click.option(
    "--version",
    "release_version",
    help="Release version (defaults to the installed version).",
)
def changelog_command(release_version: str | None, timeout_config: TimeoutConfig) -> list[CheckResult]:
    """Retrieve GitHub release notes with a changelog fallback."""
    return core.changelog(release_version, timeout_config=timeout_config)


@core_group.command(name="update")
@common_cli_options(format_alias=True, include_timeout=True)
@click.option(
    "--installer",
    type=click.Choice(["auto", "pip", "uv"]),
    default="auto",
    show_default=True,
)
@click.option("--dry-run", is_flag=True, help="Report the installer command without executing it.")
@click.option(
    "--yes",
    is_flag=True,
    help="Confirm modification of this interpreter's installation.",
)
def update_command(timeout_config: TimeoutConfig, installer: str, *, dry_run: bool, yes: bool) -> list[CheckResult]:
    """Upgrade this installation with pip or uv (requires --yes or --dry-run)."""
    if not dry_run and not yes:
        raise click.UsageError("Updating changes this installation; pass --yes or inspect --dry-run first.")
    return core.update(installer=installer, dry_run=dry_run, timeout_config=timeout_config)
