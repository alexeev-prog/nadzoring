"""Tests for nadzoring.network_base.network_params — 100% coverage."""

from subprocess import CalledProcessError

from nadzoring.network_base.network_params import (
    _create_empty_network_info,
    _extract_interface_details,
    _find_enabled_interface,
    _get_linux_gateway,
    _get_linux_interface_info,
    _get_linux_mac_address,
    _get_linux_network_info,
    _get_windows_network_info,
    _parse_windows_network_configs,
    network_param,
    public_ip,
)

# ---------------------------------------------------------------------------
# public_ip
# ---------------------------------------------------------------------------


def test_public_ip_success(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.text = "1.2.3.4"
    mocker.patch("nadzoring.network_base.network_params.requests.get", return_value=mock_resp)
    assert public_ip() == "1.2.3.4"


def test_public_ip_exception_returns_loopback(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.requests.get",
        side_effect=Exception("timeout"),
    )
    assert public_ip() == "127.0.0.1"


# ---------------------------------------------------------------------------
# _get_linux_interface_info
# ---------------------------------------------------------------------------


def test_get_linux_interface_info_success(mocker):
    mock_result = mocker.MagicMock()
    mock_result.stdout = "eth0           UP             192.168.1.100/24 fe80::1/64\n"
    mocker.patch("nadzoring.network_base.network_params.run", return_value=mock_result)
    result = _get_linux_interface_info()
    assert result["name"] == "eth0"
    assert result["ipv4"] == "192.168.1.100"
    assert result["ipv6"] == "fe80::1"


def test_get_linux_interface_info_no_up_interfaces(mocker):
    mock_result = mocker.MagicMock()
    mock_result.stdout = "lo             DOWN           127.0.0.1/8\n"
    mocker.patch("nadzoring.network_base.network_params.run", return_value=mock_result)
    result = _get_linux_interface_info()
    assert result == {"name": None, "ipv4": None, "ipv6": None}


def test_get_linux_interface_info_no_ipv6(mocker):
    mock_result = mocker.MagicMock()
    mock_result.stdout = "eth0           UP             192.168.1.100/24\n"
    mocker.patch("nadzoring.network_base.network_params.run", return_value=mock_result)
    result = _get_linux_interface_info()
    assert result["name"] == "eth0"
    assert result["ipv4"] == "192.168.1.100"
    assert result["ipv6"] is None


def test_get_linux_interface_info_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.run",
        side_effect=CalledProcessError(1, "ip"),
    )
    result = _get_linux_interface_info()
    assert result == {"name": None, "ipv4": None, "ipv6": None}


def test_get_linux_interface_info_index_error(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.run",
        side_effect=IndexError,
    )
    result = _get_linux_interface_info()
    assert result == {"name": None, "ipv4": None, "ipv6": None}


def test_get_linux_interface_info_attribute_error(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.run",
        side_effect=AttributeError,
    )
    result = _get_linux_interface_info()
    assert result == {"name": None, "ipv4": None, "ipv6": None}


# ---------------------------------------------------------------------------
# _get_linux_gateway
# ---------------------------------------------------------------------------


def test_get_linux_gateway_success(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "default        192.168.1.1     0.0.0.0         UG    100    0        0 eth0\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    mocker.patch(
        "nadzoring.network_base.network_params.gethostbyname",
        return_value="192.168.1.1",
    )
    result = _get_linux_gateway()
    assert result == "192.168.1.1"


