"""ARP category connectors — wraps every command from ``nadzoring arp``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.result import ProbeResult

_TAGS = ("arp", "network", "security")


def _ok(data: Any) -> ProbeResult:
    return ProbeResult(status="ok", details={"data": data})


def _err(msg: str) -> ProbeResult:
    return ProbeResult(status="error", error=msg)


# ---------------------------------------------------------------------------
# arp cache
# ---------------------------------------------------------------------------


@dataclass
class ArpCacheConnector(ConnectorBase):
    """Read the local ARP cache.

    Wraps :class:`nadzoring.arp.cache.ARPCache`.
    """

    meta = ConnectorMeta(
        name="arp-cache",
        category=ConnectorCategory.NETWORK,
        description="Reads the local ARP cache (IP→MAC mappings).",
        tags=_TAGS,
    )

    def probe(self) -> ProbeResult:
        from nadzoring.arp.cache import ARPCache

        try:
            cache = ARPCache()
            entries = cache.get_cache()
            return ProbeResult(
                status="ok",
                details={
                    "data": [e.__dict__ if hasattr(e, "__dict__") else e for e in entries],
                    "count": len(entries),
                },
            )
        except Exception as exc:
            return _err(str(exc))


# ---------------------------------------------------------------------------
# arp detect-spoofing
# ---------------------------------------------------------------------------


@dataclass
class ArpSpoofingConnector(ConnectorBase):
    """Detect ARP spoofing in the local ARP cache.

    Wraps :class:`nadzoring.arp.detector.ARPSpoofingDetector`.

    Attributes:
        interfaces: Network interfaces to filter by. Empty list checks all.
    """

    meta = ConnectorMeta(
        name="arp-spoofing",
        category=ConnectorCategory.NETWORK,
        description="Detects ARP spoofing / duplicate MAC alerts in ARP cache.",
        tags=_TAGS,
    )

    interfaces: list[str] = field(default_factory=list)

    def probe(self) -> ProbeResult:
        from nadzoring.arp.cache import ARPCache
        from nadzoring.arp.detector import ARPSpoofingDetector

        try:
            cache = ARPCache()
            alerts = ARPSpoofingDetector(cache).detect()
            if self.interfaces:
                alerts = [
                    a
                    for a in alerts
                    if any(iface in self.interfaces for iface in a.interfaces)
                ]
            alert_list = [
                {
                    "alert_type": a.alert_type,
                    "ip_address": a.ip_address,
                    "mac_address": a.mac_address,
                    "interfaces": list(a.interfaces),
                    "description": a.description,
                }
                for a in alerts
            ]

            if alert_list:
                return ProbeResult(
                    status="error",
                    error=f"ARP spoofing detected: {len(alert_list)} alert(s)",
                    details={"data": alert_list, "count": len(alert_list)},
                )
            return ProbeResult(
                status="ok",
                details={"data": [], "count": 0},
            )
        except Exception as exc:
            return _err(str(exc))
