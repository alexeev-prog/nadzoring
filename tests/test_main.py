import shlex
from socket import gaierror
from unittest.mock import MagicMock, patch

from nadzoring.network_base.router_ip import (
    check_ipv4,
    check_ipv6,
    get_ip_from_host,
    router_ip,
)
from nadzoring.network_base.service_on_port import get_service_on_port


class TestGetServiceOnPort:
    """Tests for service_on_port.get_service_on_port function."""

    def test_known_port_returns_service_name(self):
        """Test that known port returns correct service name."""
        assert get_service_on_port(80) == "http"
        assert get_service_on_port(22) == "ssh"
        assert get_service_on_port(443) == "https"
        assert get_service_on_port(53) == "domain"

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_unknown_port_returns_unknown(self, mock_getservbyport):
        """Test that unknown port returns 'Unknown'."""
        mock_getservbyport.side_effect = OSError("Port not found")
        assert get_service_on_port(9999) == "Unknown"
        assert get_service_on_port(0) == "Unknown"
        assert get_service_on_port(65535) == "Unknown"
        assert mock_getservbyport.call_count == 3

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_getservbyport_raises_exception_returns_unknown(self, mock_getservbyport):
        """Test that when getservbyport raises exception, function returns 'Unknown'."""
        mock_getservbyport.side_effect = OSError("Port not found")
        assert get_service_on_port(12345) == "Unknown"
        mock_getservbyport.assert_called_once_with(12345)

    @patch("nadzoring.network_base.service_on_port.getservbyport")
    def test_getservbyport_returns_service_name(self, mock_getservbyport):
        """Test that getservbyport returns correct service name."""
        mock_getservbyport.return_value = "smtp"
        assert get_service_on_port(25) == "smtp"
        mock_getservbyport.assert_called_once_with(25)


class TestGetIpFromHost:
    """Tests for router_ip.get_ip_from_host function."""

    @patch("nadzoring.network_base.router_ip.gethostbyname")
    def test_valid_hostname_returns_ip(self, mock_gethostbyname):
        """Test that valid hostname returns IP address."""
        mock_gethostbyname.return_value = "93.184.216.34"
        result = get_ip_from_host("example.com")
        assert result == "93.184.216.34"
        mock_gethostbyname.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.router_ip.gethostbyname")
    def test_gethostbyname_raises_exception_returns_hostname(self, mock_gethostbyname):
        """Test that when gethostbyname raises exception, function returns hostname."""
        mock_gethostbyname.side_effect = gaierror("Name or service not known")
        result = get_ip_from_host("invalid.hostname.local")
        assert result == "invalid.hostname.local"
        mock_gethostbyname.assert_called_once_with("invalid.hostname.local")

    @patch("nadzoring.network_base.router_ip.gethostbyname")
    def test_hostname_with_ip_format_returns_same_value(self, mock_gethostbyname):
        """Test that passing IP-like string still goes through gethostbyname."""
        mock_gethostbyname.return_value = "192.168.1.1"
        result = get_ip_from_host("192.168.1.1")
        assert result == "192.168.1.1"
        mock_gethostbyname.assert_called_once_with("192.168.1.1")


