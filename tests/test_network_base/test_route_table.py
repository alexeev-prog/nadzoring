# tests/test_network_base/test_route_table.py
"""Tests for nadzoring.network_base.route_table — 100% coverage."""

from subprocess import CalledProcessError

from nadzoring.network_base.route_table import (
    RouteEntry,
    _get_linux_routes,
    _get_windows_routes,
    _parse_linux_ip_route,
    _parse_windows_route_print,
    get_route_table,
)


def test_linux_empty_input():
    assert _parse_linux_ip_route("") == []


def test_linux_default_route():
    raw = "default via 192.168.1.1 dev eth0 proto dhcp metric 100\n"
    entries = _parse_linux_ip_route(raw)
    assert len(entries) == 1
    assert entries[0].destination == "default"
    assert entries[0].gateway == "192.168.1.1"
    assert entries[0].interface == "eth0"
    assert entries[0].metric == "100"


def test_linux_subnet_no_via():
    raw = "192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100\n"
    entries = _parse_linux_ip_route(raw)
    assert entries[0].destination == "192.168.1.0/24"
    assert entries[0].gateway == "0.0.0.0"


def test_linux_multiple_routes():
    raw = "default via 10.0.0.1 dev eth0\n10.0.0.0/8 dev eth0\n"
    assert len(_parse_linux_ip_route(raw)) == 2


def test_linux_route_without_metric():
    raw = "default via 10.0.0.1 dev eth0\n"
    assert _parse_linux_ip_route(raw)[0].metric is None


def test_linux_netmask_is_none():
    raw = "default via 10.0.0.1 dev eth0\n"
    assert _parse_linux_ip_route(raw)[0].netmask is None


def test_linux_flags_is_none():
    raw = "default via 10.0.0.1 dev eth0\n"
    assert _parse_linux_ip_route(raw)[0].flags is None


def test_linux_blank_lines_skipped():
    raw = "\ndefault via 10.0.0.1 dev eth0\n\n"
    assert len(_parse_linux_ip_route(raw)) == 1


def test_linux_returns_route_entry_objects():
    raw = "default via 10.0.0.1 dev eth0\n"
    assert all(isinstance(e, RouteEntry) for e in _parse_linux_ip_route(raw))


def test_linux_no_via_no_dev_defaults():
    raw = "169.254.0.0/16\n"
    entries = _parse_linux_ip_route(raw)
    assert entries[0].gateway == "0.0.0.0"
    assert entries[0].interface is None
    assert entries[0].metric is None


def test_linux_route_with_via_after_dev():
    raw = "default dev eth0 via 192.168.1.1 metric 100\n"
    entries = _parse_linux_ip_route(raw)
    assert entries[0].gateway == "192.168.1.1"
    assert entries[0].interface == "eth0"


def test_linux_route_with_extra_fields():
    raw = "default via 10.0.0.1 dev eth0 proto static metric 100 scope global\n"
    entries = _parse_linux_ip_route(raw)
    assert entries[0].destination == "default"
    assert entries[0].gateway == "10.0.0.1"
    assert entries[0].interface == "eth0"
    assert entries[0].metric == "100"


WINDOWS_SAMPLE = (
    "IPv4 Route Table\n"
    "===========================================================================\n"
    "Active Routes:\n"
    "Network Destination        Netmask          Gateway       Interface  Metric\n"
    "          0.0.0.0          0.0.0.0      192.168.1.1   192.168.1.100      25\n"
    "        127.0.0.0        255.0.0.0        127.0.0.1       127.0.0.1     331\n"
    "      192.168.1.0    255.255.255.0      192.168.1.100   192.168.1.100    281\n"
    "Persistent Routes:\n"
    "  None\n"
)


def test_windows_empty_input():
    assert _parse_windows_route_print("") == []


def test_windows_default_route_parsed():
    entries = _parse_windows_route_print(WINDOWS_SAMPLE)
    default = next(e for e in entries if e.destination == "0.0.0.0")
    assert default.gateway == "192.168.1.1"


def test_windows_loopback_parsed():
    entries = _parse_windows_route_print(WINDOWS_SAMPLE)
    assert any(e.destination == "127.0.0.0" for e in entries)


def test_windows_three_routes():
    assert len(_parse_windows_route_print(WINDOWS_SAMPLE)) == 3


def test_windows_netmask_captured():
    entries = _parse_windows_route_print(WINDOWS_SAMPLE)
    default = next(e for e in entries if e.destination == "0.0.0.0")
    assert default.netmask == "0.0.0.0"


def test_windows_metric_captured():
    entries = _parse_windows_route_print(WINDOWS_SAMPLE)
    default = next(e for e in entries if e.destination == "0.0.0.0")
    assert default.metric == "25"


def test_windows_persistent_routes_excluded():
    raw = WINDOWS_SAMPLE + "  0.0.0.0   0.0.0.0   5.6.7.8   1.2.3.4   1\n"
    assert len(_parse_windows_route_print(raw)) == 3


def test_windows_ipv6_section_excluded():
    raw = WINDOWS_SAMPLE.replace("Persistent Routes:", "IPv6 Route Table\nActive Routes:\n")
    entries = _parse_windows_route_print(raw)
    assert len(entries) == 3


