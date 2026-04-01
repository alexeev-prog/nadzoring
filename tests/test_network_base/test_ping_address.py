# tests/test_network_base/test_ping_address.py
"""Tests for nadzoring.network_base.ping_address — 100% coverage."""

from nadzoring.network_base.ping_address import _normalize_address, ping_addr


def test_plain_hostname_unchanged():
    assert _normalize_address("example.com") == "example.com"


def test_http_scheme_stripped():
    assert _normalize_address("http://example.com") == "example.com"


def test_https_scheme_stripped():
    assert _normalize_address("https://example.com") == "example.com"


def test_http_with_path_stripped():
    assert _normalize_address("http://example.com/some/path") == "example.com"


def test_https_with_path_and_query():
    assert _normalize_address("https://example.com/path?q=1") == "example.com"


def test_ip_unchanged():
    assert _normalize_address("192.168.1.1") == "192.168.1.1"


def test_http_ip_scheme_stripped():
    assert _normalize_address("http://192.168.1.1") == "192.168.1.1"


def test_https_with_port():
    result = _normalize_address("https://example.com:8443/path")
    assert result == "example.com:8443"


def test_subdomain_unchanged():
    assert _normalize_address("sub.example.com") == "sub.example.com"


def test_www_two_parts_not_stripped():
    assert _normalize_address("www.example.com") == "www.example.com"


def test_empty_string():
    result = _normalize_address("")
    assert isinstance(result, str)


def test_reachable_returns_true(mocker):
    mocker.patch("nadzoring.network_base.ping_address.ping3.ping", return_value=0.042)
    assert ping_addr("8.8.8.8") is True


def test_none_response_returns_false(mocker):
    mocker.patch("nadzoring.network_base.ping_address.ping3.ping", return_value=None)
    assert ping_addr("192.0.2.1") is False


def test_zero_rtt_returns_true(mocker):
    mocker.patch("nadzoring.network_base.ping_address.ping3.ping", return_value=0)
    assert ping_addr("127.0.0.1") is True


def test_url_normalized_before_ping(mocker):
    mock = mocker.patch("nadzoring.network_base.ping_address.ping3.ping", return_value=0.01)
    ping_addr("https://example.com")
    mock.assert_called_once_with("example.com")


def test_http_url_normalized_before_ping(mocker):
    mock = mocker.patch("nadzoring.network_base.ping_address.ping3.ping", return_value=0.01)
    ping_addr("http://example.com/path")
    mock.assert_called_once_with("example.com")


def test_plain_ip_passed_directly(mocker):
    mock = mocker.patch("nadzoring.network_base.ping_address.ping3.ping", return_value=0.05)
    ping_addr("1.2.3.4")
    mock.assert_called_once_with("1.2.3.4")


def test_www_url_ping(mocker):
    mock = mocker.patch("nadzoring.network_base.ping_address.ping3.ping", return_value=0.03)
    ping_addr("https://www.example.com")
    mock.assert_called_once_with("www.example.com")


def test_exception_returns_false(mocker):
    mocker.patch(
        "nadzoring.network_base.ping_address.ping3.ping",
        side_effect=Exception("socket error"),
    )
    assert ping_addr("example.com") is False


def test_oserror_returns_false(mocker):
    mocker.patch(
        "nadzoring.network_base.ping_address.ping3.ping",
        side_effect=OSError("unreachable"),
    )
    assert ping_addr("10.0.0.1") is False


def test_return_type_is_bool(mocker):
    mocker.patch("nadzoring.network_base.ping_address.ping3.ping", return_value=0.1)
    assert isinstance(ping_addr("1.1.1.1"), bool)