class TestCheckIpv4:
    """Tests for router_ip.check_ipv4 function."""

    def test_valid_ipv4_returns_same_ip(self):
        """Test that valid IPv4 address returns same address."""
        result = check_ipv4("192.168.1.1")
        assert result == "192.168.1.1"

    def test_valid_ipv4_with_leading_zeros_returns_normalized_ip(self):
        """Test that IPv4 with leading zeros is normalized by IPv4Address."""
        result = check_ipv4("192.168.001.001")
        assert result == "192.168.1.1"

    def test_valid_ipv4_special_addresses(self):
        """Test that special IPv4 addresses are considered valid."""
        assert check_ipv4("0.0.0.0") == "0.0.0.0"
        assert check_ipv4("255.255.255.255") == "255.255.255.255"
        assert check_ipv4("127.0.0.1") == "127.0.0.1"

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_invalid_ipv4_calls_get_ip_from_host(self, mock_get_ip_from_host):
        """Test that invalid IPv4 string calls get_ip_from_host."""
        mock_get_ip_from_host.return_value = "93.184.216.34"
        result = check_ipv4("example.com")
        assert result == "93.184.216.34"
        mock_get_ip_from_host.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_ipv4_with_too_many_octets_calls_get_ip_from_host(
        self, mock_get_ip_from_host
    ):
        """Test that string with too many octets is invalid IPv4."""
        mock_get_ip_from_host.return_value = "192.168.1.1.5"
        result = check_ipv4("192.168.1.1.5")
        assert result == "192.168.1.1.5"
        mock_get_ip_from_host.assert_called_once_with("192.168.1.1.5")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_ipv4_with_octet_out_of_range_calls_get_ip_from_host(
        self, mock_get_ip_from_host
    ):
        """Test that octet value >255 makes IPv4 invalid."""
        mock_get_ip_from_host.return_value = "256.168.1.1"
        result = check_ipv4("256.168.1.1")
        assert result == "256.168.1.1"
        mock_get_ip_from_host.assert_called_once_with("256.168.1.1")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_empty_string_calls_get_ip_from_host(self, mock_get_ip_from_host):
        """Test that empty string is invalid IPv4."""
        mock_get_ip_from_host.return_value = ""
        result = check_ipv4("")
        assert result == ""
        mock_get_ip_from_host.assert_called_once_with("")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_none_string_calls_get_ip_from_host(self, mock_get_ip_from_host):
        """Test that 'None' string is invalid IPv4."""
        mock_get_ip_from_host.return_value = "None"
        result = check_ipv4("None")
        assert result == "None"
        mock_get_ip_from_host.assert_called_once_with("None")


class TestCheckIpv6:
    """Tests for router_ip.check_ipv6 function."""

    def test_valid_ipv6_returns_same_ip(self):
        """Test that valid IPv6 address returns same address."""
        result = check_ipv6("2001:db8::1")
        assert result == "2001:db8::1"

    def test_valid_ipv6_full_format_returns_same_format(self):
        """Test that full format IPv6 is returned as-is (no automatic compression)."""
        result = check_ipv6("2001:0db8:0000:0000:0000:0000:0000:0001")
        assert result == "2001:0db8:0000:0000:0000:0000:0000:0001"

    def test_valid_ipv6_loopback_returns_same_ip(self):
        """Test that IPv6 loopback is valid."""
        result = check_ipv6("::1")
        assert result == "::1"

    def test_valid_ipv6_unspecified_returns_same_ip(self):
        """Test that IPv6 unspecified address is valid."""
        result = check_ipv6("::")
        assert result == "::"

    def test_valid_ipv6_ipv4_compatible_returns_same_format(self):
        """Test that IPv4-compatible IPv6 address is valid."""
        result = check_ipv6("::192.168.1.1")
        assert result == "::192.168.1.1"

    def test_valid_ipv6_mapped_ipv4_returns_same_format(self):
        """Test that IPv4-mapped IPv6 address is valid."""
        result = check_ipv6("::ffff:192.168.1.1")
        assert result == "::ffff:192.168.1.1"

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_invalid_ipv6_calls_get_ip_from_host(self, mock_get_ip_from_host):
        """Test that invalid IPv6 string calls get_ip_from_host."""
        mock_get_ip_from_host.return_value = "2001:db8::1"
        result = check_ipv6("example.com")
        assert result == "2001:db8::1"
        mock_get_ip_from_host.assert_called_once_with("example.com")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_ipv6_with_too_many_blocks_calls_get_ip_from_host(
        self, mock_get_ip_from_host
    ):
        """Test that string with too many blocks is invalid IPv6."""
        mock_get_ip_from_host.return_value = "2001:db8::1:2:3:4:5:6"
        result = check_ipv6("2001:db8::1:2:3:4:5:6")
        assert result == "2001:db8::1:2:3:4:5:6"
        mock_get_ip_from_host.assert_called_once_with("2001:db8::1:2:3:4:5:6")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_ipv6_with_invalid_hex_calls_get_ip_from_host(self, mock_get_ip_from_host):
        """Test that invalid hex digits make IPv6 invalid."""
        mock_get_ip_from_host.return_value = "2001:dbg::1"
        result = check_ipv6("2001:dbg::1")
        assert result == "2001:dbg::1"
        mock_get_ip_from_host.assert_called_once_with("2001:dbg::1")

    @patch("nadzoring.network_base.router_ip.get_ip_from_host")
    def test_ipv4_string_calls_get_ip_from_host(self, mock_get_ip_from_host):
        """Test that IPv4 string is invalid IPv6."""
        mock_get_ip_from_host.return_value = "192.168.1.1"
        result = check_ipv6("192.168.1.1")
        assert result == "192.168.1.1"
        mock_get_ip_from_host.assert_called_once_with("192.168.1.1")


