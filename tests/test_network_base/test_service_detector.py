# tests/test_network_base/test_service_detector.py

import nadzoring.network_base.service_detector as _sd_module
from nadzoring.network_base.service_detector import (
    SERVICE_SIGNATURES,
    ServiceDetectionResult,
    _analyze_banner,
    _get_probe_for_port,
    detect_service_on_host,
)
from nadzoring.utils.timeout import TimeoutConfig


def test_probe_port_80():
    assert _get_probe_for_port(80) == b"HEAD / HTTP/1.0\r\n\r\n"


def test_probe_port_443():
    assert _get_probe_for_port(443) == b"HEAD / HTTP/1.0\r\n\r\n"


def test_probe_port_8080():
    assert _get_probe_for_port(8080) == b"HEAD / HTTP/1.0\r\n\r\n"


def test_probe_port_8443():
    assert _get_probe_for_port(8443) == b"HEAD / HTTP/1.0\r\n\r\n"


def test_probe_port_21():
    assert _get_probe_for_port(21) == b"HELP\r\n"


def test_probe_port_25():
    assert _get_probe_for_port(25) == b"EHLO detect.local\r\n"


def test_probe_port_22_empty_bytes():
    assert _get_probe_for_port(22) == b""


def test_probe_port_110_empty_bytes():
    assert _get_probe_for_port(110) == b""


def test_probe_port_143_empty_bytes():
    assert _get_probe_for_port(143) == b""


def test_probe_unknown_port_returns_none():
    assert _get_probe_for_port(9999) is None


def test_probe_return_type_bytes_or_none():
    result = _get_probe_for_port(80)
    assert isinstance(result, bytes)
    result_none = _get_probe_for_port(12345)
    assert result_none is None


def test_analyze_ssh_banner():
    assert _analyze_banner("SSH-2.0-OpenSSH_8.0", 22) == "SSH"


def test_analyze_openssh_banner():
    assert _analyze_banner("OpenSSH server", 22) == "SSH"


def test_analyze_http_banner():
    assert _analyze_banner("HTTP/1.1 200 OK\r\nContent-Type: text/html", 80) == "HTTP"


def test_analyze_html_doctype_banner():
    assert _analyze_banner("<!DOCTYPE html>", 80) == "HTTP"


def test_analyze_html_tag_banner():
    assert _analyze_banner("<html>", 80) == "HTTP"


def test_analyze_smtp_banner():
    assert _analyze_banner("220 mail.example.com ESMTP Postfix", 25) == "SMTP"


def test_analyze_esmtp_banner():
    assert _analyze_banner("ESMTP ready", 25) == "SMTP"


def test_analyze_pop3_ok_banner():
    assert _analyze_banner("+OK POP3 server ready", 110) == "POP3"


def test_analyze_pop3_err_banner():
    assert _analyze_banner("-ERR unknown command", 110) == "POP3"


def test_analyze_imap_ok_banner():
    assert _analyze_banner("* OK IMAP server ready", 143) == "IMAP"


def test_analyze_imap_keyword():
    assert _analyze_banner("IMAP4rev1 ready", 143) == "IMAP"


def test_analyze_ftp_banner():
    result = _analyze_banner("FTP server ready", 21)
    assert result is not None


def test_analyze_ftp_specific():
    result = _analyze_banner("220 FTP Welcome", 21)
    assert result is not None


def test_analyze_mysql_banner():
    assert _analyze_banner("5.7.30-mysql", 3306) == "MySQL"


def test_analyze_mariadb_banner():
    assert _analyze_banner("10.3.27-MariaDB", 3306) == "MySQL"


def test_analyze_postgresql_banner():
    assert _analyze_banner("PostgreSQL 13.0", 5432) == "PostgreSQL"


def test_analyze_redis_ok_banner():
    assert _analyze_banner("+OK", 6379) == "POP3"


def test_analyze_redis_specific():
    assert _analyze_banner("redis server ready", 6379) == "Redis"


def test_analyze_mongodb_banner():
    assert _analyze_banner("mongodb server", 27017) == "MongoDB"


def test_analyze_telnet_banner():
    assert _analyze_banner("Telnet session", 23) == "Telnet"


def test_analyze_login_prompt():
    assert _analyze_banner("login: ", 23) == "Telnet"


def test_analyze_fallback_port_80():
    assert _analyze_banner("unknown banner", 80) == "HTTP"


def test_analyze_fallback_port_443():
    assert _analyze_banner("unknown banner", 443) == "HTTPS"


def test_analyze_fallback_port_22():
    assert _analyze_banner("unknown banner", 22) == "SSH"


def test_analyze_fallback_port_21():
    assert _analyze_banner("unknown banner", 21) == "FTP"


def test_analyze_fallback_port_25():
    assert _analyze_banner("unknown banner", 25) == "SMTP"


def test_analyze_no_match_unknown_port_returns_none():
    assert _analyze_banner("totally unknown", 9999) is None


def test_analyze_empty_banner_unknown_port():
    assert _analyze_banner("", 9999) is None


def test_analyze_banner_bytes_pattern_matching():
    banner_bytes = b"HTTP/1.1 200 OK"
    result = _analyze_banner(banner_bytes.decode(), 80)
    assert result == "HTTP"


