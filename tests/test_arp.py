"""Isolated ARP cache parsing and spoofing detection tests."""

import importlib
import subprocess
from unittest.mock import Mock

import pytest
from scapy.all import ARP, Ether

from nadzoring.arp.cache import ARPCache, _is_valid_ip
from nadzoring.arp.detector import ARPSpoofingDetector
from nadzoring.arp.models import ARPEntry, ARPEntryState
from nadzoring.arp.realtime import ARPRealtimeDetector
from nadzoring.utils.errors import ARPCacheRetrievalError
from nadzoring.utils.timeout import TimeoutConfig


@pytest.mark.parametrize("platform,expected", [("linux", "linux"), ("win32", "windows"), ("darwin", "darwin")])
def test_cache_platform_dispatch(monkeypatch, platform, expected):
    """Dispatch to the platform-specific cache reader."""
    monkeypatch.setattr("nadzoring.arp.cache.sys.platform", platform)
    reader = Mock(return_value=[])
    monkeypatch.setattr(ARPCache, f"_get_{expected}_cache", reader)
    assert ARPCache().get_cache() == []
    reader.assert_called_once_with()


def test_cache_unsupported_platform(monkeypatch):
    """Reject unsupported operating systems."""
    monkeypatch.setattr("nadzoring.arp.cache.sys.platform", "unknown")
    with pytest.raises(ARPCacheRetrievalError, match="Unsupported"):
        ARPCache().get_cache()


@pytest.mark.parametrize("platform", ["linux", "windows", "darwin"])
@pytest.mark.parametrize("failure", [None, "missing", "Permission denied", "failed"])
def test_cache_command_results(monkeypatch, platform, failure):
    """Handle absent executables and subprocess errors without real commands."""
    monkeypatch.setattr("nadzoring.arp.cache.which", lambda _: None if failure == "missing" else "/bin/tool")
    run = Mock(return_value=subprocess.CompletedProcess([], 0, ""))
    if failure and failure != "missing":
        run.side_effect = subprocess.CalledProcessError(1, "tool", stderr=failure)
    monkeypatch.setattr("nadzoring.arp.cache.subprocess.run", run)
    reader = getattr(ARPCache(), f"_get_{platform}_cache")
    if failure:
        with pytest.raises(ARPCacheRetrievalError):
            reader()
    else:
        assert reader() == []
        assert run.call_args.kwargs["check"] is True


def test_cache_parsers():
    """Parse valid, incomplete, and malformed rows on all supported platforms."""
    cache = ARPCache()
    entries = cache._parse_ip_neigh_output(
        "\nshort\n192.0.2.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE\n"
        "192.0.2.2 dev eth1 FAILED\n192.0.2.3 missing interface\n"
    )
    assert len(entries) == 2
    assert entries[0].mac_address == "aa:bb:cc:dd:ee:ff"
    assert entries[1].state == ARPEntryState.FAILED
    assert not entries[1].has_mac
    entries = cache._parse_windows_arp_output(
        "\n192.0.2.1 aa-bb-cc-dd-ee-ff static\nInterface: 192.0.2.2 --- 0x1\n"
        "192.0.2.3 aa-bb-cc-dd-ee-ff dynamic\ninvalid row ignored\n"
    )
    assert entries[0].interface == "unknown"
    assert entries[0].state == ARPEntryState.PERMANENT
    assert entries[1].interface == "192.0.2.2"
    assert entries[1].state == ARPEntryState.REACHABLE
    assert entries[1].mac_address == "aa:bb:cc:dd:ee:ff"
    entries = cache._parse_darwin_arp_output("ignored\n? (192.0.2.1) at aa:bb:cc:dd:ee:ff on en0")
    assert len(entries) == 1
    assert entries[0].interface == "en0"
    assert _is_valid_ip("192.0.2.1")
    assert not _is_valid_ip("::1")
    assert not _is_valid_ip("invalid")


def test_cache_spoofing_detection():
    """Report both duplicate MAC and duplicate IP mappings."""
    entries = [
        ARPEntry("192.0.2.1", "aa", "eth0", ARPEntryState.REACHABLE),
        ARPEntry("192.0.2.2", "aa", "eth1", ARPEntryState.REACHABLE),
        ARPEntry("192.0.2.1", "bb", "eth1", ARPEntryState.REACHABLE),
        ARPEntry("192.0.2.4", None, "eth0", ARPEntryState.FAILED),
        ARPEntry("192.0.2.5", "(incomplete)", "eth0", ARPEntryState.FAILED),
    ]
    cache = Mock(get_cache=Mock(return_value=entries))
    alerts = ARPSpoofingDetector(cache).detect()
    assert {alert.alert_type for alert in alerts} == {"duplicate_mac", "duplicate_ip"}
    assert all(set(alert.interfaces) == {"eth0", "eth1"} for alert in alerts)
    cache.get_cache.return_value = []
    assert ARPSpoofingDetector(cache).detect() == []


def test_realtime_packets_and_reset():
    """Ignore unrelated packets and preserve independent statistics snapshots."""
    detector = ARPRealtimeDetector()
    assert detector.process_packet(Ether()) is None
    assert detector.process_packet(ARP()) is None
    packet = Ether(src="aa:bb:cc:dd:ee:ff") / ARP(psrc="192.0.2.1")
    assert detector.process_packet(packet) is None
    assert detector.process_packet(packet) is None
    assert "192.0.2.1 for 192.0.2.2" in detector.process_packet(Ether(src="aa:bb:cc:dd:ee:ff") / ARP(psrc="192.0.2.2"))
    stats = detector.get_stats()
    assert stats == {"packets_processed": 3, "alerts_generated": 1, "unique_macs_seen": 1}
    detector.reset()
    assert not detector.ip_mac_map
    assert all(value == 0 for value in detector.get_stats().values())
    assert stats["packets_processed"] == 3


@pytest.mark.parametrize("custom", [False, True])
def test_realtime_monitor(monkeypatch, custom):
    """Feed captured packets through default and caller-provided callbacks."""
    packets = [Ether(src="aa:bb:cc:dd:ee:ff") / ARP(psrc=ip) for ip in ["192.0.2.1", "192.0.2.2"]]
    sniff = Mock(side_effect=lambda **kwargs: [kwargs["prn"](packet) for packet in packets])
    monkeypatch.setattr("nadzoring.arp.realtime.sniff", sniff)
    callback = Mock() if custom else None
    alerts = ARPRealtimeDetector().monitor(count=0, packet_callback=callback)
    assert sniff.call_args.kwargs["count"] is None
    if custom:
        assert alerts == []
        assert callback.call_count == 2
    else:
        assert len(alerts) == 1
        assert alerts[0]["interface"] == "all"
        assert alerts[0]["src_ip"] == "192.0.2.2"


def test_realtime_monitor_failure(monkeypatch):
    """Surface capture failures with their original cause."""
    sniff = Mock(side_effect=OSError("denied"))
    monkeypatch.setattr("nadzoring.arp.realtime.sniff", sniff)
    with pytest.raises(RuntimeError, match="Failed to sniff packets: denied"):
        ARPRealtimeDetector().monitor(interface="eth0", timeout_config=TimeoutConfig(lifetime=0))
    assert sniff.call_args.kwargs["timeout"] is None


def test_arp_error_module():
    """Load the public ARP exception definitions."""
    module = importlib.import_module("nadzoring.arp.errors")
    assert module is not None
