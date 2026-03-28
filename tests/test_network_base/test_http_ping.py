"""Tests for nadzoring.network_base.http_ping — 100% coverage."""

import socket

from requests.exceptions import RequestException

from nadzoring.network_base.http_ping import HttpPingResult, _measure_dns, http_ping

# ---------------------------------------------------------------------------
# _measure_dns
# ---------------------------------------------------------------------------


def test_measure_dns_success_returns_float(mocker):
    mocker.patch("nadzoring.network_base.http_ping.socket.gethostbyname", return_value="1.2.3.4")
    result = _measure_dns("example.com")
    assert isinstance(result, float)
    assert result >= 0


def test_measure_dns_gaierror_returns_none(mocker):
    mocker.patch(
        "nadzoring.network_base.http_ping.socket.gethostbyname",
        side_effect=socket.gaierror,
    )
    assert _measure_dns("invalid.local") is None


def test_measure_dns_result_rounded_to_2dp(mocker):
    mocker.patch("nadzoring.network_base.http_ping.socket.gethostbyname", return_value="1.2.3.4")
    result = _measure_dns("x")
    # Result is rounded to 2 decimal places
    assert result == round(result, 2)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _session_mock(mocker, status=200, url="http://example.com", content=b"OK", headers=None):
    """Create a mock Session that returns a fake response."""
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = status
    mock_resp.url = url
    mock_resp.headers = headers or {"Content-Type": "text/html"}
    mock_resp.content = content

    mock_ctx = mocker.MagicMock()
    mock_ctx.__enter__ = mocker.MagicMock(return_value=mock_resp)
    mock_ctx.__exit__ = mocker.MagicMock(return_value=False)

    mock_session = mocker.MagicMock()
    mock_session.get.return_value = mock_ctx

    mocker.patch("nadzoring.network_base.http_ping.Session", return_value=mock_session)
    mocker.patch("nadzoring.network_base.http_ping._measure_dns", return_value=5.0)
    return mock_session


# ---------------------------------------------------------------------------
# http_ping — happy paths
# ---------------------------------------------------------------------------


def test_http_ping_returns_result_object(mocker):
    _session_mock(mocker)
    result = http_ping("http://example.com")
    assert isinstance(result, HttpPingResult)


def test_http_ping_status_code_captured(mocker):
    _session_mock(mocker, status=404)
    result = http_ping("http://example.com")
    assert result.status_code == 404


def test_http_ping_content_length(mocker):
    _session_mock(mocker, content=b"Hello World")
    result = http_ping("http://example.com")
    assert result.content_length == 11


def test_http_ping_headers_included_by_default(mocker):
    _session_mock(mocker, headers={"X-Custom": "value"})
    result = http_ping("http://example.com")
    assert "X-Custom" in result.headers


def test_http_ping_headers_excluded_when_flag_false(mocker):
    _session_mock(mocker)
    result = http_ping("http://example.com", include_headers=False)
    assert result.headers == {}


def test_http_ping_redirect_sets_final_url(mocker):
    _session_mock(mocker, url="http://www.example.com/redirected")
    result = http_ping("http://example.com")
    assert result.final_url == "http://www.example.com/redirected"


def test_http_ping_no_redirect_final_url_none(mocker):
    _session_mock(mocker, url="http://example.com")
    result = http_ping("http://example.com")
    assert result.final_url is None


def test_http_ping_dns_ms_set(mocker):
    _session_mock(mocker)
    result = http_ping("http://example.com")
    assert result.dns_ms == 5.0


def test_http_ping_ttfb_ms_is_float(mocker):
    _session_mock(mocker)
    result = http_ping("http://example.com")
    assert isinstance(result.ttfb_ms, float)


def test_http_ping_total_ms_is_float(mocker):
    _session_mock(mocker)
    result = http_ping("http://example.com")
    assert isinstance(result.total_ms, float)


def test_http_ping_url_field_preserved(mocker):
    _session_mock(mocker)
    result = http_ping("http://example.com")
    assert result.url == "http://example.com"


def test_http_ping_error_is_none_on_success(mocker):
    _session_mock(mocker)
    result = http_ping("http://example.com")
    assert result.error is None


# ---------------------------------------------------------------------------
# Scheme injection
# ---------------------------------------------------------------------------


def test_http_ping_adds_http_scheme_when_missing(mocker):
    mock_session = _session_mock(mocker)
    result = http_ping("example.com")
    assert result.url.startswith("http://")


def test_http_ping_does_not_double_add_scheme(mocker):
    _session_mock(mocker)
    result = http_ping("https://example.com")
    assert result.url == "https://example.com"


# ---------------------------------------------------------------------------
# DNS failure
# ---------------------------------------------------------------------------


def test_http_ping_dns_failure_dns_ms_none(mocker):
    mocker.patch("nadzoring.network_base.http_ping._measure_dns", return_value=None)
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = 200
    mock_resp.url = "http://example.com"
    mock_resp.headers = {}
    mock_resp.content = b""
    mock_ctx = mocker.MagicMock()
    mock_ctx.__enter__ = mocker.MagicMock(return_value=mock_resp)
    mock_ctx.__exit__ = mocker.MagicMock(return_value=False)
    mock_session = mocker.MagicMock()
    mock_session.get.return_value = mock_ctx
    mocker.patch("nadzoring.network_base.http_ping.Session", return_value=mock_session)

    result = http_ping("http://example.com")
    assert result.dns_ms is None


# ---------------------------------------------------------------------------
# RequestException
# ---------------------------------------------------------------------------


def test_http_ping_request_exception_error_set(mocker):
    mocker.patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    mock_session = mocker.MagicMock()
    mock_session.get.side_effect = RequestException("connection refused")
    mocker.patch("nadzoring.network_base.http_ping.Session", return_value=mock_session)

    result = http_ping("http://example.com")
    assert result.error is not None
    assert result.status_code is None
    assert result.ttfb_ms is None
    assert result.total_ms is None
    assert result.content_length is None
    assert result.final_url is None


def test_http_ping_request_exception_dns_ms_preserved(mocker):
    mocker.patch("nadzoring.network_base.http_ping._measure_dns", return_value=3.0)
    mock_session = mocker.MagicMock()
    mock_session.get.side_effect = RequestException("err")
    mocker.patch("nadzoring.network_base.http_ping.Session", return_value=mock_session)

    result = http_ping("http://example.com")
    assert result.dns_ms == 3.0


def test_http_ping_session_closed_on_success(mocker):
    mock_session = _session_mock(mocker)
    http_ping("http://example.com")
    mock_session.close.assert_called_once()


def test_http_ping_session_closed_on_exception(mocker):
    mocker.patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    mock_session = mocker.MagicMock()
    mock_session.get.side_effect = RequestException("err")
    mocker.patch("nadzoring.network_base.http_ping.Session", return_value=mock_session)

    http_ping("http://example.com")
    mock_session.close.assert_called_once()


# ---------------------------------------------------------------------------
# HttpPingResult dataclass defaults
# ---------------------------------------------------------------------------


def test_result_headers_default_empty():
    r = HttpPingResult(
        url="http://x",
        final_url=None,
        status_code=200,
        dns_ms=1.0,
        ttfb_ms=10.0,
        total_ms=20.0,
        content_length=0,
    )
    assert r.headers == {}


def test_result_error_default_none():
    r = HttpPingResult(
        url="http://x",
        final_url=None,
        status_code=200,
        dns_ms=None,
        ttfb_ms=None,
        total_ms=None,
        content_length=None,
    )
    assert r.error is None
