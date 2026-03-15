"""ARP-related CLI commands."""

from datetime import UTC, datetime
from logging import Logger
from typing import Any

import click
from scapy.all import ARP, Ether, sniff  # type: ignore
from tqdm import tqdm

from nadzoring.arp import (
    ARPCache,
    ARPCacheRetrievalError,
    ARPEntry,
    ARPSpoofingDetector,
    SpoofingAlert,
)
from nadzoring.arp.realtime import ARPRealtimeDetector
from nadzoring.logger import get_logger
from nadzoring.utils.decorators import common_cli_options

logger: Logger = get_logger(__name__)


@click.group(name="arp")
def arp_group() -> None:
    """ARP cache and spoofing detection commands."""


@arp_group.command(name="cache")
@common_cli_options()
def show_cache() -> list[dict[str, Any]]:
    """Show current ARP cache table."""
    try:
        cache = ARPCache()
        entries: list[ARPEntry] = cache.get_cache()
    except ARPCacheRetrievalError as e:
        raise click.ClickException(str(e)) from e

    return [
        {
            "ip_address": entry.ip_address,
            "mac_address": entry.mac_address or "(incomplete)",
            "interface": entry.interface,
            "state": entry.state.value,
        }
        for entry in entries
    ]


@arp_group.command(name="detect-spoofing")
@common_cli_options(include_quiet=True)
@click.argument("interfaces", nargs=-1, required=False)
def detect_spoofing(interfaces: tuple[str, ...], *, quiet: bool) -> list[dict[str, Any]]:
    """
    Detect potential ARP spoofing attacks on one or more interfaces.

    If no interfaces specified, checks all interfaces.
    """
    try:
        cache = ARPCache()
        all_entries: list[ARPEntry] = cache.get_cache()
    except ARPCacheRetrievalError as e:
        raise click.ClickException(str(e)) from e

    if interfaces:
        entries: list[ARPEntry] = [e for e in all_entries if e.interface in interfaces]
        if not entries and not quiet:
            click.echo(
                f"No ARP entries found for interfaces: {', '.join(interfaces)}",
                err=True,
            )
    else:
        entries = all_entries

    detector = ARPSpoofingDetector(cache)

    all_alerts: list[SpoofingAlert] = detector.detect()

    interfaces_to_check: list[str] = list({e.interface for e in entries})

    total: int = len(interfaces_to_check)
    pbar: tqdm | None = None if quiet else tqdm(total=total, desc="Analyzing interfaces", unit="iface")

    results: list[dict[str, str]] = []
    for interface in interfaces_to_check:
        interface_alerts: list[SpoofingAlert] = [alert for alert in all_alerts if interface in alert.interfaces]

        results.extend(
            {
                "alert_type": alert.alert_type,
                "ip_address": alert.ip_address,
                "mac_address": alert.mac_address,
                "interface": interface,
                "description": alert.description,
            }
            for alert in interface_alerts
        )

        if pbar:
            pbar.set_description(f"Analyzing {interface}")
            pbar.update(1)

    if pbar:
        pbar.close()

    return results


@arp_group.command(name="monitor-spoofing")
@common_cli_options(include_quiet=True, include_output=True, include_save=True)
@click.option(
    "--interface",
    "-i",
    default=None,
    help="Network interface to monitor (default: all interfaces).",
)
@click.option(
    "--count",
    "-c",
    default=10,
    help="Number of packets to capture (default: 10).",
    show_default=True,
)
@click.option(
    "--timeout",
    "-t",
    default=30,
    help="Timeout in seconds (default: 30).",
    show_default=True,
)
def monitor_spoofing(
    interface: str | None,
    count: int,
    timeout: int,
    *,
    quiet: bool,
    output: str,
    save: str | None,
) -> list[dict[str, Any]]:
    """
    Monitor network for ARP spoofing attacks in real-time.

    Captures ARP packets on the specified interface and detects potential
    spoofing attacks by tracking IP-to-MAC mappings.
    """
    alerts: list[dict[str, Any]] = []

    try:
        detector = ARPRealtimeDetector()

        def packet_callback(packet: Any) -> None:
            """Process packet and collect alerts."""
            alert: str | None = detector.process_packet(packet)
            if alert:
                alert_dict: dict[str, Any] = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "interface": interface or "all",
                    "message": alert,
                    "src_ip": getattr(packet[ARP], "psrc", "unknown"),
                    "src_mac": getattr(packet[Ether], "src", "unknown"),
                }
                alerts.append(alert_dict)

                if not quiet:
                    click.secho(f"\n! {alert}", fg="red", bold=True)

        if not quiet:
            click.echo(f"Monitoring ARP spoofing on {interface or 'all interfaces'}...\nPress Ctrl+C to stop.")

        packets = sniff(
            iface=interface,
            filter="arp",
            prn=packet_callback,
            store=False,
            count=count if count > 0 else None,
            timeout=timeout if timeout > 0 else None,
        )

        if not quiet:
            click.echo(f"\nCaptured {len(packets)} ARP packets.")

    except KeyboardInterrupt:
        if not quiet:
            click.echo("\n\nMonitoring stopped by user.")
    except Exception as e:
        raise click.ClickException(f"Monitoring failed: {e}") from e

    return alerts
