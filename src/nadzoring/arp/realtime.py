"""Real-time ARP spoofing detection using packet sniffing."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from scapy.all import ARP, Ether, sniff  # type: ignore

from nadzoring.logger import get_logger

logger = get_logger(__name__)


class ARPRealtimeDetector:
    """
    Real-time ARP spoofing detector using packet analysis.

    Monitors network traffic for ARP packets and detects potential spoofing
    attacks by tracking IP-to-MAC mappings and identifying inconsistencies.

    When a packet arrives, the detector checks whether the source MAC already
    maps to a *different* IP — if so, a spoofing alert is generated.

    Attributes:
        ip_mac_map: Dict mapping MAC addresses to their most recently seen IP.
        stats: Monitoring statistics (packets processed, alerts, unique MACs).

    Examples:
        >>> detector = ARPRealtimeDetector()
        >>> alerts = detector.monitor(interface="eth0", count=100)
        >>> for alert in alerts:
        ...     print(alert["message"])

    """

    def __init__(self) -> None:
        """Initialise the real-time ARP spoofing detector."""
        self.ip_mac_map: dict[str, str] = {}
        self.stats: dict[str, int] = {
            "packets_processed": 0,
            "alerts_generated": 0,
            "unique_macs_seen": 0,
        }

    def process_packet(self, packet: Ether) -> str | None:
        """
        Process a single network packet for ARP spoofing detection.

        Args:
            packet: Scapy packet object. Must contain both ARP and Ethernet
                layers; packets missing either layer are silently ignored.

        Returns:
            Alert message string when spoofing is detected, ``None`` otherwise.
            Format: ``"ARP attack detected from machine with IP {old_ip} for
            {new_ip}"``.

        """
        if not packet.haslayer(ARP) or not packet.haslayer(Ether):
            return None

        src_ip: str = packet[ARP].psrc
        src_mac: str = packet[Ether].src

        self.stats["packets_processed"] += 1

        if src_mac in self.ip_mac_map:
            known_ip: str = self.ip_mac_map[src_mac]
            if known_ip != src_ip:
                self.stats["alerts_generated"] += 1
                message = (
                    f"ARP attack detected from machine with IP {known_ip} for {src_ip}"
                )
                logger.warning(message)
                return message
        else:
            self.ip_mac_map[src_mac] = src_ip
            self.stats["unique_macs_seen"] = len(self.ip_mac_map)

        return None

    def monitor(
        self,
        interface: str | None = None,
        count: int = 10,
        timeout: int = 30,
        packet_callback: Callable[[Ether, str | None], None] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Monitor network traffic for ARP spoofing attacks.

        Args:
            interface: Network interface to monitor. ``None`` monitors all
                interfaces.
            count: Number of packets to capture. ``0`` captures indefinitely.
            timeout: Capture timeout in seconds. ``0`` disables the timeout.
            packet_callback: Optional callback receiving ``(packet, alert)``
                for each processed packet. When ``None``, detected alerts are
                collected internally and returned.

        Returns:
            List of alert dicts, each with ``timestamp``, ``interface``,
            ``message``, ``src_ip``, and ``src_mac`` keys. Always empty when
            a custom *packet_callback* is supplied.

        Raises:
            RuntimeError: If packet sniffing fails.

        """
        alerts: list[dict[str, Any]] = []

        def _default_callback(packet: Ether, alert: str | None) -> None:
            if alert:
                alerts.append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "interface": interface or "all",
                        "message": alert,
                        "src_ip": getattr(packet[ARP], "psrc", "unknown"),
                        "src_mac": getattr(packet[Ether], "src", "unknown"),
                    }
                )

        callback: Callable[[Ether, str | None], None] = (
            packet_callback if packet_callback is not None else _default_callback
        )

        logger.info(
            "Starting ARP spoofing monitoring on %s",
            interface if interface is not None else "all interfaces",
        )

        def _packet_handler(packet: Ether) -> None:
            alert: str | None = self.process_packet(packet)
            callback(packet, alert)

        try:
            sniff(
                iface=interface,
                filter="arp",
                prn=_packet_handler,
                store=False,
                count=count if count > 0 else None,
                timeout=timeout if timeout > 0 else None,
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to sniff packets: {exc}") from exc

        return alerts

    def get_stats(self) -> dict[str, int]:
        """
        Return a copy of the current monitoring statistics.

        Returns:
            Dict with ``packets_processed``, ``alerts_generated``, and
            ``unique_macs_seen`` keys.

        """
        return self.stats.copy()

    def reset(self) -> None:
        """Reset detector state and statistics."""
        self.ip_mac_map.clear()
        self.stats = {
            "packets_processed": 0,
            "alerts_generated": 0,
            "unique_macs_seen": 0,
        }
