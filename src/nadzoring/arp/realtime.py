"""
Real-time ARP spoofing detection using packet sniffing.

This module provides real-time monitoring of network traffic to detect
ARP spoofing attacks by analyzing ARP packets and tracking IP-to-MAC
address mappings.

Example:
    >>> detector = ARPRealtimeDetector()
    >>> alerts = detector.monitor(interface="eth0", count=100)
    >>> for alert in alerts:
    ...     print(alert["message"])

"""

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

    The detector maintains a mapping of MAC addresses to their associated IPs.
    When a packet is received, it checks if the MAC address already has a
    different IP associated with it, which would indicate a potential spoofing
    attack.

    Attributes:
        ip_mac_map: Dictionary mapping MAC addresses to their associated IPs.
            Format: {mac_address: ip_address}
        stats: Dictionary with monitoring statistics.

    """

    def __init__(self) -> None:
        """Initialize the real-time ARP spoofing detector."""
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
            packet: Scapy packet object to analyze. Must contain ARP and
                Ethernet layers.

        Returns:
            Alert message if ARP spoofing detected, None otherwise.
            The message format:
                "ARP attack detected from machine with IP {old_ip} for {new_ip}"

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
                message: str = (
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
        Monitor network for ARP spoofing attacks and return alerts.

        Args:
            interface: Network interface to monitor (None for all interfaces).
            count: Number of packets to capture (0 for infinite).
            timeout: Timeout in seconds (0 for no timeout).
            packet_callback: Optional callback function that receives
                the packet and alert message for custom handling.

        Returns:
            List of alert dictionaries, each containing:
                - timestamp: ISO format timestamp
                - interface: Interface being monitored
                - message: Alert message text
                - src_ip: Source IP address
                - src_mac: Source MAC address

        Raises:
            RuntimeError: If packet sniffing fails.

        """
        alerts: list[dict[str, Any]] = []

        def _default_callback(packet: Ether, alert: str | None) -> None:
            """Default packet callback that collects alerts."""
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
            """Handle incoming packet and invoke callback."""
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
        except Exception as e:
            raise RuntimeError(f"Failed to sniff packets: {e}") from e

        return alerts

    def get_stats(self) -> dict[str, int]:
        """
        Get monitoring statistics.

        Returns:
            Dictionary with statistics:
                - packets_processed: Total packets analyzed
                - alerts_generated: Number of alerts detected
                - unique_macs_seen: Number of unique MAC addresses seen

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