def test_windows_header_line_skipped():
    entries = _parse_windows_route_print(WINDOWS_SAMPLE)
    destinations = [e.destination for e in entries]
    assert "Network" not in destinations


def test_windows_equals_line_skipped():
    entries = _parse_windows_route_print(WINDOWS_SAMPLE)
    assert all("=" not in e.destination for e in entries)


def test_windows_returns_route_entry_objects():
    entries = _parse_windows_route_print(WINDOWS_SAMPLE)
    assert all(isinstance(e, RouteEntry) for e in entries)


def test_windows_line_too_short_skipped():
    raw = "Active Routes:\n  0.0.0.0  0.0.0.0\n"
    assert _parse_windows_route_print(raw) == []


def test_windows_route_with_interface_name():
    raw = (
        "Active Routes:\n"
        "Network Destination        Netmask          Gateway       Interface  Metric\n"
        "          0.0.0.0          0.0.0.0      192.168.1.1   192.168.1.100      25\n"
    )
    entries = _parse_windows_route_print(raw)
    assert entries[0].interface == "192.168.1.100"


def test_get_linux_routes_success(mocker):
    mock_output = b"default via 10.0.0.1 dev eth0\n"
    mocker.patch("nadzoring.network_base.route_table.check_output", return_value=mock_output)
    result = _get_linux_routes()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].destination == "default"


def test_get_linux_routes_empty_output(mocker):
    mock_output = b""
    mocker.patch("nadzoring.network_base.route_table.check_output", return_value=mock_output)
    result = _get_linux_routes()
    assert result == []


def test_get_linux_routes_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.route_table.check_output",
        side_effect=CalledProcessError(1, "ip route"),
    )
    assert _get_linux_routes() == []


def test_get_linux_routes_file_not_found(mocker):
    mocker.patch(
        "nadzoring.network_base.route_table.check_output",
        side_effect=FileNotFoundError,
    )
    assert _get_linux_routes() == []


def test_get_linux_routes_with_multiple_entries(mocker):
    mock_output = b"default via 10.0.0.1 dev eth0\n10.0.0.0/8 dev eth0\n"
    mocker.patch("nadzoring.network_base.route_table.check_output", return_value=mock_output)
    result = _get_linux_routes()
    assert len(result) == 2


def test_get_linux_routes_decode_error(mocker):
    """Test that decode errors are handled gracefully."""
    mock_output = b"\xff\xff\xff"
    mocker.patch("nadzoring.network_base.route_table.check_output", return_value=mock_output)
    # This should not raise an exception
    result = _get_linux_routes()
    assert isinstance(result, list)


def test_get_windows_routes_success(mocker):
    mocker.patch(
        "nadzoring.network_base.route_table.check_output",
        return_value=WINDOWS_SAMPLE.encode("cp866"),
    )
    result = _get_windows_routes()
    assert isinstance(result, list)
    assert len(result) == 3


def test_get_windows_routes_empty_output(mocker):
    mocker.patch(
        "nadzoring.network_base.route_table.check_output",
        return_value=b"",
    )
    result = _get_windows_routes()
    assert result == []


def test_get_windows_routes_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.route_table.check_output",
        side_effect=CalledProcessError(1, "route"),
    )
    assert _get_windows_routes() == []


def test_get_windows_routes_file_not_found(mocker):
    mocker.patch(
        "nadzoring.network_base.route_table.check_output",
        side_effect=FileNotFoundError,
    )
    assert _get_windows_routes() == []


def test_get_windows_routes_decode_error(mocker):
    """Test that decode errors with cp866 are handled."""
    mocker.patch(
        "nadzoring.network_base.route_table.check_output",
        return_value=b"\xff\xff\xff",
    )
    result = _get_windows_routes()
    assert isinstance(result, list)


def test_get_route_table_linux(mocker):
    mocker.patch("nadzoring.network_base.route_table.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.route_table._get_linux_routes", return_value=[])
    get_route_table()
    mock.assert_called_once()


def test_get_route_table_windows(mocker):
    mocker.patch("nadzoring.network_base.route_table.system", return_value="Windows")
    mock = mocker.patch("nadzoring.network_base.route_table._get_windows_routes", return_value=[])
    get_route_table()
    mock.assert_called_once()


def test_get_route_table_unsupported_os(mocker):
    mocker.patch("nadzoring.network_base.route_table.system", return_value="Darwin")
    assert get_route_table() == []


def test_get_route_table_returns_list(mocker):
    mocker.patch("nadzoring.network_base.route_table.system", return_value="Linux")
    mocker.patch(
        "nadzoring.network_base.route_table._get_linux_routes",
        return_value=[RouteEntry("default", "10.0.0.1", None, "eth0", "100", None)],
    )
    result = get_route_table()
    assert isinstance(result, list)
    assert isinstance(result[0], RouteEntry)


def test_route_entry_dataclass():
    entry = RouteEntry(
        destination="0.0.0.0",
        gateway="192.168.1.1",
        netmask="0.0.0.0",
        interface="eth0",
        metric="100",
        flags="UG",
    )
    assert entry.destination == "0.0.0.0"
    assert entry.gateway == "192.168.1.1"
    assert entry.netmask == "0.0.0.0"
    assert entry.interface == "eth0"
    assert entry.metric == "100"
    assert entry.flags == "UG"
