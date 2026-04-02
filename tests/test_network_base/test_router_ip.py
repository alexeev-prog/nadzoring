# tests/test_network_base/test_router_ip.py
"""Tests for nadzoring.network_base.router_ip — 100% coverage."""

from socket import gaierror

from nadzoring.network_base.router_ip import (
    _get_linux_router_ip,
    _get_windows_router_ip,
    _is_valid_ipv4,
    _is_valid_ipv6,
    check_ipv4,
    check_ipv6,
    get_ip_from_host,
    router_ip,
)


def test_is_valid_ipv4_true():
    assert _is_valid_ipv4("192.168.1.1") is True
    assert _is_valid_ipv4("0.0.0.0") is True
    assert _is_valid_ipv4("255.255.255.255") is True


def test_is_valid_ipv4_false():
    assert _is_valid_ipv4("256.1.1.1") is False
    assert _is_valid_ipv4("192.168.1") is False
    assert _is_valid_ipv4("192.168.1.1.1") is False
    assert _is_valid_ipv4("not-an-ip") is False
    assert _is_valid_ipv4("") is False


def test_is_valid_ipv6_true():
    assert _is_valid_ipv6("2001:db8::1") is True
    assert _is_valid_ipv6("::1") is True
    assert _is_valid_ipv6("::") is True
    assert _is_valid_ipv6("fe80::1") is True


def test_is_valid_ipv6_false():
    assert _is_valid_ipv6("not-ipv6") is False
    assert _is_valid_ipv6("192.168.1.1") is False
    assert _is_valid_ipv6("2001:db8::1::2") is False
    assert _is_valid_ipv6("") is False


def test_get_ip_from_host_resolves_hostname(mocker):
    mocker.patch("nadzoring.network_base.router_ip.gethostbyname", return_value="1.2.3.4")
    assert get_ip_from_host("example.com") == "1.2.3.4"


def test_get_ip_from_host_gaierror_returns_original(mocker):
    mocker.patch(
        "nadzoring.network_base.router_ip.gethostbyname",
        side_effect=gaierror("fail"),
    )
    assert get_ip_from_host("invalid.local") == "invalid.local"


def test_get_ip_from_host_empty_string_gaierror(mocker):
    mocker.patch(
        "nadzoring.network_base.router_ip.gethostbyname",
        side_effect=gaierror,
    )
    assert get_ip_from_host("") == ""


def test_get_ip_from_host_passes_through_ip(mocker):
    mocker.patch("nadzoring.network_base.router_ip.gethostbyname", return_value="192.168.1.1")
    assert get_ip_from_host("192.168.1.1") == "192.168.1.1"


def test_get_ip_from_host_return_type_str(mocker):
    mocker.patch("nadzoring.network_base.router_ip.gethostbyname", return_value="1.1.1.1")
    assert isinstance(get_ip_from_host("host"), str)


def test_check_ipv4_standard():
    assert check_ipv4("192.168.1.1") == "192.168.1.1"


def test_check_ipv4_loopback():
    assert check_ipv4("127.0.0.1") == "127.0.0.1"


def test_check_ipv4_zeros():
    assert check_ipv4("0.0.0.0") == "0.0.0.0"


def test_check_ipv4_broadcast():
    assert check_ipv4("255.255.255.255") == "255.255.255.255"


def test_check_ipv4_leading_zeros_normalized():
    assert check_ipv4("192.168.001.001") == "192.168.1.1"


def test_check_ipv4_returns_str():
    assert isinstance(check_ipv4("10.0.0.1"), str)


def test_check_ipv4_invalid_octet_calls_get_ip(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="0.0.0.0")
    check_ipv4("192.168.1.1a")
    mock.assert_called_once_with("192.168.1.1a")


def test_check_ipv4_hostname_calls_get_ip(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="5.6.7.8")
    assert check_ipv4("example.com") == "5.6.7.8"
    mock.assert_called_once_with("example.com")


def test_check_ipv4_octet_out_of_range(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="256.0.0.1")
    check_ipv4("256.0.0.1")
    mock.assert_called_once_with("256.0.0.1")


def test_check_ipv4_too_many_octets(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="1.2.3.4.5")
    check_ipv4("1.2.3.4.5")
    mock.assert_called_once_with("1.2.3.4.5")


def test_check_ipv4_too_few_octets(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="192.168.1")
    check_ipv4("192.168.1")
    mock.assert_called_once_with("192.168.1")


