"""Data models for ARP module."""

from dataclasses import dataclass
from enum import Enum


class ARPEntryState(Enum):
    """
    ARP entry state enumeration.

    Represents the possible states of an ARP cache entry as defined by the
    Linux kernel neighbor subsystem.

    Attributes:
        REACHABLE: Entry is valid and reachable.
        STALE: Entry is valid but possibly unreachable.
        DELAY: Waiting for confirmation before probing.
        PROBE: Actively probing the entry.
        FAILED: Entry has failed resolution.
        PERMANENT: Manually configured permanent entry.
        NOARP: Device does not support ARP.
        UNKNOWN: State could not be determined.

    """

    REACHABLE = "reachable"
    STALE = "stale"
    DELAY = "delay"
    PROBE = "probe"
    FAILED = "failed"
    PERMANENT = "permanent"
    NOARP = "noarp"
    UNKNOWN = "unknown"


@dataclass
class ARPEntry:
    """
    Represents a single ARP cache entry.

    Attributes:
        ip_address: IP address string (e.g. ``"192.168.1.1"``).
        mac_address: MAC address string (e.g. ``"00:11:22:33:44:55"``),
            or ``None`` for incomplete entries.
        interface: Network interface name (e.g. ``"eth0"``).
        state: Current state of the ARP entry.
        flags: Optional platform-specific flags or attributes.

    """

    ip_address: str
    mac_address: str | None
    interface: str
    state: ARPEntryState
    flags: str | None = None

    @property
    def has_mac(self) -> bool:
        """
        Check whether the entry has a resolved MAC address.

        Returns:
            ``True`` if entry has a valid MAC address, ``False`` for
            incomplete entries.

        """
        return self.mac_address is not None and self.mac_address != "(incomplete)"


@dataclass
class SpoofingAlert:
    """
    Represents a potential ARP spoofing alert.

    Attributes:
        alert_type: Type of alert — ``"duplicate_mac"`` or ``"duplicate_ip"``.
        ip_address: IP address involved in the alert.
        mac_address: MAC address involved in the alert.
        interfaces: Network interfaces where the issue was detected.
        description: Human-readable description of the alert.

    """

    alert_type: str
    ip_address: str
    mac_address: str
    interfaces: list[str]
    description: str