def test_get_linux_gateway_no_ug_lines(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "Kernel IP routing table\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    assert _get_linux_gateway() is None


def test_get_linux_gateway_invalid_ip_format(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "default        not-an-ip     0.0.0.0         UG    100    0        0 eth0\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    result = _get_linux_gateway()
    assert result is None


def test_get_linux_gateway_gethostbyname_fails_returns_candidate(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "default        192.168.1.1     0.0.0.0         UG    100    0        0 eth0\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    mocker.patch(
        "nadzoring.network_base.network_params.gethostbyname",
        side_effect=Exception("resolution failed"),
    )
    result = _get_linux_gateway()
    assert result == "192.168.1.1"


def test_get_linux_gateway_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.check_output",
        side_effect=CalledProcessError(1, "route"),
    )
    assert _get_linux_gateway() is None


def test_get_linux_gateway_index_error(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.check_output",
        side_effect=IndexError,
    )
    assert _get_linux_gateway() is None


# ---------------------------------------------------------------------------
# _get_linux_mac_address
# ---------------------------------------------------------------------------


def test_get_linux_mac_address_none_interface():
    assert _get_linux_mac_address(None) is None


def test_get_linux_mac_address_ether_keyword(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "eth0  Link encap:Ethernet  ether aa:bb:cc:dd:ee:ff  txqueuelen\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    result = _get_linux_mac_address("eth0")
    assert result == "aa:bb:cc:dd:ee:ff"


def test_get_linux_mac_address_hwaddr_keyword(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "eth0  Link encap:Ethernet  HWaddr aa:bb:cc:dd:ee:ff\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    result = _get_linux_mac_address("eth0")
    assert result == "aa:bb:cc:dd:ee:ff"


def test_get_linux_mac_address_no_mac_lines(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "eth0  inet addr:192.168.1.1\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    result = _get_linux_mac_address("eth0")
    assert result is None


def test_get_linux_mac_address_called_process_error(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.check_output",
        side_effect=CalledProcessError(1, "ifconfig"),
    )
    assert _get_linux_mac_address("eth0") is None


def test_get_linux_mac_address_index_error(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.check_output",
        side_effect=IndexError,
    )
    assert _get_linux_mac_address("eth0") is None


def test_get_linux_mac_address_attribute_error(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params.check_output",
        side_effect=AttributeError,
    )
    assert _get_linux_mac_address("eth0") is None


def test_get_linux_mac_address_ether_at_end_of_parts(mocker):
    # ether is the last part → i+1 >= len(parts) → no return from loop → returns None
    mb = mocker.MagicMock()
    mb.decode.return_value = "only ether\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    result = _get_linux_mac_address("eth0")
    assert result is None


# ---------------------------------------------------------------------------
# _get_linux_network_info
# ---------------------------------------------------------------------------


def test_get_linux_network_info_returns_dict(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params._get_linux_interface_info",
        return_value={"name": "eth0", "ipv4": "192.168.1.100", "ipv6": "::1"},
    )
    mocker.patch(
        "nadzoring.network_base.network_params._get_linux_gateway",
        return_value="192.168.1.1",
    )
    mocker.patch(
        "nadzoring.network_base.network_params._get_linux_mac_address",
        return_value="aa:bb:cc:dd:ee:ff",
    )
    mocker.patch(
        "nadzoring.network_base.network_params.public_ip",
        return_value="5.6.7.8",
    )
    result = _get_linux_network_info()
    assert result["Default Interface"] == "eth0"
    assert result["IPv4 address"] == "192.168.1.100"
    assert result["IPv6 address"] == "::1"
    assert result["Router ip-address"] == "192.168.1.1"
    assert result["MAC-address"] == "aa:bb:cc:dd:ee:ff"
    assert result["Public IP address"] == "5.6.7.8"


def test_get_linux_network_info_calls_mac_with_name(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params._get_linux_interface_info",
        return_value={"name": "wlan0", "ipv4": None, "ipv6": None},
    )
    mocker.patch("nadzoring.network_base.network_params._get_linux_gateway", return_value=None)
    mock_mac = mocker.patch(
        "nadzoring.network_base.network_params._get_linux_mac_address",
        return_value=None,
    )
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")

    _get_linux_network_info()
    mock_mac.assert_called_once_with("wlan0")


# ---------------------------------------------------------------------------
# _parse_windows_network_configs
# ---------------------------------------------------------------------------

WMIC_OUTPUT = (
    "DefaultIPGateway={192.168.1.1}\r\r\n"
    'IPAddress={"192.168.1.100"}\r\r\n'
    "IPEnabled=TRUE\r\r\n"
    "MACAddress=AA:BB:CC:DD:EE:FF\r\r\n"
    "SettingID={guid-1234}\r\r\n"
    "\r\r\n"
    "DefaultIPGateway=\r\r\n"
    'IPAddress={"10.0.0.1"}\r\r\n'
    "IPEnabled=FALSE\r\r\n"
    "MACAddress=00:11:22:33:44:55\r\r\n"
    "SettingID={guid-5678}\r\r\n"
)


def test_parse_windows_network_configs_returns_list(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = WMIC_OUTPUT
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    result = _parse_windows_network_configs()
    assert isinstance(result, list)
    assert len(result) >= 1


def test_parse_windows_network_configs_blocks_joined(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "Key=Value\r\r\nKey2=Value2\r\r\n\r\r\n"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    result = _parse_windows_network_configs()
    assert len(result) == 1
    assert "~" in result[0]


def test_parse_windows_network_configs_trailing_block(mocker):
    # No trailing empty line → current_block appended at end
    mb = mocker.MagicMock()
    mb.decode.return_value = "Key=Value\r\r\nKey2=Value2"
    mocker.patch("nadzoring.network_base.network_params.check_output", return_value=mb)
    result = _parse_windows_network_configs()
    assert len(result) == 1


# ---------------------------------------------------------------------------
# _find_enabled_interface
# ---------------------------------------------------------------------------


def test_find_enabled_interface_found():
    blocks = [
        "IPEnabled=FALSE~SettingID=x",
        "IPEnabled=TRUE~SettingID=y~MACAddress=aa:bb",
    ]
    result = _find_enabled_interface(blocks)
    assert result is not None
    assert "IPEnabled=TRUE" in result


def test_find_enabled_interface_none_found():
    blocks = ["IPEnabled=FALSE~SettingID=x"]
    assert _find_enabled_interface(blocks) is None


def test_find_enabled_interface_empty_list():
    assert _find_enabled_interface([]) is None


# ---------------------------------------------------------------------------
# _extract_interface_details
# ---------------------------------------------------------------------------


def test_extract_interface_details_setting_id(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")
    parts = ["SettingID={guid}", "IPEnabled=TRUE"]
    result = _extract_interface_details(parts)
    assert result["Default Interface"] == "{guid}"


def test_extract_interface_details_gateway(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")
    parts = ['DefaultIPGateway={"192.168.1.1"}']
    result = _extract_interface_details(parts)
    assert result["Router ip-address"] == "192.168.1.1"


def test_extract_interface_details_mac(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")
    parts = ["MACAddress=AA:BB:CC:DD:EE:FF"]
    result = _extract_interface_details(parts)
    assert result["MAC-address"] == "AA:BB:CC:DD:EE:FF"


def test_extract_interface_details_ipaddress_single(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")
    parts = ['IPAddress={"192.168.1.100"}']
    result = _extract_interface_details(parts)
    assert result["IPv4 address"] == "192.168.1.100"
    assert result["IPv6 address"] is None


def test_extract_interface_details_ipaddress_both(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")
    parts = ['IPAddress={"192.168.1.100","::1"}']
    result = _extract_interface_details(parts)
    assert result["IPv4 address"] == "192.168.1.100"
    assert result["IPv6 address"] == "::1"


def test_extract_interface_details_empty_value_skipped(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")
    parts = ["SettingID="]
    result = _extract_interface_details(parts)
    assert result["Default Interface"] is None


def test_extract_interface_details_no_equals_skipped(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")
    parts = ["no-equals-here"]
    result = _extract_interface_details(parts)
    assert result["Default Interface"] is None


def test_extract_interface_details_empty_part_skipped(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="1.1.1.1")
    parts = ["", "SettingID=test"]
    result = _extract_interface_details(parts)
    assert result["Default Interface"] == "test"


def test_extract_interface_details_public_ip_set(mocker):
    mocker.patch("nadzoring.network_base.network_params.public_ip", return_value="5.5.5.5")
    result = _extract_interface_details([])
    assert result["Public IP address"] == "5.5.5.5"


# ---------------------------------------------------------------------------
# _create_empty_network_info
# ---------------------------------------------------------------------------


def test_create_empty_network_info_all_none():
    result = _create_empty_network_info()
    assert all(v is None for v in result.values())


def test_create_empty_network_info_keys():
    result = _create_empty_network_info()
    expected = {
        "Default Interface",
        "IPv4 address",
        "IPv6 address",
        "Router ip-address",
        "MAC-address",
        "Public IP address",
    }
    assert set(result.keys()) == expected


# ---------------------------------------------------------------------------
# _get_windows_network_info
# ---------------------------------------------------------------------------


def test_get_windows_network_info_enabled_interface(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params._parse_windows_network_configs",
        return_value=["IPEnabled=TRUE~SettingID=x~MACAddress=aa:bb"],
    )
    mocker.patch(
        "nadzoring.network_base.network_params._find_enabled_interface",
        return_value=["IPEnabled=TRUE", "SettingID=x"],
    )
    mocker.patch(
        "nadzoring.network_base.network_params._extract_interface_details",
        return_value={
            "Default Interface": "x",
            "IPv4 address": None,
            "IPv6 address": None,
            "Router ip-address": None,
            "MAC-address": None,
            "Public IP address": None,
        },
    )
    result = _get_windows_network_info()
    assert result["Default Interface"] == "x"


def test_get_windows_network_info_no_enabled_interface(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params._parse_windows_network_configs",
        return_value=["IPEnabled=FALSE~SettingID=x"],
    )
    mocker.patch(
        "nadzoring.network_base.network_params._find_enabled_interface",
        return_value=None,
    )
    result = _get_windows_network_info()
    assert all(v is None for v in result.values())


def test_get_windows_network_info_exception_returns_empty(mocker):
    mocker.patch(
        "nadzoring.network_base.network_params._parse_windows_network_configs",
        side_effect=Exception("wmic error"),
    )
    result = _get_windows_network_info()
    assert all(v is None for v in result.values())


# ---------------------------------------------------------------------------
# network_param — dispatcher
# ---------------------------------------------------------------------------


def test_network_param_linux(mocker):
    mocker.patch("nadzoring.network_base.network_params.system", return_value="Linux")
    mock = mocker.patch(
        "nadzoring.network_base.network_params._get_linux_network_info",
        return_value={"Default Interface": "eth0"},
    )
    result = network_param()
    assert result == {"Default Interface": "eth0"}
    mock.assert_called_once()


def test_network_param_windows(mocker):
    mocker.patch("nadzoring.network_base.network_params.system", return_value="Windows")
    mock = mocker.patch(
        "nadzoring.network_base.network_params._get_windows_network_info",
        return_value={"Default Interface": None},
    )
    result = network_param()
    assert result is not None
    mock.assert_called_once()


def test_network_param_unsupported_os(mocker):
    mocker.patch("nadzoring.network_base.network_params.system", return_value="Darwin")
    assert network_param() is None


def test_network_param_empty_os(mocker):
    mocker.patch("nadzoring.network_base.network_params.system", return_value="")
    assert network_param() is None
