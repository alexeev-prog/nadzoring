"""Error propagation and remaining connector delegation tests."""

from unittest.mock import Mock

import pytest

from nadzoring.arp.models import SpoofingAlert
from nadzoring.plugins.connectors import arp, dns, security
from nadzoring.utils.errors import ARPCacheRetrievalError


@pytest.mark.parametrize("mixed", [False, True])
def test_reverse_connector_errors(monkeypatch, mixed):
    """Distinguish complete reverse lookup failure from partial success."""
    results = [{"error": "failed"}] + ([{"hostname": "test"}] if mixed else [])
    monkeypatch.setattr("nadzoring.dns_lookup.reverse_dns", Mock(side_effect=results))
    assert dns.DnsReverseConnector(["192.0.2.1"] * len(results)).probe().status == ("degraded" if mixed else "error")


def test_dns_connector_delegation(monkeypatch):
    """Handle DNS health, benchmark, and delegation trace outcomes."""
    monkeypatch.setattr("nadzoring.dns_lookup.health_check_dns", Mock(return_value={"error": "failed"}))
    assert dns.DnsHealthConnector("example.com").probe().status == "error"
    monkeypatch.setattr(
        "nadzoring.dns_lookup.benchmark_dns_servers",
        Mock(return_value=[{"failed_queries": 1}]),
    )
    assert dns.DnsBenchmarkConnector("example.com").probe().status == "degraded"
    monkeypatch.setattr(
        "nadzoring.dns_lookup.trace_dns",
        Mock(side_effect=[{"error": "failed"}, {"hops": []}]),
    )
    assert dns.DnsTraceConnector("example.com").probe().status == "error"
    assert dns.DnsTraceConnector("example.com").probe().status == "ok"


def test_arp_connector_errors_and_filter(monkeypatch):
    """Translate cache failures and filter spoofing alerts by interface."""
    monkeypatch.setattr(
        "nadzoring.arp.cache.ARPCache",
        Mock(side_effect=ARPCacheRetrievalError("failed")),
    )
    assert arp.ArpCacheConnector().probe().status == "error"
    assert arp.ArpSpoofingConnector().probe().status == "error"
    monkeypatch.setattr("nadzoring.arp.cache.ARPCache", Mock())
    alert = SpoofingAlert("duplicate_ip", "192.0.2.1", "aa", ["eth0"], "test")
    monkeypatch.setattr(
        "nadzoring.arp.detector.ARPSpoofingDetector",
        Mock(return_value=Mock(detect=Mock(return_value=[alert]))),
    )
    assert arp.ArpSpoofingConnector(interfaces=["absent"]).probe().status == "ok"
    assert arp._ok([]).details == {"data": []}


@pytest.mark.parametrize(
    "connector,operation",
    [
        (security.SslCertConnector, "check_ssl_expiry_with_fallback"),
        (security.HttpHeadersConnector, "check_http_security_headers"),
    ],
)
def test_security_connector_errors(monkeypatch, connector, operation):
    """Preserve structured errors when every target fails."""
    monkeypatch.setattr(security, operation, Mock(return_value={"error": "failed"}))
    assert connector(["example.com"]).probe().status == "error"


def test_subdomain_wordlist_forwarding(monkeypatch, tmp_path):
    """Forward custom and default wordlist choices."""
    scan = Mock(return_value=[])
    monkeypatch.setattr(security, "scan_subdomains", scan)
    path = tmp_path / "words"
    assert security.SubdomainScanConnector("example.com", wordlist_path=path).probe().status == "ok"
    assert scan.call_args.kwargs["wordlist_path"] == str(path)
    assert security.SubdomainScanConnector("example.com").probe().status == "ok"
    assert scan.call_args.kwargs["wordlist_path"] is None
    assert security._ok([], 1).latency_ms == 1