def test_check_ipv4_empty_string(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="")
    check_ipv4("")
    mock.assert_called_once_with("")


def test_check_ipv4_with_valid_ipv4_but_non_digit_octets(mocker):
    """Test that IP with valid format but non-digit parts is resolved."""
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="1.2.3.4")
    result = check_ipv4("192.168.1.abc")
    mock.assert_called_once_with("192.168.1.abc")


def test_check_ipv6_compressed():
    assert check_ipv6("2001:db8::1") == "2001:db8::1"


def test_check_ipv6_loopback():
    assert check_ipv6("::1") == "::1"


def test_check_ipv6_unspecified():
    assert check_ipv6("::") == "::"


def test_check_ipv6_full_format():
    addr = "2001:0db8:0000:0000:0000:0000:0000:0001"
    assert check_ipv6(addr) == addr


def test_check_ipv6_ipv4_mapped():
    assert check_ipv6("::ffff:192.168.1.1") == "::ffff:192.168.1.1"


def test_check_ipv6_ipv4_compatible():
    assert check_ipv6("::192.168.1.1") == "::192.168.1.1"


def test_check_ipv6_link_local():
    assert check_ipv6("fe80::1") == "fe80::1"


def test_check_ipv6_return_type():
    assert isinstance(check_ipv6("::1"), str)


def test_check_ipv6_hostname(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="2001:db8::1")
    assert check_ipv6("example.com") == "2001:db8::1"
    mock.assert_called_once_with("example.com")


def test_check_ipv6_ipv4_string(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="192.168.1.1")
    check_ipv6("192.168.1.1")
    mock.assert_called_once_with("192.168.1.1")


def test_check_ipv6_invalid_hex(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="::1")
    check_ipv6("2001:dbg::1")
    mock.assert_called_once_with("2001:dbg::1")


def _make_route_bytes(mocker, text):
    mb = mocker.MagicMock()
    mb.decode.return_value = text
    return mb


def test_linux_router_ipv4_success(mocker):
    mocker.patch(
        "nadzoring.network_base.router_ip.check_output",
        return_value=_make_route_bytes(
            mocker,
            "default        192.168.1.1     0.0.0.0         UG    100    0        0 eth0\n",
        ),
    )
    mocker.patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.1.1")
    assert _get_linux_router_ip(ipv6=False) == "192.168.1.1"


def test_linux_router_ipv6_success(mocker):
    mocker.patch(
        "nadzoring.network_base.router_ip.check_output",
        return_value=_make_route_bytes(
            mocker,
            "default        2001:db8::1     ::              UG    100    0        0 eth0\n",
        ),
    )
    mocker.patch("nadzoring.network_base.router_ip.check_ipv6", return_value="2001:db8::1")
    assert _get_linux_router_ip(ipv6=True) == "2001:db8::1"


def test_linux_router_no_ug_lines_returns_none(mocker):
    mocker.patch(
        "nadzoring.network_base.router_ip.check_output",
        return_value=_make_route_bytes(mocker, "Kernel IP routing table\n"),
    )
    assert _get_linux_router_ip(ipv6=False) is None


def test_linux_router_empty_route_output(mocker):
    mocker.patch(
        "nadzoring.network_base.router_ip.check_output",
        return_value=_make_route_bytes(mocker, ""),
    )
    assert _get_linux_router_ip(ipv6=False) is None


def test_linux_router_oserror_returns_none(mocker):
    mocker.patch("nadzoring.network_base.router_ip.check_output", side_effect=OSError)
    assert _get_linux_router_ip(ipv6=False) is None


def test_linux_router_called_process_error_returns_none(mocker):
    from subprocess import CalledProcessError

    mocker.patch(
        "nadzoring.network_base.router_ip.check_output",
        side_effect=CalledProcessError(1, "route"),
    )
    assert _get_linux_router_ip(ipv6=False) is None


