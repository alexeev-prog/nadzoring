"""ARP spoofing detection logic."""

from collections import defaultdict

from nadzoring.arp.cache import ARPCache
from nadzoring.arp.models import ARPEntry, SpoofingAlert


class ARPSpoofingDetector:
    """
    Detects potential ARP spoofing attacks.

    Analyzes ARP cache entries to identify potential spoofing attempts by
    detecting duplicate MAC addresses across different IPs or duplicate IP
    addresses across different MACs.

    Attributes:
        cache: ARPCache instance used to retrieve ARP entries.

    """

    def __init__(self, cache: ARPCache) -> None:
        """
        Initialize detector with ARP cache.

        Args:
            cache: ARPCache instance for retrieving ARP entries.

        """
        self.cache = cache

    def detect(self) -> list[SpoofingAlert]:
        """
        Detect potential ARP spoofing in current cache.

        Analyzes all ARP entries and generates alerts for suspicious patterns:
        - Same MAC address associated with multiple IPs (duplicate_mac)
        - Same IP address associated with multiple MACs (duplicate_ip)

        Returns:
            List of SpoofingAlert objects for each detected anomaly.

        """
        entries: list[ARPEntry] = self.cache.get_cache()
        alerts: list[SpoofingAlert] = []

        valid_entries: list[ARPEntry] = [e for e in entries if e.has_mac]

        mac_to_entries: dict[str, list[ARPEntry]] = defaultdict(list)
        for entry in valid_entries:
            if entry.mac_address:
                mac_to_entries[entry.mac_address].append(entry)

        for mac, mac_entries in mac_to_entries.items():
            if len(mac_entries) > 1:
                ips: list[str] = [e.ip_address for e in mac_entries]
                interfaces: list[str] = list({e.interface for e in mac_entries})
                alerts.append(
                    SpoofingAlert(
                        alert_type="duplicate_mac",
                        ip_address=ips[0],
                        mac_address=mac,
                        interfaces=interfaces,
                        description=(
                            f"MAC address {mac} is used by IPs: {', '.join(ips)}. "
                            "This could indicate ARP spoofing."
                        ),
                    )
                )

        ip_to_entries: dict[str, list[ARPEntry]] = defaultdict(list)
        for entry in valid_entries:
            ip_to_entries[entry.ip_address].append(entry)

        for ip, ip_entries in ip_to_entries.items():
            if len(ip_entries) > 1:
                macs: list[str] = [e.mac_address for e in ip_entries if e.mac_address]
                interfaces = list({e.interface for e in ip_entries})
                alerts.append(
                    SpoofingAlert(
                        alert_type="duplicate_ip",
                        ip_address=ip,
                        mac_address=macs[0],
                        interfaces=interfaces,
                        description=(
                            f"IP address {ip} is claimed by MACs: {', '.join(macs)}. "
                            "This is a strong indicator of ARP spoofing."
                        ),
                    )
                )

        return alerts