class TestRouterIp:
    """Tests for router_ip.router_ip function on Linux."""

    @patch("nadzoring.network_base.router_ip.system")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv4")
    def test_linux_router_ipv4_success(
        self, mock_check_ipv4, mock_check_output, mock_system
    ):
        """Test successful IPv4 router IP retrieval on Linux."""
        mock_system.return_value = "Linux"

        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = "default        192.168.1.1     0.0.0.0         UG    100    0        0 eth0\n"
        mock_check_output.return_value = mock_bytes

        mock_check_ipv4.return_value = "192.168.1.1"

        result = router_ip(ipv6=False)

        assert result == "192.168.1.1"
        mock_check_output.assert_called_once_with(shlex.split("route -n"))
        mock_check_ipv4.assert_called_once_with("192.168.1.1")

    @patch("nadzoring.network_base.router_ip.system")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv6")
    def test_linux_router_ipv6_success(
        self, mock_check_ipv6, mock_check_output, mock_system
    ):
        """Test successful IPv6 router IP retrieval on Linux."""
        mock_system.return_value = "Linux"

        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = "default        2001:db8::1     ::             UG    100    0        0 eth0\n"
        mock_check_output.return_value = mock_bytes

        mock_check_ipv6.return_value = "2001:db8::1"

        result = router_ip(ipv6=True)

        assert result == "2001:db8::1"
        mock_check_output.assert_called_once_with(shlex.split("route -n"))
        mock_check_ipv6.assert_called_once_with("2001:db8::1")

    @patch("nadzoring.network_base.router_ip.system")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv4")
    def test_linux_router_ip_with_domain_name_gateway(
        self, mock_check_ipv4, mock_check_output, mock_system
    ):
        """Test Linux router IP when gateway is a hostname."""
        mock_system.return_value = "Linux"

        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = "default        gateway.local    0.0.0.0         UG    100    0        0 eth0\n"
        mock_check_output.return_value = mock_bytes

        mock_check_ipv4.return_value = "192.168.1.1"

        result = router_ip(ipv6=False)

        assert result == "192.168.1.1"
        mock_check_ipv4.assert_called_once_with("gateway.local")

    @patch("nadzoring.network_base.router_ip.system")
    @patch("nadzoring.network_base.router_ip.check_output")
    @patch("nadzoring.network_base.router_ip.check_ipv4")
    def test_linux_multiple_default_routes_takes_first(
        self, mock_check_ipv4, mock_check_output, mock_system
    ):
        """Test that with multiple default routes, the first one is taken."""
        mock_system.return_value = "Linux"

        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = (
            "default        192.168.1.1     0.0.0.0         UG    100    0        0 eth0\n"
            "default        10.0.0.1        0.0.0.0         UG    101    0        0 eth1\n"
        )
        mock_check_output.return_value = mock_bytes

        mock_check_ipv4.return_value = "192.168.1.1"

        result = router_ip()

        assert result == "192.168.1.1"
        mock_check_ipv4.assert_called_once_with("192.168.1.1")

    @patch("nadzoring.network_base.router_ip.system")
    @patch("nadzoring.network_base.router_ip.check_output")
    def test_linux_route_output_format_variation(self, mock_check_output, mock_system):
        """Test that function handles different whitespace in route output."""
        mock_system.return_value = "Linux"

        mock_bytes = MagicMock()
        mock_bytes.decode.return_value = (
            "default   192.168.1.1   0.0.0.0   UG   100   0   0   eth0\n"
        )
        mock_check_output.return_value = mock_bytes

        with patch("nadzoring.network_base.router_ip.check_ipv4") as mock_check_ipv4:
            mock_check_ipv4.return_value = "192.168.1.1"
            result = router_ip()
            assert result == "192.168.1.1"
            mock_check_ipv4.assert_called_once_with("192.168.1.1")
