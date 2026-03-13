"""Security-related CLI commands."""

from datetime import datetime
from logging import Logger
from typing import Any

import click
from tqdm import tqdm

from nadzoring.logger import get_logger
from nadzoring.security.check_website_ssl_cert import (
    check_ssl_expiry,
    check_ssl_expiry_with_fallback,
)
from nadzoring.utils.decorators import common_cli_options

logger: Logger = get_logger(__name__)


@click.group(name="security")
def security_group() -> None:
    """Security network commands."""


@security_group.command(name="check-ssl-expiry")
@common_cli_options(include_quiet=True)
@click.argument("domains", nargs=-1, required=True)
@click.option(
    "--days-before",
    "-d",
    type=int,
    default=7,
    show_default=True,
    help="Number of days before expiry to flag as warning",
)
@click.option(
    "--no-verify",
    is_flag=True,
    help="Disable SSL certificate verification (insecure, for testing only)",
)
def check_ssl_expiry_command(
    domains: tuple[str, ...],
    days_before: int,
    *,
    no_verify: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """
    Check SSL certificate expiry dates for one or more domains.

    Connects to each domain on port 443, retrieves the SSL certificate,
    and calculates the number of days until expiry. Results include the
    domain, remaining days, and whether it expires within the warning
    threshold.

    Args:
        domains: One or more domain names to check
        days_before: Number of days before expiry to flag as warning
        no_verify: Disable SSL certificate verification (insecure)
        quiet: Suppress progress bar when True

    Returns:
        List of dictionaries with domain, remaining days, and warning status

    Example:
        nadzoring security check-ssl-expiry example.com google.com
        nadzoring security check-ssl-expiry example.com --days-before 14
        nadzoring security check-ssl-expiry example.com --no-verify

    """
    results: list[dict[str, Any]] = []
    total: int = len(domains)

    pbar: tqdm | None = (
        None
        if quiet
        else tqdm(total=total, desc="Checking SSL certificates", unit="domain")
    )

    for domain in domains:
        try:
            if no_verify:
                result: dict[str, datetime | int | str] = (
                    check_ssl_expiry_with_fallback(domain, days_before)
                )
            else:
                result: dict[str, datetime | int | str] = check_ssl_expiry(
                    domain, days_before
                )

            remaining = result.get("remaining days")
            result["warning"] = (
                remaining <= days_before if remaining is not None else True
            )
            result["status"] = (
                "expired"
                if remaining is not None and remaining < 0
                else "warning"
                if remaining is not None and remaining <= days_before
                else "valid"
                if remaining is not None
                else "unknown"
            )

            results.append(result)

        except Exception as e:
            results.append(
                {
                    "domain": domain,
                    "remaining days": None,
                    "days before": days_before,
                    "warning": True,
                    "status": "error",
                    "error": str(e),
                }
            )

            if not quiet:
                click.secho(f"\nError checking {domain}: {e}", fg="red", err=True)

        if pbar:
            pbar.set_description(f"Checking {domain}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results
