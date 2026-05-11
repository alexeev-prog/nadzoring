"""Unit tests for plugin connectors with mocked domain and network I/O."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from nadzoring.arp.models import ARPEntry, ARPEntryState, SpoofingAlert
from nadzoring.network_base.connections import ConnectionEntry
from nadzoring.network_base.http_ping import HttpPingResult
from nadzoring.network_base.traceroute import TraceHop
from nadzoring.plugins.connectors.arp import ArpCacheConnector, ArpSpoofingConnector
from nadzoring.plugins.connectors.dns import (
    DnsCompareConnector,
    DnsHealthConnector,
    DnsPoisoningConnector,
    DnsResolveConnector,
)
from nadzoring.plugins.connectors.network import (
    ConnectionsConnector,
    GeolocationConnector,
    HttpPingConnector,
    PingConnector,
    TracerouteConnector,
)
from nadzoring.plugins.connectors.security import (
    HttpHeadersConnector,
    SslCertConnector,
)
from nadzoring.plugins.connectors.web import HttpEndpointConnector
from nadzoring.plugins.examples.frameworks import DjangoConnector, FastAPIConnector, FlaskConnector
from nadzoring.utils.timeout import TimeoutConfig


def test_dns_resolve_connector_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """DnsResolveConnector aggregates successful resolve results."""

    def fake_resolve(
        domain: str,
        record_type: str,
        nameserver: str | None,
        timeout_config: TimeoutConfig | None,
        *,
        include_ttl: bool = False,
    ) -> dict:
        return {"domain": domain, "record_type": record_type, "records": ["1.1.1.1"], "error": None}

    monkeypatch.setattr("nadzoring.dns_lookup.resolve_dns", fake_resolve)
    conn = DnsResolveConnector(domains=["a.test"], record_types=["A"])
    result = conn.probe()
    assert result.status == "ok"
    assert result.error is None
    assert len(result.details["data"]) == 1


def test_dns_resolve_connector_all_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """When every query fails, status is error with a combined message."""

    def fake_resolve(
        domain: str,
        record_type: str,
        nameserver: str | None,
        timeout_config: TimeoutConfig | None,
        *,
        include_ttl: bool = False,
    ) -> dict:
        return {"error": "timeout"}

    monkeypatch.setattr("nadzoring.dns_lookup.resolve_dns", fake_resolve)
    conn = DnsResolveConnector(domains=["bad.test"], record_types=["A"])
    result = conn.probe()
    assert result.status == "error"
    assert "timeout" in (result.error or "")


def test_dns_health_connector_healthy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.dns_lookup.health_check_dns",
        lambda domain, ns, tc: {"domain": domain, "status": "healthy", "score": 100},
    )
    result = DnsHealthConnector(domain="example.com").probe()
    assert result.status == "ok"


def test_dns_health_connector_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.dns_lookup.health_check_dns",
        lambda domain, ns, tc: {"domain": domain, "status": "degraded", "score": 40},
    )
    result = DnsHealthConnector(domain="example.com").probe()
    assert result.status == "degraded"


def test_dns_compare_consistent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.dns_lookup.compare_dns_servers",
        lambda domain, servers, types, cb, tc: {
            "domain": domain,
            "differences": [],
            "servers": {},
        },
    )
    result = DnsCompareConnector(domain="example.com").probe()
    assert result.status == "ok"


def test_dns_compare_inconsistent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.dns_lookup.compare_dns_servers",
        lambda domain, servers, types, cb, tc: {
            "domain": domain,
            "differences": [{"server": "1.1.1.1"}],
            "servers": {},
        },
    )
    result = DnsCompareConnector(domain="example.com").probe()
    assert result.status == "degraded"


def test_dns_poisoning_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.dns_lookup.check_dns_poisoning",
        lambda *a, **k: {"domain": "x", "poisoned": True, "poisoning_likely": False},
    )
    result = DnsPoisoningConnector(domain="x.test").probe()
    assert result.status == "error"


def test_ping_connector_all_up(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("nadzoring.network_base.ping_address.ping_addr", lambda addr: True)
    result = PingConnector(addresses=["127.0.0.1"]).probe()
    assert result.status == "ok"


def test_ping_connector_all_down(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("nadzoring.network_base.ping_address.ping_addr", lambda addr: False)
    result = PingConnector(addresses=["192.0.2.1"]).probe()
    assert result.status == "unreachable"


def test_traceroute_connector_serialises_hops(monkeypatch: pytest.MonkeyPatch) -> None:
    hop = TraceHop(hop=1, host="r1", ip="10.0.0.1", rtt_ms=[1.0])
    monkeypatch.setattr(
        "nadzoring.network_base.traceroute.traceroute",
        lambda target, **kw: [hop],
    )
    result = TracerouteConnector(targets=["example.com"]).probe()
    assert result.status == "ok"
    rows = result.details["data"]
    assert rows[0]["hops"][0]["hop"] == 1


def test_http_ping_connector(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = HttpPingResult(
        url="https://x",
        final_url="https://x",
        status_code=200,
        dns_ms=1.0,
        ttfb_ms=2.0,
        total_ms=5.0,
        content_length=10,
        error=None,
    )
    monkeypatch.setattr("nadzoring.network_base.http_ping.http_ping", lambda *a, **k: fake)
    result = HttpPingConnector(urls=["https://x"]).probe()
    assert result.status == "ok"
    assert result.details["data"][0]["total_ms"] is not None
    assert abs(result.details["data"][0]["total_ms"] - 5.0) < 0.001


def test_geolocation_connector_empty_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("nadzoring.network_base.geolocation_ip.geo_ip", lambda ip: {})
    result = GeolocationConnector(ip_addresses=["192.0.2.1"]).probe()
    assert result.status == "error"


def test_geolocation_connector_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.network_base.geolocation_ip.geo_ip",
        lambda ip: {"lat": "1", "lon": "2", "country": "X", "city": "Y"},
    )
    result = GeolocationConnector(ip_addresses=["8.8.8.8"]).probe()
    assert result.status == "ok"


def test_connections_connector(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [
        ConnectionEntry("tcp", "0.0.0.0:80", "0.0.0.0:0", "LISTEN", None, None),
    ]
    monkeypatch.setattr("nadzoring.network_base.connections.get_connections", lambda **kw: rows)
    result = ConnectionsConnector().probe()
    assert result.status == "ok"
    assert result.details["data"][0]["protocol"] == "tcp"


def test_ssl_cert_connector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.security.check_website_ssl_cert.check_ssl_expiry_with_fallback",
        lambda domain, days, tc: {"domain": domain, "days_remaining": 90, "error": None},
    )
    result = SslCertConnector(domains=["example.com"], days_before=7).probe()
    assert result.status == "ok"


def test_ssl_cert_expiring(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.security.check_website_ssl_cert.check_ssl_expiry_with_fallback",
        lambda domain, days, tc: {"domain": domain, "days_remaining": 3, "error": None},
    )
    result = SslCertConnector(domains=["example.com"], days_before=7).probe()
    assert result.status == "degraded"


def test_http_headers_connector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nadzoring.security.http_headers.check_http_security_headers",
        lambda url, **kw: {"url": url, "score": 80, "error": None},
    )
    result = HttpHeadersConnector(urls=["https://example.com"]).probe()
    assert result.status == "ok"


def test_http_endpoint_connector_ok() -> None:
    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None
    mock_resp.status = 200

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = HttpEndpointConnector(target="https://example.com", expected_status=200).probe()
    assert result.status == "ok"
    assert result.details["http_status"] == 200


def test_http_endpoint_connector_wrong_status() -> None:
    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None
    mock_resp.status = 500

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = HttpEndpointConnector(target="https://example.com", expected_status=200).probe()
    assert result.status == "degraded"


def test_flask_connector_health_ok() -> None:
    body = json.dumps({"status": "ok"}).encode()
    with patch(
        "nadzoring.plugins.examples.frameworks._request",
        return_value=(200, body.decode()),
    ):
        result = FlaskConnector(base_url="http://127.0.0.1:5000").probe()
    assert result.status == "ok"
    assert result.details["health"]["http_status"] == 200


def test_fastapi_connector_health_and_openapi() -> None:
    health = json.dumps({"status": "healthy"}).encode()
    openapi = json.dumps({"info": {"title": "API", "version": "1"}, "paths": {"/x": {}}}).encode()

    def fake_request(url, **kw):
        if url.endswith("/health"):
            return (200, health.decode())
        if "openapi" in url:
            return (200, openapi.decode())
        return (200, "{}")

    with patch("nadzoring.plugins.examples.frameworks._request", side_effect=fake_request):
        result = FastAPIConnector(base_url="http://127.0.0.1:8000").probe()
    assert result.status == "ok"
    assert result.details["openapi"]["ok"] is True


def test_django_connector_health_json() -> None:
    body = json.dumps({"DatabaseBackend": "working", "Cache backend": "working"})
    with patch(
        "nadzoring.plugins.examples.frameworks._request",
        return_value=(200, body),
    ):
        result = DjangoConnector(base_url="http://127.0.0.1:8000").probe()
    assert result.status == "ok"


def test_arp_cache_connector(monkeypatch: pytest.MonkeyPatch) -> None:
    entry = ARPEntry(
        ip_address="192.168.1.1",
        mac_address="00:11:22:33:44:55",
        interface="eth0",
        state=ARPEntryState.REACHABLE,
    )
    cache = MagicMock()
    cache.get_cache.return_value = [entry]
    monkeypatch.setattr("nadzoring.arp.cache.ARPCache", lambda: cache)
    result = ArpCacheConnector().probe()
    assert result.status == "ok"
    assert result.details["count"] == 1


def test_arp_spoofing_connector_no_alerts(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = MagicMock()
    cache.get_cache.return_value = []
    detector = MagicMock()
    detector.detect.return_value = []

    monkeypatch.setattr("nadzoring.arp.cache.ARPCache", lambda: cache)
    monkeypatch.setattr("nadzoring.arp.detector.ARPSpoofingDetector", lambda c: detector)

    result = ArpSpoofingConnector().probe()
    assert result.status == "ok"


def test_arp_spoofing_connector_with_alert(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = MagicMock()
    cache.get_cache.return_value = []
    alert = SpoofingAlert(
        alert_type="duplicate_mac",
        ip_address="10.0.0.1",
        mac_address="00:00:00:00:00:01",
        interfaces=["eth0"],
        description="test",
    )
    detector = MagicMock()
    detector.detect.return_value = [alert]

    monkeypatch.setattr("nadzoring.arp.cache.ARPCache", lambda: cache)
    monkeypatch.setattr("nadzoring.arp.detector.ARPSpoofingDetector", lambda c: detector)

    result = ArpSpoofingConnector().probe()
    assert result.status == "error"
    assert "spoofing" in (result.error or "").lower()