def test_analyze_banner_with_byte_signature_match():
    banner = "SSH-2.0-OpenSSH"
    result = _analyze_banner(banner, 22)
    assert result == "SSH"


def test_analyze_banner_str_signature_branch(mocker):
    fake_signatures = {"CUSTOM": ["CUSTOM_BANNER_STRING"]}
    mocker.patch.object(_sd_module, "SERVICE_SIGNATURES", fake_signatures)
    result = _analyze_banner("custom_banner_string extra data", 9999)
    assert result == "CUSTOM"


def test_service_signatures_structure():
    assert isinstance(SERVICE_SIGNATURES, dict)
    assert "SSH" in SERVICE_SIGNATURES
    assert "HTTP" in SERVICE_SIGNATURES
    assert isinstance(SERVICE_SIGNATURES["SSH"], list)


def test_detect_success_banner_method(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"SSH-2.0-OpenSSH_8.0\r\n"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="ssh",
    )

    result = detect_service_on_host("localhost", 22)
    assert result.method == "banner"
    assert result.detected_service == "SSH"
    assert result.banner is not None


def test_detect_banner_truncated_to_200(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"SSH-2.0-" + b"X" * 300
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="ssh",
    )

    result = detect_service_on_host("localhost", 22)
    assert len(result.banner) <= 200


def test_detect_sends_probe_when_flag_true(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"HTTP/1.1 200 OK\r\n"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    detect_service_on_host("localhost", 80, send_probe=True)
    mock_sock.send.assert_called_once_with(b"HEAD / HTTP/1.0\r\n\r\n")


def test_detect_no_probe_for_unknown_port_when_send_probe_true(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"some banner"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="unknown",
    )

    detect_service_on_host("localhost", 9999, send_probe=True)
    mock_sock.send.assert_not_called()


def test_detect_no_probe_sent_when_flag_false(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"HTTP/1.1 200 OK\r\n"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    detect_service_on_host("localhost", 80, send_probe=False)
    mock_sock.send.assert_not_called()


def test_detect_empty_probe_not_sent(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"SSH-2.0-OpenSSH\r\n"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="ssh",
    )

    detect_service_on_host("localhost", 22, send_probe=True)
    mock_sock.send.assert_not_called()


def test_detect_connection_refused(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect.side_effect = ConnectionRefusedError
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    result = detect_service_on_host("localhost", 80)
    assert result.method == "failed"
    assert result.error == "Connection refused"
    assert result.detected_service is None


def test_detect_timeout(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect.side_effect = TimeoutError
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    result = detect_service_on_host("localhost", 80)
    assert result.method == "failed"
    assert result.error == "Connection timeout"


def test_detect_generic_exception(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect.side_effect = OSError("network down")
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    result = detect_service_on_host("localhost", 80)
    assert result.method == "failed"
    assert "network down" in result.error


def test_detect_sock_closed_on_success(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"SSH-2.0\r\n"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="ssh",
    )

    detect_service_on_host("localhost", 22)
    mock_sock.close.assert_called_once()


def test_detect_sock_closed_on_failure(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect.side_effect = ConnectionRefusedError
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    detect_service_on_host("localhost", 80)
    mock_sock.close.assert_called_once()


def test_detect_guessed_service_always_set(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect.side_effect = ConnectionRefusedError
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    result = detect_service_on_host("localhost", 80)
    assert result.guessed_service == "http"


def test_detect_port_field_set(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect.side_effect = ConnectionRefusedError
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    result = detect_service_on_host("localhost", 8080)
    assert result.port == 8080


def test_detect_with_custom_timeout_config(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"SSH-2.0\r\n"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="ssh",
    )

    cfg = TimeoutConfig(connect=0.5, read=1.0, lifetime=3.0)
    result = detect_service_on_host("localhost", 22, timeout_config=cfg)
    assert result.method == "banner"
    mock_sock.settimeout.assert_called_once_with(0.5)


def test_detect_banner_with_probe_for_http(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"HTTP/1.1 200 OK\r\n"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    result = detect_service_on_host("localhost", 8080, send_probe=True)
    assert result.detected_service == "HTTP"


def test_result_error_default_none():
    r = ServiceDetectionResult(
        port=80,
        detected_service="HTTP",
        guessed_service="http",
        banner="HTTP/1.1 200",
        method="banner",
    )
    assert r.error is None


def test_detect_with_default_timeout_config(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.recv.return_value = b"SSH-2.0\r\n"
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="ssh",
    )

    result = detect_service_on_host("localhost", 22, timeout_config=None)
    assert result.method == "banner"
    mock_sock.settimeout.assert_called_once()


def test_detect_socket_timeout_exception(mocker):
    mock_sock = mocker.MagicMock()
    mock_sock.connect.side_effect = TimeoutError("timed out")
    mocker.patch("nadzoring.network_base.service_detector.socket.socket", return_value=mock_sock)
    mocker.patch(
        "nadzoring.network_base.service_detector.get_service_on_port",
        return_value="http",
    )

    result = detect_service_on_host("localhost", 80)
    assert result.method == "failed"
    assert "timed out" in result.error or result.error == "Connection timeout"
