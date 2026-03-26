"""Tests for nadzoring.network_base.router_ip."""

import shlex
from socket import gaierror
from unittest.mock import MagicMock, patch

from nadzoring.network_base.router_ip import (
    check_ipv4,
    check_ipv6,
    get_ip_from_host,
    router_ip,
)

# ---------------------------------------------------------------------------
# get_ip_from_host
# ---------------------------------------------------------------------------


class TestGetIpFromHost:
    @patch("nadzoring.network_base.router_ip.gethostbyname")
    def test_valid_hostname_resolved(self, mock_ghbn):
        mock_ghbn.return_value = "93.184.216.34"
        assert get_ip_from_host("example.com") == "93.184.216.34"
        mock_ghbn.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.router_ip.gethostbyname")
    def test_gaierror_returns_original_hostname(self, mock_ghbn):
        mock_ghbn.side_effect = gaierror("Name not known")
        assert get_ip_from_host("invalid.local") == "invalid.local"

    @patch("nadzoring.network_base.router_ip.gethostbyname")
    def test_ip_string_passes_through_gethostbyname(self, mock_ghbn):
        mock_ghbn.return_value = "192.168.1.1"
        assert get_ip_from_host("192.168.1.1") == "192.168.1.1"
        mock_ghbn.assert_called_once_with("192.168.1.1")

    @patch("nadzoring.network_base.router_ip.gethostbyname")
    def test_empty_string_gaierror_returns_empty_string(self, mock_ghbn):
        mock_ghbn.side_effect = gaierror
        assert get_ip_from_host("") == ""

    @patch("nadzoring.network_base.router_ip.gethostbyname")
    def test_return_type_is_str(self, mock_ghbn):
        mock_ghbn.return_value = "1.2.3.4"
        result = get_ip_from_host("host")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# check_ipv4
# ---------------------------------------------------------------------------


class TestCheckIpv4:
    # Valid addresses
    def test_standard_ipv4_returned_unchanged(self):
        assert check_ipv4("192.168.1.1") == "192.168.1.1"

    def test_loopback(self):
        assert check_ipv4("127.0.0.1") == "127.0.0.1"

    def test_all_zeros(self):
        assert check_ipv4("0.0.0.0") == "0.0.0.0"

    def test_broadcast(self):
        assert check_ipv4("255.255.255.255") == "255.255.255.255"

    def test_leading_zeros_normalized(self):
        # "192.168.001.001" → valid 4-part all-digit → normalized to "192.168.1.1"
        assert check_ipv4("192.168.001.001") == "192.168.1.1"

    def test_single_octet_boundary_lower(self):
        assert check_ipv4("10.0.0.0") == "10.0.0.0"

    def test_single_octet_boundary_upper(self):
        assert check_ipv4("10.255.255.254") == "10.255.255.254"

    # Invalid → falls back to get_ip_from_host
    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_hostname_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "1.2.3.4"
        result = check_ipv4("example.com")
        assert result == "1.2.3.4"
        mock_giph.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_octet_out_of_range_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "256.0.0.1"
        result = check_ipv4("256.0.0.1")
        mock_giph.assert_called_once_with("256.0.0.1")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_too_many_octets_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "1.2.3.4.5"
        check_ipv4("1.2.3.4.5")
        mock_giph.assert_called_once_with("1.2.3.4.5")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_too_few_octets_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "192.168.1"
        check_ipv4("192.168.1")
        mock_giph.assert_called_once_with("192.168.1")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_empty_string_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = ""
        check_ipv4("")
        mock_giph.assert_called_once_with("")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_alpha_in_octet_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "0.0.0.0"
        check_ipv4("192.168.1.abc")
        mock_giph.assert_called_once_with("192.168.1.abc")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_none_string_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "None"
        result = check_ipv4("None")
        assert result == "None"

    def test_return_type_is_str(self):
        assert isinstance(check_ipv4("10.0.0.1"), str)


# ---------------------------------------------------------------------------
# check_ipv6
# ---------------------------------------------------------------------------


class TestCheckIpv6:
    # Valid addresses
    def test_compressed_ipv6(self):
        assert check_ipv6("2001:db8::1") == "2001:db8::1"

    def test_loopback(self):
        assert check_ipv6("::1") == "::1"

    def test_unspecified(self):
        assert check_ipv6("::") == "::"

    def test_full_ipv6(self):
        addr = "2001:0db8:0000:0000:0000:0000:0000:0001"
        assert check_ipv6(addr) == addr

    def test_ipv4_mapped(self):
        assert check_ipv6("::ffff:192.168.1.1") == "::ffff:192.168.1.1"

    def test_ipv4_compatible(self):
        assert check_ipv6("::192.168.1.1") == "::192.168.1.1"

    def test_link_local(self):
        assert check_ipv6("fe80::1") == "fe80::1"

    # Invalid → falls back to get_ip_from_host
    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_hostname_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "2001:db8::1"
        result = check_ipv6("example.com")
        assert result == "2001:db8::1"
        mock_giph.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_ipv4_string_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "192.168.1.1"
        check_ipv6("192.168.1.1")
        mock_giph.assert_called_once_with("192.168.1.1")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_invalid_hex_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "2001:dbg::1"
        check_ipv6("2001:dbg::1")
        mock_giph.assert_called_once_with("2001:dbg::1")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_too_many_groups_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = "::1"
        check_ipv6("1:2:3:4:5:6:7:8:9")
        mock_giph.assert_called_once_with("1:2:3:4:5:6:7:8:9")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_empty_string_calls_get_ip_from_host(self, mock_giph):
        mock_giph.return_value = ""
        check_ipv6("")
        mock_giph.assert_called_once_with("")

    def test_return_type_is_str(self):
        assert isinstance(check_ipv6("::1"), str)


