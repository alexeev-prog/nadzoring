"""Command orchestration tests with domain operations isolated."""

from unittest.mock import Mock

import click
import pytest
from scapy.all import ARP, Ether

from nadzoring.arp.models import ARPEntry, ARPEntryState, SpoofingAlert
from nadzoring.commands import arp_commands as arp
from nadzoring.commands import security_commands as security
from nadzoring.utils.timeout import TimeoutConfig


@pytest.mark.parametrize("quiet", [False, True])
def test_security_batch_commands(monkeypatch, quiet):
    """Forward batch inputs and update optional progress bars."""
    monkeypatch.setattr(security, "tqdm", Mock(return_value=Mock()))
    monkeypatch.setattr(security, "check_http_security_headers", Mock(return_value={"score": 100}))
    monkeypatch.setattr(security, "check_email_security", Mock(return_value={"overall_score": 3}))
    assert security.check_headers_command.callback.__wrapped__(
        ("example.com",),
        TimeoutConfig(),
        no_verify=False,
        quiet=quiet,
    ) == [{"score": 100}]
    assert security.check_email_command.callback.__wrapped__(("example.com",), quiet=quiet) == [{"overall_score": 3}]
    scan = Mock(return_value=[])
    monkeypatch.setattr(security, "scan_subdomains", scan)
    assert (
        security.subdomains_command.callback.__wrapped__(
            "example.com",
            None,
            2,
            TimeoutConfig(),
            no_bruteforce=True,
            quiet=quiet,
        )
        == []
    )
    assert scan.call_args.kwargs["wordlist_path"] == ""


@pytest.mark.parametrize("full,no_verify", [(False, False), (True, True)])
def test_ssl_command(monkeypatch, full, no_verify):
    """Return full or compact certificate details and retain per-domain errors."""
    result = {
        "domain": "example.com",
        "status": "valid",
        "public_key": {"algorithm": "EC", "curve": "P-256"},
        "protocols": {"supported": ["TLSv1.3"]},
        "warning": "test",
        "error": "diagnostic",
    }
    check = Mock(side_effect=[result, RuntimeError("failed")])
    monkeypatch.setattr(security, "check_ssl_certificate_safe", check)
    monkeypatch.setattr(security, "check_ssl_expiry_with_fallback", check)
    monkeypatch.setattr(security, "tqdm", Mock(return_value=Mock()))
    results = security.check_ssl_command.callback.__wrapped__(
        ("example.com", "failed.com"),
        7,
        TimeoutConfig(),
        no_verify=no_verify,
        full=full,
        quiet=False,
    )
    assert results[0]["warning"] == "test"
    assert results[1]["error"] == "failed"
    if not full:
        assert results[0]["key"] == "EC/P-256"
    else:
        assert results[0] == result


@pytest.mark.parametrize("mode", ["cycles", "run", "interrupt"])
@pytest.mark.parametrize("quiet", [False, True])
def test_ssl_watch_command(monkeypatch, mode, quiet):
    """Run finite and indefinite monitors and handle user interruption."""
    monitor = Mock()
    monitor.run_cycles.return_value = [{"status": "valid"}]
    monitor.history.return_value = [{"status": "valid"}]
    if mode == "interrupt":
        monitor.run.side_effect = KeyboardInterrupt
    monitor.set_alert_callback.side_effect = lambda callback: callback("example.com", "expiring")
    monkeypatch.setattr(security, "SSLMonitor", Mock(return_value=monitor))
    result = security.watch_ssl_command.callback.__wrapped__(
        ("example.com",),
        1,
        1 if mode == "cycles" else 0,
        7,
        TimeoutConfig(),
        quiet=quiet,
    )
    assert result == [{"status": "valid"}]


def test_arp_cache_command(monkeypatch):
    """Normalize incomplete entries and translate cache retrieval errors."""
    cache = Mock()
    cache.get_cache.return_value = [ARPEntry("192.0.2.1", None, "eth0", ARPEntryState.FAILED)]
    monkeypatch.setattr(arp, "ARPCache", Mock(return_value=cache))
    assert arp.show_cache.callback.__wrapped__()[0]["mac_address"] == "(incomplete)"
    cache.get_cache.side_effect = arp.ARPCacheRetrievalError("failed")
    with pytest.raises(click.ClickException, match="failed"):
        arp.show_cache.callback.__wrapped__()
    with pytest.raises(click.ClickException, match="failed"):
        arp.detect_spoofing.callback.__wrapped__((), quiet=True)


@pytest.mark.parametrize("interfaces,quiet", [((), False), (("eth0",), True), (("absent",), False)])
def test_arp_detect_command(monkeypatch, interfaces, quiet):
    """Filter interface output while preserving structured alerts."""
    cache = Mock(get_cache=Mock(return_value=[ARPEntry("192.0.2.1", "aa", "eth0", ARPEntryState.REACHABLE)]))
    monkeypatch.setattr(arp, "ARPCache", Mock(return_value=cache))
    alert = SpoofingAlert("duplicate_ip", "192.0.2.1", "aa", ["eth0"], "suspicious")
    monkeypatch.setattr(
        arp,
        "ARPSpoofingDetector",
        Mock(return_value=Mock(detect=Mock(return_value=[alert]))),
    )
    monkeypatch.setattr(arp, "tqdm", Mock(return_value=Mock()))
    result = arp.detect_spoofing.callback.__wrapped__(interfaces, quiet=quiet)
    assert len(result) == (0 if interfaces == ("absent",) else 1)


@pytest.mark.parametrize("mode", ["packets", "interrupt", "error"])
@pytest.mark.parametrize("quiet", [False, True])
def test_arp_monitor_command(monkeypatch, mode, quiet):
    """Process captured packets and handle capture errors and interrupts."""
    packets = [Ether(src="aa:bb:cc:dd:ee:ff") / ARP(psrc=ip) for ip in ["192.0.2.1", "192.0.2.2"]]

    def sniff(**kwargs):
        if mode == "interrupt":
            raise KeyboardInterrupt
        if mode == "error":
            raise OSError("denied")
        for packet in packets:
            kwargs["prn"](packet)
        return packets

    monkeypatch.setattr(arp, "sniff", sniff)
    callback = arp.monitor_spoofing.callback.__wrapped__
    if mode == "error":
        with pytest.raises(click.ClickException, match="Monitoring failed: denied"):
            callback(None, 0, TimeoutConfig(lifetime=0), quiet=quiet)
    else:
        result = callback(None, 0, TimeoutConfig(lifetime=0), quiet=quiet)
        assert len(result) == (1 if mode == "packets" else 0)
