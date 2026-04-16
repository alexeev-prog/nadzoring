"""Tests for nadzoring.network_base.service_on_port — 100% coverage."""

import pytest

from nadzoring.network_base.service_on_port import (
    _FALLBACK_SERVICES,
    get_service_on_port,
)

# ---------------------------------------------------------------------------
# System getservbyport succeeds
# ---------------------------------------------------------------------------


def test_http_port_80(mocker):
    mocker.patch("nadzoring.network_base.service_on_port.getservbyport", return_value="http")
    assert get_service_on_port(80) == "http"


def test_ssh_port_22(mocker):
    mocker.patch("nadzoring.network_base.service_on_port.getservbyport", return_value="ssh")
    assert get_service_on_port(22) == "ssh"


def test_https_port_443(mocker):
    mocker.patch("nadzoring.network_base.service_on_port.getservbyport", return_value="https")
    assert get_service_on_port(443) == "https"


def test_smtp_port_25(mocker):
    mocker.patch("nadzoring.network_base.service_on_port.getservbyport", return_value="smtp")
    assert get_service_on_port(25) == "smtp"


def test_calls_getservbyport_with_given_port(mocker):
    mock = mocker.patch("nadzoring.network_base.service_on_port.getservbyport", return_value="ftp")
    get_service_on_port(21)
    mock.assert_called_once_with(21)


# ---------------------------------------------------------------------------
# OSError → fallback table
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("port,expected", list(_FALLBACK_SERVICES.items()))
def test_fallback_known_ports(mocker, port, expected):
    mocker.patch(
        "nadzoring.network_base.service_on_port.getservbyport",
        side_effect=OSError("not found"),
    )
    assert get_service_on_port(port) == expected


def test_oserror_unknown_port_returns_Unknown(mocker):
    mocker.patch(
        "nadzoring.network_base.service_on_port.getservbyport",
        side_effect=OSError("not found"),
    )
    assert get_service_on_port(9999) == "Unknown"


# ---------------------------------------------------------------------------
# OverflowError / TypeError → fallback table
# ---------------------------------------------------------------------------


def test_overflow_error_known_port_returns_fallback(mocker):
    mocker.patch(
        "nadzoring.network_base.service_on_port.getservbyport",
        side_effect=OverflowError,
    )
    assert get_service_on_port(80) == "http"


def test_type_error_unknown_port_returns_Unknown(mocker):
    mocker.patch(
        "nadzoring.network_base.service_on_port.getservbyport",
        side_effect=TypeError,
    )
    assert get_service_on_port(0) == "Unknown"


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------


def test_return_type_is_str(mocker):
    mocker.patch("nadzoring.network_base.service_on_port.getservbyport", return_value="http")
    assert isinstance(get_service_on_port(80), str)


def test_return_type_is_str_on_fallback(mocker):
    mocker.patch(
        "nadzoring.network_base.service_on_port.getservbyport",
        side_effect=OSError,
    )
    assert isinstance(get_service_on_port(12345), str)
