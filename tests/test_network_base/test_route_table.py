"""Tests for nadzoring.network_base.route_table."""

from unittest.mock import patch

from nadzoring.network_base.route_table import (
    RouteEntry,
    _parse_linux_ip_route,
    _parse_windows_route_print,
    get_route_table,
)

# ---------------------------------------------------------------------------
# _parse_linux_ip_route
# ---------------------------------------------------------------------------


class TestParseLinuxIpRoute:
    def test_default_route_parsed(self):
        raw = "default via 192.168.1.1 dev eth0 proto dhcp metric 100\n"
        entries = _parse_linux_ip_route(raw)
        assert len(entries) == 1
        assert entries[0].destination == "default"
        assert entries[0].gateway == "192.168.1.1"
        assert entries[0].interface == "eth0"
        assert entries[0].metric == "100"

    def test_subnet_route(self):
        raw = "192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100\n"
        entries = _parse_linux_ip_route(raw)
        assert entries[0].destination == "192.168.1.0/24"
        assert entries[0].gateway == "0.0.0.0"  # default when no "via"

    def test_multiple_routes(self):
        raw = "default via 10.0.0.1 dev eth0\n10.0.0.0/8 dev eth0\n"
        entries = _parse_linux_ip_route(raw)
        assert len(entries) == 2

    def test_empty_input(self):
        assert _parse_linux_ip_route("") == []

    def test_route_without_metric(self):
        raw = "default via 10.0.0.1 dev eth0\n"
        entries = _parse_linux_ip_route(raw)
        assert entries[0].metric is None

    def test_route_without_interface(self):
        raw = "169.254.0.0/16 dev eth0 scope link\n"
        # Has dev — interface should be captured
        entries = _parse_linux_ip_route(raw)
        assert entries[0].interface == "eth0"

    def test_netmask_is_none_for_linux(self):
        # Linux ip route doesn't have a separate netmask field
        raw = "default via 10.0.0.1 dev eth0\n"
        entries = _parse_linux_ip_route(raw)
        assert entries[0].netmask is None

    def test_flags_is_none_for_linux(self):
        raw = "default via 10.0.0.1 dev eth0\n"
        entries = _parse_linux_ip_route(raw)
        assert entries[0].flags is None

    def test_blank_lines_skipped(self):
        raw = "\ndefault via 10.0.0.1 dev eth0\n\n"
        entries = _parse_linux_ip_route(raw)
        assert len(entries) == 1

    def test_return_type_is_list_of_route_entry(self):
        raw = "default via 10.0.0.1 dev eth0\n"
        entries = _parse_linux_ip_route(raw)
        assert all(isinstance(e, RouteEntry) for e in entries)


# ---------------------------------------------------------------------------
# _parse_windows_route_print
# ---------------------------------------------------------------------------

WINDOWS_ROUTE_SAMPLE = """\
IPv4 Route Table
===========================================================================
Active Routes:
Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0      192.168.1.1   192.168.1.100      25
        127.0.0.0        255.0.0.0        127.0.0.1       127.0.0.1     331
      192.168.1.0    255.255.255.0      192.168.1.100   192.168.1.100    281
Persistent Routes:
  None
"""


class TestParseWindowsRoutePrint:
    def test_default_route_parsed(self):
        entries = _parse_windows_route_print(WINDOWS_ROUTE_SAMPLE)
        default = next((e for e in entries if e.destination == "0.0.0.0"), None)
        assert default is not None
        assert default.gateway == "192.168.1.1"

    def test_loopback_route_parsed(self):
        entries = _parse_windows_route_print(WINDOWS_ROUTE_SAMPLE)
        lo = next((e for e in entries if e.destination == "127.0.0.0"), None)
        assert lo is not None

    def test_three_active_routes_parsed(self):
        entries = _parse_windows_route_print(WINDOWS_ROUTE_SAMPLE)
        assert len(entries) == 3

    def test_persistent_routes_section_excluded(self):
        raw = WINDOWS_ROUTE_SAMPLE + "  0.0.0.0   0.0.0.0   1.2.3.4   5.6.7.8   10\n"
        entries = _parse_windows_route_print(raw)
        # The line after "Persistent Routes:" should not be included
        assert len(entries) == 3

    def test_empty_input(self):
        assert _parse_windows_route_print("") == []

    def test_netmask_captured(self):
        entries = _parse_windows_route_print(WINDOWS_ROUTE_SAMPLE)
        default = next(e for e in entries if e.destination == "0.0.0.0")
        assert default.netmask == "0.0.0.0"

    def test_metric_captured(self):
        entries = _parse_windows_route_print(WINDOWS_ROUTE_SAMPLE)
        default = next(e for e in entries if e.destination == "0.0.0.0")
        assert default.metric == "25"

    def test_header_line_skipped(self):
        entries = _parse_windows_route_print(WINDOWS_ROUTE_SAMPLE)
        destinations = [e.destination for e in entries]
        assert "Network" not in destinations


# ---------------------------------------------------------------------------
# get_route_table — dispatcher
# ---------------------------------------------------------------------------


class TestGetRouteTable:
    @patch("nadzoring.network_base.route_table.system", return_value="Linux")
    @patch("nadzoring.network_base.route_table._get_linux_routes", return_value=[])
    def test_linux_calls_linux_impl(self, mock_linux, mock_sys):
        get_route_table()
        mock_linux.assert_called_once()

    @patch("nadzoring.network_base.route_table.system", return_value="Windows")
    @patch("nadzoring.network_base.route_table._get_windows_routes", return_value=[])
    def test_windows_calls_windows_impl(self, mock_win, mock_sys):
        get_route_table()
        mock_win.assert_called_once()

    @patch("nadzoring.network_base.route_table.system", return_value="Darwin")
    def test_unsupported_os_returns_empty_list(self, mock_sys):
        assert get_route_table() == []

    @patch("nadzoring.network_base.route_table.system", return_value="Linux")
    @patch("nadzoring.network_base.route_table.check_output", side_effect=FileNotFoundError)
    def test_linux_command_not_found_returns_empty(self, mock_co, mock_sys):
        result = get_route_table()
        assert result == []

    @patch("nadzoring.network_base.route_table.system", return_value="Linux")
    @patch("nadzoring.network_base.route_table._get_linux_routes")
    def test_returns_list_of_route_entries(self, mock_linux, mock_sys):
        mock_linux.return_value = [
            RouteEntry(
                destination="default",
                gateway="10.0.0.1",
                netmask=None,
                interface="eth0",
                metric="100",
                flags=None,
            )
        ]
        result = get_route_table()
        assert isinstance(result, list)
        assert isinstance(result[0], RouteEntry)
