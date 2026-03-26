"""Tests for nadzoring.network_base.ping_address."""

from unittest.mock import patch

from nadzoring.network_base.ping_address import _normalize_address, ping_addr

# ---------------------------------------------------------------------------
# _normalize_address
# ---------------------------------------------------------------------------


class TestNormalizeAddress:
    def test_plain_hostname_unchanged(self):
        assert _normalize_address("example.com") == "example.com"

    def test_strips_http_scheme(self):
        assert _normalize_address("http://example.com") == "example.com"

    def test_strips_https_scheme(self):
        assert _normalize_address("https://example.com") == "example.com"

    def test_strips_http_with_path(self):
        result = _normalize_address("http://example.com/some/path")
        assert result == "example.com"

    def test_strips_https_with_path_and_query(self):
        result = _normalize_address("https://example.com/path?q=1")
        assert result == "example.com"

    def test_ip_address_unchanged(self):
        assert _normalize_address("192.168.1.1") == "192.168.1.1"

    def test_http_ip_strips_scheme(self):
        assert _normalize_address("http://192.168.1.1") == "192.168.1.1"

    def test_www_prefix_not_stripped_when_only_two_parts(self):
        # "www.example.com" → 3 parts, but condition is len(parts) > 2
        # parts = ["www", "example.com"] when split with maxsplit=1 → len == 2
        # so www is NOT stripped
        result = _normalize_address("www.example.com")
        assert result == "www.example.com"

    def test_subdomain_other_than_www_unchanged(self):
        assert _normalize_address("sub.example.com") == "sub.example.com"

    def test_empty_string(self):
        result = _normalize_address("")
        assert isinstance(result, str)

    def test_https_with_port(self):
        result = _normalize_address("https://example.com:8443/path")
        assert result == "example.com:8443"


# ---------------------------------------------------------------------------
# ping_addr
# ---------------------------------------------------------------------------


class TestPingAddr:
    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_reachable_host_returns_true(self, mock_ping):
        mock_ping.return_value = 0.042
        assert ping_addr("8.8.8.8") is True

    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_unreachable_host_returns_false(self, mock_ping):
        mock_ping.return_value = None
        assert ping_addr("192.0.2.1") is False

    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_url_is_normalized_before_ping(self, mock_ping):
        mock_ping.return_value = 0.01
        ping_addr("https://example.com")
        mock_ping.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_http_url_is_normalized_before_ping(self, mock_ping):
        mock_ping.return_value = 0.01
        ping_addr("http://example.com/path")
        mock_ping.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_exception_returns_false(self, mock_ping):
        mock_ping.side_effect = Exception("socket error")
        assert ping_addr("example.com") is False

    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_os_error_returns_false(self, mock_ping):
        mock_ping.side_effect = OSError("network unreachable")
        assert ping_addr("10.0.0.1") is False

    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_returns_bool(self, mock_ping):
        mock_ping.return_value = 0.1
        result = ping_addr("1.1.1.1")
        assert isinstance(result, bool)

    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_rtt_zero_is_truthy_returns_true(self, mock_ping):
        # ping3 returns 0 for localhost on some systems — not None
        mock_ping.return_value = 0
        assert ping_addr("127.0.0.1") is True

    @patch("nadzoring.network_base.ping_address.ping3.ping")
    def test_plain_ip_passed_directly(self, mock_ping):
        mock_ping.return_value = 0.05
        ping_addr("1.2.3.4")
        mock_ping.assert_called_once_with("1.2.3.4")
