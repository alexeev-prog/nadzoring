"""Network and web connector transport and composition tests."""

import importlib
import socket
import ssl
import urllib.error
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, Mock

import pytest

from nadzoring.plugins.connectors import network, web


@pytest.mark.parametrize("spec", ["", "22,80", "1-10", "invalid-range"])
def test_scan_connector(monkeypatch, spec):
    """Parse connector port specifications and forward scan configuration."""
    scan = Mock(return_value=[])
    monkeypatch.setattr("nadzoring.network_base.port_scanner.scan_ports", scan)
    assert network.PortScanConnector(["example.com"], ports=spec).probe().status == "ok"
    config = scan.call_args.args[0]
    if spec == "1-10":
        assert config.port_range == (1, 10)
    elif spec == "22,80":
        assert config.custom_ports == [22, 80]


@pytest.mark.parametrize(
    "results,status",
    [
        ([{"error": "failed"}], "error"),
        ([{"error": "failed"}, {"name": "test"}], "degraded"),
        ([{"name": "test"}], "ok"),
    ],
)
def test_whois_connector(monkeypatch, results, status):
    """Preserve successful WHOIS entries alongside partial failures."""
    monkeypatch.setattr("nadzoring.network_base.whois_lookup.whois_lookup", Mock(side_effect=results))
    assert network.WhoisConnector(["example.com"] * len(results)).probe().status == status


def test_http_ping_failure(monkeypatch):
    """Return an error when all HTTP timing probes fail."""
    module = importlib.import_module("nadzoring.network_base.http_ping")
    result = module.HttpPingResult(
        url="https://example.com",
        final_url=None,
        status_code=None,
        dns_ms=None,
        ttfb_ms=None,
        total_ms=None,
        content_length=None,
        error="failed",
    )
    monkeypatch.setattr(module, "http_ping", Mock(return_value=result))
    assert network.HttpPingConnector(["example.com"]).probe().status == "error"


@pytest.mark.parametrize(
    "failure,status",
    [
        (None, "ok"),
        (TimeoutError(), "unreachable"),
        (ConnectionRefusedError(), "unreachable"),
        (OSError("failed"), "error"),
    ],
)
def test_tcp_connector(monkeypatch, failure, status):
    """Translate TCP connection outcomes without opening sockets."""
    monkeypatch.setattr(socket, "create_connection", MagicMock(side_effect=failure))
    assert network.TcpPortConnector("example.com", 443).probe().status == status


@pytest.mark.parametrize("days,status", [(-1, "error"), (5, "degraded"), (60, "ok"), (None, "error")])
def test_tls_connector_expiry(monkeypatch, days, status):
    """Parse peer certificate expiration and subject metadata."""
    expiry = (datetime.now(UTC) + timedelta(days=days or 0)).strftime("%b %d %H:%M:%S %Y GMT")
    peer = {"notAfter": expiry, "subject": ((("commonName", "example.com"),),)} if days is not None else None
    context = MagicMock()
    context.wrap_socket.return_value.__enter__.return_value.getpeercert.return_value = peer
    monkeypatch.setattr(ssl, "create_default_context", Mock(return_value=context))
    monkeypatch.setattr(socket, "create_connection", MagicMock())
    assert network.TlsCertConnector("example.com").probe().status == status


@pytest.mark.parametrize(
    "failure,status",
    [
        (ssl.SSLCertVerificationError(), "error"),
        (TimeoutError(), "unreachable"),
        (OSError("failed"), "error"),
    ],
)
def test_tls_connector_errors(monkeypatch, failure, status):
    """Handle TLS verification and handshake transport failures."""
    monkeypatch.setattr(ssl, "create_default_context", MagicMock())
    monkeypatch.setattr(socket, "create_connection", Mock(side_effect=failure))
    assert network.TlsCertConnector("example.com").probe().status == status


def test_local_network_connectors(monkeypatch):
    """Compose local route and network parameter results."""
    monkeypatch.setattr("nadzoring.network_base.route_table.get_route_table", Mock(return_value=[]))
    assert network.RouteTableConnector().probe().status == "ok"
    monkeypatch.setattr(
        "nadzoring.network_base.network_params.network_param",
        Mock(side_effect=[None, {"interface": "eth0"}]),
    )
    monkeypatch.setattr(
        "nadzoring.network_base.ipv4_local_cli.get_local_ipv4",
        Mock(return_value="192.0.2.1"),
    )
    assert network.NetworkParamsConnector().probe().status == "error"
    assert network.NetworkParamsConnector().probe().status == "ok"


@pytest.mark.parametrize("connector", [web.HttpEndpointConnector, web.WebhookConnector])
@pytest.mark.parametrize(
    "failure,status",
    [
        (TimeoutError(), "unreachable"),
        (urllib.error.URLError("offline"), "unreachable"),
        (OSError("failed"), "error"),
    ],
)
def test_web_connector_errors(monkeypatch, connector, failure, status):
    """Map expected delivery and endpoint failures to structured results."""
    monkeypatch.setattr(web.urllib.request, "urlopen", Mock(side_effect=failure))
    assert connector("https://example.com").probe().status == status


@pytest.mark.parametrize("status,expected", [(200, "ok"), (202, "degraded")])
def test_webhook_delivery(monkeypatch, status, expected):
    """POST the payload and check the expected response status."""
    response = MagicMock()
    response.__enter__.return_value.status = status
    opener = Mock(return_value=response)
    monkeypatch.setattr(web.urllib.request, "urlopen", opener)
    assert web.WebhookConnector("https://example.com", payload=b'{"test":true}').probe().status == expected
    request = opener.call_args.args[0]
    assert request.method == "POST"
    assert request.data == b'{"test":true}'