# ---------------------------------------------------------------------------
# router_ip — Linux
# ---------------------------------------------------------------------------


def _mock_route_output(gateway: str) -> MagicMock:
    """Helper: build a bytes-like mock for check_output on Linux."""
    mock_bytes = MagicMock()
    mock_bytes.decode.return_value = f"default        {gateway}     0.0.0.0         UG    100    0        0 eth0\n"
    return mock_bytes


class TestRouterIpLinux:
    @patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.1.1")
    def test_ipv4_success(self, mock_cv4, mock_co, mock_sys):
        mock_co.return_value = _mock_route_output("192.168.1.1")
        assert router_ip(ipv6=False) == "192.168.1.1"
        mock_co.assert_called_once_with(shlex.split("route -n"))
        mock_cv4.assert_called_once_with("192.168.1.1")

    @patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv6", return_value="2001:db8::1")
    def test_ipv6_success(self, mock_cv6, mock_co, mock_sys):
        mock_co.return_value = _mock_route_output("2001:db8::1")
        assert router_ip(ipv6=True) == "2001:db8::1"
        mock_cv6.assert_called_once_with("2001:db8::1")

    @patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.1.1")
    def test_hostname_gateway_resolved_via_check_ipv4(self, mock_cv4, mock_co, mock_sys):
        mock_co.return_value = _mock_route_output("gateway.local")
        result = router_ip(ipv6=False)
        assert result == "192.168.1.1"
        mock_cv4.assert_called_once_with("gateway.local")

    @patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.1.1")
    def test_multiple_default_routes_takes_first(self, mock_cv4, mock_co, mock_sys):
        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = (
            "default        192.168.1.1     0.0.0.0         UG    100    0        0 eth0\n"
            "default        10.0.0.1        0.0.0.0         UG    200    0        0 eth1\n"
        )
        mock_co.return_value = mock_bytes
        assert router_ip() == "192.168.1.1"
        mock_cv4.assert_called_once_with("192.168.1.1")

    @patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    @patch("nadzoring.network_base.router_ip.check_output")
    def test_no_ug_lines_returns_none(self, mock_co, mock_sys):
        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = "Kernel IP routing table\nDestination   Gateway\n"
        mock_co.return_value = mock_bytes
        assert router_ip() is None

    @patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    @patch("nadzoring.network_base.router_ip.check_output", side_effect=OSError)
    def test_oserror_returns_none(self, mock_co, mock_sys):
        assert router_ip() is None

    @patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv4", return_value="10.0.0.1")
    def test_extra_whitespace_in_route_output(self, mock_cv4, mock_co, mock_sys):
        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = "default   10.0.0.1   0.0.0.0   UG   100   0   0   eth0\n"
        mock_co.return_value = mock_bytes
        assert router_ip() == "10.0.0.1"

    @patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    @patch("nadzoring.network_base.router_ip.check_output")
    def test_ipv4_is_default(self, mock_co, mock_sys):
        """Calling router_ip() without args should use ipv6=False."""
        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = "default        192.168.0.1     0.0.0.0         UG    100    0        0 eth0\n"
        mock_co.return_value = mock_bytes
        with patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.0.1") as cv4:
            router_ip()
            cv4.assert_called_once()


# ---------------------------------------------------------------------------
# router_ip — Windows
# ---------------------------------------------------------------------------


class TestRouterIpWindows:
    @patch("nadzoring.network_base.router_ip.system", return_value="Windows")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.1.1")
    def test_windows_ipv4_success(self, mock_cv4, mock_co, mock_sys):
        mock_bytes = MagicMock()
        # Windows "route PRINT" output: gateway is at index [-3] of the matching line
        mock_bytes.decode.return_value = (
            "Network Destination  Netmask   Gateway     Interface  Metric\n"
            "0.0.0.0              0.0.0.0   192.168.1.1 192.168.1.100  25\n"
        )
        mock_co.return_value = mock_bytes
        result = router_ip(ipv6=False)
        assert result == "192.168.1.1"

    @patch("nadzoring.network_base.router_ip.system", return_value="Windows")
    @patch("nadzoring.network_base.router_ip.check_output", side_effect=OSError)
    def test_windows_oserror_returns_none(self, mock_co, mock_sys):
        assert router_ip() is None

    @patch("nadzoring.network_base.router_ip.system", return_value="Windows")
    @patch("nadzoring.network_base.router_ip.check_output")
    def test_windows_no_matching_lines_returns_none(self, mock_co, mock_sys):
        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = "nothing here\n"
        mock_co.return_value = mock_bytes
        assert router_ip() is None


# ---------------------------------------------------------------------------
# router_ip — unsupported OS
# ---------------------------------------------------------------------------


class TestRouterIpUnsupportedOS:
    @patch("nadzoring.network_base.router_ip.system", return_value="Darwin")
    def test_macos_returns_none(self, mock_sys):
        assert router_ip() is None

    @patch("nadzoring.network_base.router_ip.system", return_value="FreeBSD")
    def test_freebsd_returns_none(self, mock_sys):
        assert router_ip() is None

    @patch("nadzoring.network_base.router_ip.system", return_value="")
    def test_empty_os_returns_none(self, mock_sys):
        assert router_ip() is None
