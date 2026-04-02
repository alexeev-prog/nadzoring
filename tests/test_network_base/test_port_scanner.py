# tests/test_network_base/test_port_scanner.py
"""Tests for nadzoring.network_base.port_scanner — 100% coverage."""

import socket
from datetime import UTC, datetime

import pytest

from nadzoring.network_base.port_scanner import (
    COMMON_PORTS,
    PortResult,
    ScanConfig,
    ScanResult,
    _grab_banner,
    _scan_target_ports,
    _scan_tcp_port,
    _scan_udp_port,
    get_ports_from_mode,
    resolve_target,
    scan_ports,
)
from nadzoring.utils.timeout import TimeoutConfig

TIMEOUT_CONFIG = TimeoutConfig(connect=1.0, read=2.0, lifetime=5.0)


# ---------------------------------------------------------------------------
# resolve_target
# ---------------------------------------------------------------------------


def test_resolve_valid_ipv4():
    assert resolve_target("192.168.1.1") == "192.168.1.1"


def test_resolve_valid_ipv6():
    assert resolve_target("::1") == "::1"


def test_resolve_loopback():
    assert resolve_target("127.0.0.1") == "127.0.0.1"


def test_resolve_hostname_success(mocker):
    mocker.patch(
        "nadzoring.network_base.port_scanner.socket.gethostbyname",
        return_value="1.2.3.4",
    )
    assert resolve_target("example.com") == "1.2.3.4"


def test_resolve_hostname_gaierror_returns_none(mocker):
    mocker.patch(
        "nadzoring.network_base.port_scanner.socket.gethostbyname",
        side_effect=socket.gaierror,
    )
    assert resolve_target("invalid.local") is None


# ---------------------------------------------------------------------------
# get_ports_from_mode
# ---------------------------------------------------------------------------


def _cfg(mode, **kwargs):
    return ScanConfig(targets=["127.0.0.1"], mode=mode, **kwargs)


def test_fast_returns_sorted_common_ports():
    assert get_ports_from_mode(_cfg("fast")) == sorted(COMMON_PORTS)


def test_fast_no_duplicates():
    ports = get_ports_from_mode(_cfg("fast"))
    assert len(ports) == len(set(ports))


def test_full_range():
    ports = get_ports_from_mode(_cfg("full"))
    assert ports[0] == 1
    assert ports[-1] == 65535
    assert len(ports) == 65535


def test_custom_explicit_list():
    ports = get_ports_from_mode(_cfg("custom", custom_ports=[443, 80, 22, 80]))
    assert ports == sorted({443, 80, 22})


def test_custom_port_range():
    ports = get_ports_from_mode(_cfg("custom", port_range=(100, 110)))
    assert ports == list(range(100, 111))


def test_custom_port_range_min_clamped():
    ports = get_ports_from_mode(_cfg("custom", port_range=(0, 5)))
    assert ports[0] == 1


def test_custom_port_range_max_clamped():
    ports = get_ports_from_mode(_cfg("custom", port_range=(65530, 70000)))
    assert ports[-1] == 65535


def test_custom_no_ports_no_range_returns_empty():
    assert get_ports_from_mode(_cfg("custom")) == []


def test_unknown_mode_returns_empty():
    cfg = ScanConfig(targets=["x"], mode="fast")
    cfg.mode = "unknown"
    assert get_ports_from_mode(cfg) == []


# ---------------------------------------------------------------------------
# ScanResult properties
# ---------------------------------------------------------------------------


@pytest.fixture
def scan_result():
    t0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    t1 = datetime(2024, 1, 1, 0, 0, 5, tzinfo=UTC)
    return ScanResult(
        target="192.168.1.1",
        target_ip="192.168.1.1",
        start_time=t0,
        end_time=t1,
        results={
            80: PortResult(port=80, state="open"),
            443: PortResult(port=443, state="open"),
            22: PortResult(port=22, state="filtered"),
            25: PortResult(port=25, state="closed"),
        },
    )