def test_linux_router_index_error_returns_none(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "UG\n"
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    result = _get_linux_router_ip(ipv6=False)
    assert result is None


def test_linux_router_multiple_routes_takes_first(mocker):
    mocker.patch(
        "nadzoring.network_base.router_ip.check_output",
        return_value=_make_route_bytes(
            mocker,
            "default        192.168.1.1     0.0.0.0         UG    100    0        0 eth0\n"
            "default        10.0.0.1        0.0.0.0         UG    200    0        0 eth1\n",
        ),
    )
    mock_cv4 = mocker.patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.1.1")
    _get_linux_router_ip(ipv6=False)
    mock_cv4.assert_called_once_with("192.168.1.1")


def test_linux_router_gateway_as_hostname(mocker):
    mocker.patch(
        "nadzoring.network_base.router_ip.check_output",
        return_value=_make_route_bytes(
            mocker,
            "default        gateway.local    0.0.0.0         UG    100    0        0 eth0\n",
        ),
    )
    mock_cv4 = mocker.patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.1.1")
    _get_linux_router_ip(ipv6=False)
    mock_cv4.assert_called_once_with("gateway.local")


def test_linux_router_with_check_ipv4_returning_different_value(mocker):
    """Test that the returned value from check_ipv4 is used."""
    mocker.patch(
        "nadzoring.network_base.router_ip.check_output",
        return_value=_make_route_bytes(mocker, "default        gateway.local    0.0.0.0         UG\n"),
    )
    mocker.patch("nadzoring.network_base.router_ip.check_ipv4", return_value="10.0.0.1")
    result = _get_linux_router_ip(ipv6=False)
    assert result == "10.0.0.1"


def test_windows_router_ipv4_success(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = (
        "Network Destination  Netmask   Gateway     Interface  Metric\n"
        "0.0.0.0              0.0.0.0   192.168.1.1 192.168.1.100  25\n"
    )
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    mocker.patch("nadzoring.network_base.router_ip.check_ipv4", return_value="192.168.1.1")
    assert _get_windows_router_ip(ipv6=False) == "192.168.1.1"


def test_windows_router_ipv6_success(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "0.0.0.0  0.0.0.0  fe80::1  eth0  10\n"
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    mocker.patch("nadzoring.network_base.router_ip.check_ipv6", return_value="fe80::1")
    assert _get_windows_router_ip(ipv6=True) == "fe80::1"


def test_windows_router_no_gateway_lines_returns_none(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "nothing relevant\n"
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    assert _get_windows_router_ip(ipv6=False) is None


def test_windows_router_empty_route_output(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = ""
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    assert _get_windows_router_ip(ipv6=False) is None


def test_windows_router_oserror_returns_none(mocker):
    mocker.patch("nadzoring.network_base.router_ip.check_output", side_effect=OSError)
    assert _get_windows_router_ip(ipv6=False) is None


def test_windows_router_unicode_decode_error_returns_none(mocker):
    mb = mocker.MagicMock()
    mb.decode.side_effect = UnicodeDecodeError("cp866", b"", 0, 1, "reason")
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    assert _get_windows_router_ip(ipv6=False) is None


def test_windows_router_index_error_returns_none(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "0.0.0.0\n"
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    assert _get_windows_router_ip(ipv6=False) is None


def test_windows_router_with_check_ipv4_returning_different_value(mocker):
    mb = mocker.MagicMock()
    mb.decode.return_value = "0.0.0.0  0.0.0.0  192.168.1.1  interface  25\n"
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    mocker.patch("nadzoring.network_base.router_ip.check_ipv4", return_value="10.0.0.1")
    result = _get_windows_router_ip(ipv6=False)
    assert result == "10.0.0.1"


def test_router_ip_linux(mocker):
    mocker.patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.router_ip._get_linux_router_ip", return_value="10.0.0.1")
    result = router_ip(ipv6=False)
    assert result == "10.0.0.1"
    mock.assert_called_once_with(ipv6=False)


def test_router_ip_linux_ipv6(mocker):
    mocker.patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.router_ip._get_linux_router_ip", return_value="::1")
    result = router_ip(ipv6=True)
    assert result == "::1"
    mock.assert_called_once_with(ipv6=True)


def test_router_ip_windows(mocker):
    mocker.patch("nadzoring.network_base.router_ip.system", return_value="Windows")
    mock = mocker.patch(
        "nadzoring.network_base.router_ip._get_windows_router_ip",
        return_value="192.168.0.1",
    )
    result = router_ip(ipv6=False)
    assert result == "192.168.0.1"
    mock.assert_called_once_with(ipv6=False)


def test_router_ip_unsupported_os_returns_none(mocker):
    mocker.patch("nadzoring.network_base.router_ip.system", return_value="Darwin")
    assert router_ip() is None


def test_router_ip_empty_os_returns_none(mocker):
    mocker.patch("nadzoring.network_base.router_ip.system", return_value="")
    assert router_ip() is None
