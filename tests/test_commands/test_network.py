"""Network command input forwarding and result shaping tests."""

from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import click
import pytest

from nadzoring.commands import network_commands as commands
from nadzoring.utils.timeout import TimeoutConfig


def call(name, *args, **kwargs):
    """Invoke the command body independently of shared output decoration."""
    return getattr(commands, name).callback.__wrapped__(*args, **kwargs)


@pytest.fixture(autouse=True)
def progress(monkeypatch):
    """Replace progress rendering with a context-manager-compatible mock."""
    monkeypatch.setattr(commands, "tqdm", MagicMock())


@pytest.mark.parametrize("quiet", [False, True])
def test_simple_network_commands(monkeypatch, quiet):
    """Forward batch targets and normalize results for display."""
    monkeypatch.setattr(commands, "ping_addr", Mock(side_effect=[True, False]))
    assert [row["status"] for row in call("ping_command", ("up", "down"), quiet=quiet)] == ["up", "down"]
    monkeypatch.setattr(commands, "geo_ip", Mock(return_value={"lat": "1", "lon": "2"}))
    assert call("geolocation_command", ("192.0.2.1",), quiet=quiet)[0]["city"] == "Unknown"
    monkeypatch.setattr(commands, "whois_lookup", Mock(return_value={"name": "test", "absent": None}))
    assert call("whois_command", ("example.com",), quiet=quiet) == [{"name": "test"}]
    monkeypatch.setattr(commands, "get_domain_info", Mock(return_value={"domain": "example.com"}))
    assert call("domain_info_command", ("example.com",), quiet=quiet) == [{"domain": "example.com"}]
    monkeypatch.setattr(commands, "get_service_on_port", Mock(return_value="http"))
    assert call("port_service_command", (80,), quiet=quiet)[0]["service"] == "http"
    for name in ["get_ip_from_host", "check_ipv4", "check_ipv6"]:
        monkeypatch.setattr(commands, name, Mock(return_value="192.0.2.1"))
    monkeypatch.setattr(commands, "router_ip", Mock(return_value=None))
    assert call("host_to_ip_command", ("example.com",), quiet=quiet)[0]["router_ipv6"] == "Not found"


def test_network_parameters(monkeypatch):
    """Combine local IPv4 with platform network parameters."""
    monkeypatch.setattr(commands, "network_param", Mock(return_value=None))
    monkeypatch.setattr(commands, "get_local_ipv4", Mock(return_value="192.0.2.1"))
    assert call("params_command") == [{"local_ipv4": "192.0.2.1"}]


def test_service_detection(monkeypatch):
    """Prefer detected services while retaining probe errors."""
    monkeypatch.setattr(
        commands,
        "detect_service_on_host",
        Mock(
            side_effect=[
                SimpleNamespace(
                    detected_service="http", guessed_service=None, error=None, banner="test", method="probe"
                ),
                SimpleNamespace(
                    detected_service=None, guessed_service=None, error="refused", banner=None, method="port"
                ),
            ]
        ),
    )
    result = call(
        "detect_service_command", "example.com", (80, 81), timeout_config=TimeoutConfig(), no_probe=False, quiet=False
    )
    assert result[0]["detected_service"] == "http"
    assert result[1]["status"] == "error: refused"


@pytest.mark.parametrize(
    "spec,expected", [(None, (None, None)), ("22,80", ([22, 80], None)), ("1-10", (None, (1, 10)))]
)
def test_port_specification(spec, expected):
    """Parse lists and ranges without scanning."""
    assert commands._parse_port_specification("custom", spec) == expected
    assert commands._parse_port_specification("fast", spec) == (None, None)


@pytest.mark.parametrize("spec", ["a-b", "22,invalid"])
def test_invalid_port_specification(spec):
    """Reject malformed port specifications with actionable CLI errors."""
    with pytest.raises(click.BadParameter):
        commands._parse_port_specification("custom", spec)


@pytest.mark.parametrize("quiet", [False, True])
def test_port_scan_command(monkeypatch, quiet):
    """Build per-target scan configurations and wire progress updates."""
    monkeypatch.setattr(commands, "get_ports_from_mode", Mock(return_value=[80]))

    def scan(config):
        if config.progress_callback:
            config.progress_callback("scanning", 1, 2)
        return ["result"]

    monkeypatch.setattr(commands, "scan_ports", scan)
    monkeypatch.setattr(commands, "format_scan_results", lambda results, **_: results)
    assert call(
        "port_scan_command",
        ("example.com",),
        "custom",
        "80",
        "udp",
        TimeoutConfig(),
        1,
        show_closed=True,
        no_banner=True,
        quiet=quiet,
    ) == ["result"]
    monkeypatch.setattr(commands, "get_ports_from_mode", Mock(return_value=[]))
    assert (
        call(
            "port_scan_command",
            ("example.com",),
            "fast",
            None,
            "tcp",
            TimeoutConfig(),
            1,
            show_closed=False,
            no_banner=False,
            quiet=quiet,
        )
        == []
    )


def test_http_ping_command(monkeypatch):
    """Expose timing, redirects, headers, and fallback placeholders."""
    monkeypatch.setattr(
        commands,
        "http_ping",
        Mock(
            return_value=SimpleNamespace(
                url="https://example.com",
                status_code=200,
                error=None,
                dns_ms=1,
                ttfb_ms=None,
                total_ms=2,
                content_length=None,
                final_url="https://example.com/final",
                headers={"server": "test"},
            )
        ),
    )
    result = call(
        "http_ping_command",
        ("example.com",),
        TimeoutConfig(),
        no_ssl_verify=False,
        no_redirects=False,
        show_headers=True,
        quiet=False,
    )
    assert result[0]["header_server"] == "test"
    assert result[0]["ttfb_ms"] == "n/a"
    assert result[0]["redirected_to"].endswith("final")


def test_connections_routes_and_traces(monkeypatch):
    """Shape system entries and display helpful empty-result messages."""
    connection = SimpleNamespace(
        protocol="tcp", local_address="local", remote_address="remote", state=None, pid=1, process="test"
    )
    monkeypatch.setattr(commands, "get_connections", Mock(side_effect=[[connection], []]))
    assert call("connections_command", "all", None, no_process=False, quiet=False)[0]["pid"] == 1
    assert call("connections_command", "all", None, no_process=False, quiet=False) == []
    route = SimpleNamespace(destination="default", gateway="192.0.2.1", netmask=None, interface=None, metric=None)
    monkeypatch.setattr(commands, "get_route_table", Mock(side_effect=[[route], []]))
    assert call("route_command", quiet=False)[0]["netmask"] == "—"
    assert call("route_command", quiet=False) == []
    hop = SimpleNamespace(hop=1, host=None, ip=None, rtt_ms=[1.5, None])
    monkeypatch.setattr(commands, "traceroute", Mock(side_effect=[[hop], []]))
    result = call("traceroute_command", ("example.com", "missing"), 30, TimeoutConfig(), use_sudo=False, quiet=False)
    assert result[0]["rtt"] == "1.5 ms / *"
