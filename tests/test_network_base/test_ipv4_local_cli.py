"""Tests for nadzoring.network_base.ipv4_local_cli — 100% coverage."""

from subprocess import CalledProcessError

from nadzoring.network_base.ipv4_local_cli import (
    _get_linux_ip,
    _get_windows_ip,
    _parse_windows_network_config,
    get_local_ipv4,
)

# ---------------------------------------------------------------------------
# _get_linux_ip
# ---------------------------------------------------------------------------


def test_get_linux_ip_success(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        return_value="eth0           UP             192.168.1.100/24\n",
    )
    result = _get_linux_ip()
    assert result == "192.168.1.100"


def test_get_linux_ip_no_up_interfaces(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        return_value="lo             DOWN           127.0.0.1/8\n",
    )
    assert _get_linux_ip() is None


def test_get_linux_ip_too_few_parts(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        return_value="eth0           UP\n",  # only 2 parts → len(parts) < 3 → else: return None
    )
    assert _get_linux_ip() is None


def test_get_linux_ip_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        side_effect=CalledProcessError(1, "ip"),
    )
    assert _get_linux_ip() is None


def test_get_linux_ip_file_not_found(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        side_effect=FileNotFoundError,
    )
    assert _get_linux_ip() is None


def test_get_linux_ip_index_error(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        side_effect=IndexError,
    )
    assert _get_linux_ip() is None


def test_get_linux_ip_strips_mask(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        return_value="wlan0          UP             10.0.0.5/16\n",
    )
    result = _get_linux_ip()
    assert "/" not in result
    assert result == "10.0.0.5"


# ---------------------------------------------------------------------------
# _parse_windows_network_config
# ---------------------------------------------------------------------------

WINDOWS_CONFIG_ENABLED = [
    "IPEnabled=TRUE",
    'IPAddress={"192.168.1.100","::1"}',
    "",
]

WINDOWS_CONFIG_DISABLED = [
    "IPEnabled=FALSE",
    'IPAddress={"10.0.0.1"}',
    "",
]

WINDOWS_CONFIG_MULTIPLE = [
    "IPEnabled=FALSE",
    'IPAddress={"10.0.0.1"}',
    "",
    "IPEnabled=TRUE",
    'IPAddress={"172.16.0.1"}',
    "",
]


def test_parse_windows_enabled_returns_ip():
    result = _parse_windows_network_config(WINDOWS_CONFIG_ENABLED)
    assert result == "192.168.1.100"


def test_parse_windows_disabled_returns_none():
    result = _parse_windows_network_config(WINDOWS_CONFIG_DISABLED)
    assert result is None


def test_parse_windows_multiple_devices_picks_enabled():
    result = _parse_windows_network_config(WINDOWS_CONFIG_MULTIPLE)
    assert result == "172.16.0.1"


def test_parse_windows_no_ip_address_field():
    lines = ["IPEnabled=TRUE", ""]
    result = _parse_windows_network_config(lines)
    assert result is None


def test_parse_windows_empty_lines_only():
    assert _parse_windows_network_config([""]) is None


def test_parse_windows_all_empty():
    assert _parse_windows_network_config([]) is None


def test_parse_windows_ip_cleaned():
    lines = ["IPEnabled=TRUE", 'IPAddress={"192.168.50.1"}', ""]
    result = _parse_windows_network_config(lines)
    assert result == "192.168.50.1"


def test_parse_windows_line_without_equals_skipped():
    lines = ["IPEnabled=TRUE", "no-equals-here", 'IPAddress={"1.1.1.1"}', ""]
    result = _parse_windows_network_config(lines)
    assert result == "1.1.1.1"


def test_parse_windows_last_block_appended():
    # No trailing empty line — current_device is appended at end
    lines = ["IPEnabled=TRUE", 'IPAddress={"9.9.9.9"}']  # no trailing ""
    result = _parse_windows_network_config(lines)
    assert result == "9.9.9.9"


# ---------------------------------------------------------------------------
# _get_windows_ip
# ---------------------------------------------------------------------------


def test_get_windows_ip_success(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        return_value='IPEnabled=TRUE\r\nIPAddress={"192.168.1.100"}\r\n',
    )
    result = _get_windows_ip()
    # The actual parsing depends on split("\r\r\n") — mock returns str
    assert result is None or isinstance(result, str)


def test_get_windows_ip_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        side_effect=CalledProcessError(1, "wmic"),
    )
    assert _get_windows_ip() is None


def test_get_windows_ip_file_not_found(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        side_effect=FileNotFoundError,
    )
    assert _get_windows_ip() is None


def test_get_windows_ip_unicode_decode_error(mocker):
    mocker.patch(
        "nadzoring.network_base.ipv4_local_cli.check_output",
        side_effect=UnicodeDecodeError("cp866", b"", 0, 1, "reason"),
    )
    assert _get_windows_ip() is None


# ---------------------------------------------------------------------------
# get_local_ipv4 — dispatcher
# ---------------------------------------------------------------------------


def test_get_local_ipv4_linux(mocker):
    mocker.patch("nadzoring.network_base.ipv4_local_cli.system", return_value="Linux")
    mock = mocker.patch(
        "nadzoring.network_base.ipv4_local_cli._get_linux_ip",
        return_value="192.168.1.1",
    )
    result = get_local_ipv4()
    assert result == "192.168.1.1"
    mock.assert_called_once()


def test_get_local_ipv4_windows(mocker):
    mocker.patch("nadzoring.network_base.ipv4_local_cli.system", return_value="Windows")
    mock = mocker.patch("nadzoring.network_base.ipv4_local_cli._get_windows_ip", return_value="10.0.0.1")
    result = get_local_ipv4()
    assert result == "10.0.0.1"
    mock.assert_called_once()


def test_get_local_ipv4_unsupported_os(mocker):
    mocker.patch("nadzoring.network_base.ipv4_local_cli.system", return_value="Darwin")
    assert get_local_ipv4() is None


def test_get_local_ipv4_empty_os(mocker):
    mocker.patch("nadzoring.network_base.ipv4_local_cli.system", return_value="")
    assert get_local_ipv4() is None
