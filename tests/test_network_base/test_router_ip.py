"""Tests for nadzoring.network_base.router_ip — 100% coverage."""

from socket import gaierror

from nadzoring.network_base.router_ip import (
    _get_linux_router_ip,
    _get_windows_router_ip,
    check_ipv4,
    check_ipv6,
    get_ip_from_host,
    router_ip,
)

# ---------------------------------------------------------------------------
# get_ip_from_host
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# check_ipv4 — valid addresses (fast path: 4-part all-digit)
# ---------------------------------------------------------------------------


def test_check_ipv4_standard(mocker):
    assert check_ipv4("192.168.1.1") == "192.168.1.1"


def test_check_ipv4_loopback(mocker):
    assert check_ipv4("127.0.0.1") == "127.0.0.1"


def test_check_ipv4_zeros(mocker):
    assert check_ipv4("0.0.0.0") == "0.0.0.0"


def test_check_ipv4_broadcast(mocker):
    assert check_ipv4("255.255.255.255") == "255.255.255.255"


def test_check_ipv4_leading_zeros_normalized(mocker):
    # "192.168.001.001" is 4-part all-digit → int conversion normalizes
    assert check_ipv4("192.168.001.001") == "192.168.1.1"


def test_check_ipv4_returns_str(mocker):
    assert isinstance(check_ipv4("10.0.0.1"), str)


# check_ipv4 — _is_valid_ipv4 path (parts not all digits but valid IPv4Address)
def test_check_ipv4_valid_ipv4address_path(mocker):
    # Trigger the _is_valid_ipv4 fallback: e.g. "10.0.0.1" has digit-only parts
    # so it goes fast path. To hit _is_valid_ipv4, we need non-4-part or non-digit.
    # "1.2.3.4" → 4 parts, all digit → fast path.
    # Let's provide something with non-ascii digits to force _is_valid_ipv4 branch:
    # "192.168.1.1" → fast path hits. We need parts where isdigit() fails but isascii() passes.
    # Actually "192.168.1.1a" → 4 parts, last part "1a" is ascii but not digit → falls to _is_valid_ipv4
    mock_giph = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="0.0.0.0")
    result = check_ipv4("192.168.1.1a")
    # Not valid IPv4 → get_ip_from_host called
    mock_giph.assert_called_once_with("192.168.1.1a")


# ---------------------------------------------------------------------------
# check_ipv4 — invalid → get_ip_from_host
# ---------------------------------------------------------------------------


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


def test_check_ipv4_none_string(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="None")
    assert check_ipv4("None") == "None"


# ---------------------------------------------------------------------------
# check_ipv6 — valid
# ---------------------------------------------------------------------------


def test_check_ipv6_compressed(mocker):
    assert check_ipv6("2001:db8::1") == "2001:db8::1"


def test_check_ipv6_loopback(mocker):
    assert check_ipv6("::1") == "::1"


def test_check_ipv6_unspecified(mocker):
    assert check_ipv6("::") == "::"


def test_check_ipv6_full_format(mocker):
    addr = "2001:0db8:0000:0000:0000:0000:0000:0001"
    assert check_ipv6(addr) == addr


def test_check_ipv6_ipv4_mapped(mocker):
    assert check_ipv6("::ffff:192.168.1.1") == "::ffff:192.168.1.1"


def test_check_ipv6_ipv4_compatible(mocker):
    assert check_ipv6("::192.168.1.1") == "::192.168.1.1"


def test_check_ipv6_link_local(mocker):
    assert check_ipv6("fe80::1") == "fe80::1"


def test_check_ipv6_return_type(mocker):
    assert isinstance(check_ipv6("::1"), str)


# ---------------------------------------------------------------------------
# check_ipv6 — invalid → get_ip_from_host
# ---------------------------------------------------------------------------


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


def test_check_ipv6_empty_string(mocker):
    mock = mocker.patch("nadzoring.network_base.router_ip.get_ip_from_host", return_value="")
    check_ipv6("")
    mock.assert_called_once_with("")


# ---------------------------------------------------------------------------
# _get_linux_router_ip
# ---------------------------------------------------------------------------


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
    # Simulate IndexError by returning a line with no split columns
    mb = mocker.MagicMock()
    mb.decode.return_value = "UG\n"  # grep matches "UG" but split()[1] → IndexError
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    # grep_in_line will find "UG" line, but split()[1] → IndexError
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


# ---------------------------------------------------------------------------
# _get_windows_router_ip
# ---------------------------------------------------------------------------


def test_windows_router_ipv4_success(mocker):
    mb = mocker.MagicMock()
    # Windows: gateway at index [-3] of "0.0.0.0" line
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
    # "0.0.0.0" will be found by grep but split()[-3] → IndexError if too few cols
    mb.decode.return_value = "0.0.0.0\n"
    mocker.patch("nadzoring.network_base.router_ip.check_output", return_value=mb)
    assert _get_windows_router_ip(ipv6=False) is None


# ---------------------------------------------------------------------------
# router_ip — dispatcher
# ---------------------------------------------------------------------------


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


def test_router_ip_default_ipv6_false(mocker):
    mocker.patch("nadzoring.network_base.router_ip.system", return_value="Linux")
    mock = mocker.patch("nadzoring.network_base.router_ip._get_linux_router_ip", return_value=None)
    router_ip()
    mock.assert_called_once_with(ipv6=False)
