"""Security-related CLI commands."""

from datetime import UTC, datetime
from logging import Logger
from typing import Any, Never

import click
from tqdm import tqdm

from nadzoring.logger import get_logger
from nadzoring.security.check_website_ssl_cert import (
    check_ssl_certificate,
    check_ssl_expiry_with_fallback,
)
from nadzoring.security.email_security import check_email_security
from nadzoring.security.http_headers import check_http_security_headers
from nadzoring.security.ssl_monitor import SSLMonitor
from nadzoring.security.subdomain_scan import scan_subdomains
from nadzoring.utils.decorators import common_cli_options
from nadzoring.utils.timeout import TimeoutConfig

logger: Logger = get_logger(__name__)


@click.group(name="security")
def security_group() -> None:
    """Security network commands."""


@security_group.command(name="check-ssl")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("domains", nargs=-1, required=True)
@click.option(
    "--days-before",
    "-d",
    type=int,
    default=7,
    show_default=True,
    help="Days before expiry to flag as warning",
)
@click.option(
    "--no-verify",
    is_flag=True,
    help="Disable SSL certificate verification",
)
@click.option(
    "--full",
    is_flag=True,
    help="Show full certificate details",
)
def check_ssl_command(
    domains: tuple[str, ...],
    days_before: int,
    timeout_config: TimeoutConfig,
    *,
    no_verify: bool,
    full: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Check SSL/TLS certificate for one or more domains."""
    results: list[dict[str, Any]] = []
    total: int = len(domains)

    pbar: tqdm[Never] | None = None if quiet else tqdm(total=total, desc="Checking SSL certificates", unit="domain")

    for domain in domains:
        try:
            if no_verify:
                result: dict[str, Any] = check_ssl_expiry_with_fallback(
                    domain, days_before, timeout_config=timeout_config
                )
            else:
                result = check_ssl_certificate(domain, days_before, verify=True, timeout_config=timeout_config)

            if not full:
                filtered: dict[str, Any] = {
                    "domain": result["domain"],
                    "status": result.get("status", "unknown"),
                    "remaining_days": result.get("remaining_days"),
                    "expiry_date": result.get("expiry_date"),
                    "verification": result.get("verification"),
                    "issuer_cn": result.get("issuer", {}).get("CN", "Unknown"),
                    "subject_cn": result.get("subject", {}).get("CN", "Unknown"),
                    "key": (
                        "{algorithm}/{curve_or_size}".format(
                            algorithm=result.get("public_key", {}).get("algorithm", "?"),
                            curve_or_size=(
                                result.get("public_key", {}).get("curve")
                                or str(result.get("public_key", {}).get("key_size", "?"))
                            ),
                        )
                        if result.get("public_key")
                        else None
                    ),
                    "domain_match": result.get("domain_match"),
                    "protocols_supported": ", ".join(result.get("protocols", {}).get("supported", [])) or None,
                    "has_outdated_protocols": result.get("protocols", {}).get("has_outdated"),
                }
                if "warning" in result:
                    filtered["warning"] = result["warning"]
                if "error" in result:
                    filtered["error"] = result["error"]
                results.append({k: v for k, v in filtered.items() if v is not None})
            else:
                results.append(result)

        except Exception as exc:
            results.append({
                "domain": domain,
                "status": "error",
                "error": str(exc),
            })

        if pbar:
            pbar.set_description(f"Checking {domain}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@security_group.command(name="check-headers")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("urls", nargs=-1, required=True)
@click.option(
    "--no-verify",
    is_flag=True,
    help="Disable SSL certificate verification",
)
def check_headers_command(
    urls: tuple[str, ...],
    timeout_config: TimeoutConfig,
    *,
    no_verify: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Check HTTP security headers for one or more URLs."""
    results: list[dict[str, Any]] = []
    total: int = len(urls)

    pbar: tqdm[Never] | None = None if quiet else tqdm(total=total, desc="Checking security headers", unit="url")

    for url in urls:
        result: dict[str, Any] = check_http_security_headers(
            url,
            timeout_config=timeout_config,
            verify_ssl=not no_verify,
        )
        results.append(result)

        if pbar:
            pbar.set_description(f"Checking {url}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@security_group.command(name="check-email")
@common_cli_options(include_quiet=True)
@click.argument("domains", nargs=-1, required=True)
def check_email_command(
    domains: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Check email security (SPF, DKIM, DMARC) for one or more domains."""
    results: list[dict[str, Any]] = []
    total: int = len(domains)

    pbar: tqdm[Never] | None = None if quiet else tqdm(total=total, desc="Checking email security", unit="domain")

    for domain in domains:
        result: dict[str, Any] = check_email_security(domain)
        results.append(result)

        if pbar:
            pbar.set_description(f"Checking {domain}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@security_group.command(name="subdomains")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("domain", required=True)
@click.option(
    "--wordlist",
    type=click.Path(exists=True),
    help="Custom wordlist file for subdomain brute-force",
)
@click.option(
    "--threads",
    type=int,
    default=20,
    show_default=True,
    help="Number of concurrent threads",
)
@click.option(
    "--no-bruteforce",
    is_flag=True,
    help="Skip DNS brute-force, use CT logs only",
)
def subdomains_command(
    domain: str,
    wordlist: str | None,
    threads: int,
    timeout_config: TimeoutConfig,
    *,
    no_bruteforce: bool,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Discover subdomains via CT logs and brute-force DNS for a domain."""
    if not quiet:
        click.echo(f"Discovering subdomains for {domain}...", err=True)

    wordlist_arg: str | None = "" if no_bruteforce else wordlist

    return scan_subdomains(
        domain,
        wordlist_path=wordlist_arg,
        max_threads=threads,
        timeout_config=timeout_config,
    )


@security_group.command(name="watch-ssl")
@common_cli_options(include_quiet=True, include_timeout=True)
@click.argument("domains", nargs=-1, required=True)
@click.option(
    "--interval",
    "-i",
    type=int,
    default=3600,
    show_default=True,
    help="Check interval in seconds",
)
@click.option(
    "--cycles",
    "-c",
    type=int,
    default=0,
    show_default=True,
    help="Number of cycles to run (0 = infinite)",
)
@click.option(
    "--days-before",
    "-d",
    type=int,
    default=7,
    show_default=True,
    help="Days before expiry to alert",
)
def watch_ssl_command(
    domains: tuple[str, ...],
    interval: int,
    cycles: int,
    days_before: int,
    timeout_config: TimeoutConfig,
    *,
    quiet: bool,
) -> list[dict[str, Any]]:
    """Monitor SSL certificates continuously for changes and expiry."""
    monitor = SSLMonitor(
        list(domains),
        interval,
        days_before,
        timeout_config=timeout_config,
    )

    def _alert(domain: str, message: str) -> None:
        if not quiet:
            click.secho(
                f"⚠  [{datetime.now(tz=UTC).strftime('%H:%M:%S')}] {domain}: {message}",
                fg="yellow",
            )

    monitor.set_alert_callback(_alert)

    if not quiet:
        click.echo(
            f"Monitoring SSL for {len(domains)} domain(s). Press Ctrl+C to stop.",
            err=True,
        )

    try:
        if cycles > 0:
            results: list[dict[str, Any]] = monitor.run_cycles(cycles)
        else:
            monitor.run()
            results = monitor.history()
    except KeyboardInterrupt:
        if not quiet:
            click.echo("\nMonitoring stopped by user.", err=True)
        results = monitor.history()

    return results