def test_scan_result_duration(scan_result):
    assert scan_result.duration == pytest.approx(5.0)


def test_scan_result_open_ports(scan_result):
    assert sorted(scan_result.open_ports) == [80, 443]


def test_scan_result_filtered_not_in_open(scan_result):
    assert 22 not in scan_result.open_ports


def test_scan_result_closed_not_in_open(scan_result):
    assert 25 not in scan_result.open_ports


def test_scan_result_empty_open_ports():
    t = datetime(2024, 1, 1, tzinfo=UTC)
    r = ScanResult(target="x", target_ip="x", start_time=t, end_time=t)
    assert r.open_ports == []


# ---------------------------------------------------------------------------
# PortResult defaults
# ---------------------------------------------------------------------------


def test_port_result_default_service():
    assert PortResult(port=80, state="open").service == "unknown"


def test_port_result_default_banner_none():
    assert PortResult(port=80, state="open").banner is None


def test_port_result_default_response_time_none():
    assert PortResult(port=80, state="open").response_time is None


# ---------------------------------------------------------------------------
# _grab_banner
# ---------------------------------------------------------------------------


def test_grab_banner_http_port_sends_head(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"HTTP/1.1 200 OK\r\n"
    result = _grab_banner(mock_sock, "1.2.3.4", 80)
    mock_sock.send.assert_called_once_with(b"HEAD / HTTP/1.0\r\n\r\n")
    assert result is not None


def test_grab_banner_ftp_sends_help(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"220 FTP ready\r\n"
    _grab_banner(mock_sock, "1.2.3.4", 21)
    mock_sock.send.assert_called_once_with(b"HELP\r\n")


def test_grab_banner_smtp_sends_ehlo(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"220 smtp\r\n"
    _grab_banner(mock_sock, "1.2.3.4", 25)
    mock_sock.send.assert_called_once_with(b"EHLO scan.local\r\n")


def test_grab_banner_ssh_no_send(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"SSH-2.0-OpenSSH_8.0\r\n"
    _grab_banner(mock_sock, "1.2.3.4", 22)
    mock_sock.send.assert_not_called()


def test_grab_banner_other_sends_crlf(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"banner\r\n"
    _grab_banner(mock_sock, "1.2.3.4", 9999)
    mock_sock.send.assert_called_once_with(b"\r\n")


def test_grab_banner_empty_response_returns_none(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b""
    result = _grab_banner(mock_sock, "1.2.3.4", 80)
    assert result is None


def test_grab_banner_truncated_to_200(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"X" * 300
    result = _grab_banner(mock_sock, "1.2.3.4", 80)
    assert len(result) == 200


def test_grab_banner_exception_returns_none(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.side_effect = Exception("error")
    result = _grab_banner(mock_sock, "1.2.3.4", 80)
    assert result is None


def test_grab_banner_https_port(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"HTTP/1.1 400\r\n"
    _grab_banner(mock_sock, "1.2.3.4", 443)
    mock_sock.send.assert_called_once_with(b"HEAD / HTTP/1.0\r\n\r\n")


def test_grab_banner_8080_port(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"HTTP/1.1 200\r\n"
    _grab_banner(mock_sock, "1.2.3.4", 8080)
    mock_sock.send.assert_called_once_with(b"HEAD / HTTP/1.0\r\n\r\n")


# ---------------------------------------------------------------------------
# _scan_tcp_port
# ---------------------------------------------------------------------------


def test_scan_tcp_port_open(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.return_value = 0
    mock_sock.recv.return_value = b""
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)
    mocker.patch("nadzoring.network_base.port_scanner.get_service_on_port", return_value="http")

    port, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=False)
    assert result.state == "open"
    assert result.service == "http"
    assert port == 80


def test_scan_tcp_port_open_with_banner(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.return_value = 0
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)
    mocker.patch("nadzoring.network_base.port_scanner.get_service_on_port", return_value="http")
    mocker.patch(
        "nadzoring.network_base.port_scanner._grab_banner",
        return_value="HTTP/1.1 200 OK",
    )

    port, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=True)
    assert result.banner == "HTTP/1.1 200 OK"


def test_scan_tcp_port_open_banner_none(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.return_value = 0
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)
    mocker.patch("nadzoring.network_base.port_scanner.get_service_on_port", return_value="http")
    mocker.patch("nadzoring.network_base.port_scanner._grab_banner", return_value=None)

    _, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=True)
    assert result.banner is None


def test_scan_tcp_port_closed_111(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.return_value = 111
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=False)
    assert result.state == "closed"


def test_scan_tcp_port_closed_61(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.return_value = 61
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=False)
    assert result.state == "closed"


def test_scan_tcp_port_filtered_other_code(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.return_value = 13
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=False)
    assert result.state == "filtered"


def test_scan_tcp_port_timeout_error(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.side_effect = TimeoutError
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=False)
    assert result.state == "filtered"


def test_scan_tcp_port_generic_exception(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.side_effect = OSError("err")
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=False)
    assert result.state == "filtered"


def test_scan_tcp_port_response_time_set(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.return_value = 0
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)
    mocker.patch("nadzoring.network_base.port_scanner.get_service_on_port", return_value="http")

    _, result = _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=False)
    assert result.response_time is not None


def test_scan_tcp_sock_closed_on_exception(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect_ex.side_effect = OSError("err")
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)
    _scan_tcp_port("192.168.1.1", 80, TIMEOUT_CONFIG, grab_banner=False)
    mock_sock.close.assert_called_once()


# ---------------------------------------------------------------------------
# _scan_udp_port
# ---------------------------------------------------------------------------


def test_scan_udp_open_on_response(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recvfrom.return_value = (b"data", ("1.2.3.4", 53))
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)
    mocker.patch("nadzoring.network_base.port_scanner.get_service_on_port", return_value="dns")

    _, result = _scan_udp_port("192.168.1.1", 53, TIMEOUT_CONFIG)
    assert result.state == "open"
    assert result.service == "dns"


def test_scan_udp_open_filtered_on_timeout(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recvfrom.side_effect = TimeoutError
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_udp_port("192.168.1.1", 53, TIMEOUT_CONFIG)
    assert result.state == "open|filtered"


def test_scan_udp_closed_on_errno_10054(mocker):
    mock_sock = mocker.MagicMock()
    err = OSError()
    err.errno = 10054
    mock_sock.recvfrom.side_effect = err
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_udp_port("192.168.1.1", 53, TIMEOUT_CONFIG)
    assert result.state == "closed"


def test_scan_udp_other_oserror_stays_filtered(mocker):
    mock_sock = mocker.MagicMock()
    err = OSError()
    err.errno = 111
    mock_sock.recvfrom.side_effect = err
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_udp_port("192.168.1.1", 53, TIMEOUT_CONFIG)
    assert result.state == "filtered"


def test_scan_udp_generic_exception(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.sendto.side_effect = Exception("err")
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)

    _, result = _scan_udp_port("192.168.1.1", 53, TIMEOUT_CONFIG)
    assert result.state == "filtered"


def test_scan_udp_response_time_set(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recvfrom.return_value = (b"data", ("1.2.3.4", 53))
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)
    mocker.patch("nadzoring.network_base.port_scanner.get_service_on_port", return_value="dns")

    _, result = _scan_udp_port("192.168.1.1", 53, TIMEOUT_CONFIG)
    assert result.response_time is not None


def test_scan_udp_sock_closed(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.sendto.side_effect = Exception("err")
    mocker.patch("nadzoring.network_base.port_scanner.socket.socket", return_value=mock_sock)
    _scan_udp_port("192.168.1.1", 53, TIMEOUT_CONFIG)
    mock_sock.close.assert_called_once()


# ---------------------------------------------------------------------------
# _scan_target_ports
# ---------------------------------------------------------------------------


def test_scan_target_ports_tcp(mocker):
    mocker.patch(
        "nadzoring.network_base.port_scanner._scan_tcp_port",
        return_value=(80, PortResult(port=80, state="open")),
    )
    cfg = ScanConfig(
        targets=["192.168.1.1"],
        mode="custom",
        custom_ports=[80],
        max_workers=1,
        grab_banner=False,
        timeout_config=TIMEOUT_CONFIG,
    )
    result = _scan_target_ports("192.168.1.1", [80], cfg, "192.168.1.1")
    assert isinstance(result, ScanResult)
    assert 80 in result.results


def test_scan_target_ports_udp(mocker):
    mocker.patch(
        "nadzoring.network_base.port_scanner._scan_udp_port",
        return_value=(53, PortResult(port=53, state="open|filtered")),
    )
    cfg = ScanConfig(
        targets=["192.168.1.1"],
        mode="custom",
        custom_ports=[53],
        protocol="udp",
        max_workers=1,
        grab_banner=False,
        timeout_config=TIMEOUT_CONFIG,
    )
    result = _scan_target_ports("192.168.1.1", [53], cfg, "192.168.1.1")
    assert 53 in result.results


def test_scan_target_ports_progress_callback(mocker):
    mocker.patch(
        "nadzoring.network_base.port_scanner._scan_tcp_port",
        return_value=(80, PortResult(port=80, state="open")),
    )
    calls = []
    cfg = ScanConfig(
        targets=["x"],
        mode="custom",
        custom_ports=[80],
        max_workers=1,
        grab_banner=False,
        timeout_config=TIMEOUT_CONFIG,
        progress_callback=lambda msg, done, total: calls.append((msg, done, total)),
    )
    _scan_target_ports("192.168.1.1", [80], cfg, "x")
    assert len(calls) > 0
    assert any("Completed" in c[0] for c in calls)


# ---------------------------------------------------------------------------
# scan_ports
# ---------------------------------------------------------------------------


def test_scan_ports_unresolvable_target(mocker):
    mocker.patch("nadzoring.network_base.port_scanner.resolve_target", return_value=None)
    cfg = ScanConfig(targets=["bad.host"], mode="fast", timeout_config=TIMEOUT_CONFIG)
    assert scan_ports(cfg) == []


def test_scan_ports_empty_port_list(mocker):
    cfg = ScanConfig(targets=["x"], mode="custom", timeout_config=TIMEOUT_CONFIG)
    assert scan_ports(cfg) == []


def test_scan_ports_returns_scan_result(mocker):
    mocker.patch("nadzoring.network_base.port_scanner.resolve_target", return_value="1.2.3.4")
    mocker.patch(
        "nadzoring.network_base.port_scanner._scan_target_ports",
        return_value=mocker.MagicMock(spec=ScanResult),
    )
    cfg = ScanConfig(targets=["host"], mode="fast", timeout_config=TIMEOUT_CONFIG)
    results = scan_ports(cfg)
    assert len(results) == 1


def test_scan_ports_multiple_targets(mocker):
    mocker.patch("nadzoring.network_base.port_scanner.resolve_target", return_value="1.1.1.1")
    mocker.patch(
        "nadzoring.network_base.port_scanner._scan_target_ports",
        return_value=mocker.MagicMock(spec=ScanResult),
    )
    cfg = ScanConfig(targets=["h1", "h2", "h3"], mode="fast", timeout_config=TIMEOUT_CONFIG)
    assert len(scan_ports(cfg)) == 3


def test_scan_ports_mixed_targets(mocker):
    mocker.patch(
        "nadzoring.network_base.port_scanner.resolve_target",
        side_effect=lambda t: None if t == "bad" else "1.1.1.1",
    )
    mocker.patch(
        "nadzoring.network_base.port_scanner._scan_target_ports",
        return_value=mocker.MagicMock(spec=ScanResult),
    )
    cfg = ScanConfig(targets=["good", "bad"], mode="fast", timeout_config=TIMEOUT_CONFIG)
    assert len(scan_ports(cfg)) == 1
