"""Tests for nadzoring.network_base.http_ping."""

import socket
from unittest.mock import MagicMock, patch

from nadzoring.network_base.http_ping import HttpPingResult, _measure_dns, http_ping

# ---------------------------------------------------------------------------
# _measure_dns
# ---------------------------------------------------------------------------


class TestMeasureDns:
    @patch("nadzoring.network_base.http_ping.socket.gethostbyname")
    def test_successful_resolution_returns_float(self, mock_ghbn):
        mock_ghbn.return_value = "93.184.216.34"
        result = _measure_dns("example.com")
        assert isinstance(result, float)
        assert result >= 0

    @patch("nadzoring.network_base.http_ping.socket.gethostbyname")
    def test_failed_resolution_returns_none(self, mock_ghbn):
        mock_ghbn.side_effect = socket.gaierror
        assert _measure_dns("invalid.local") is None

    @patch("nadzoring.network_base.http_ping.socket.gethostbyname")
    def test_result_in_milliseconds(self, mock_ghbn):
        mock_ghbn.return_value = "1.2.3.4"
        result = _measure_dns("example.com")
        # Should be a small positive ms value; certainly < 10_000 ms in tests
        assert result is not None
        assert result < 10_000


# ---------------------------------------------------------------------------
# http_ping
# ---------------------------------------------------------------------------


def _make_mock_response(status=200, url="http://example.com", content=b"OK"):
    resp = MagicMock()
    resp.status_code = status
    resp.url = url
    resp.headers = {"Content-Type": "text/html"}
    resp.content = content
    return resp


class TestHttpPing:
    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=5.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_successful_request_returns_result(self, mock_session_cls, mock_dns):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = _make_mock_response()
        mock_session.get.return_value.__enter__ = lambda s: mock_resp
        mock_session.get.return_value.__exit__ = MagicMock(return_value=False)

        result = http_ping("http://example.com")
        assert isinstance(result, HttpPingResult)

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=5.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_status_code_captured(self, mock_session_cls, mock_dns):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = _make_mock_response(status=404)
        mock_session.get.return_value.__enter__ = lambda s: mock_resp
        mock_session.get.return_value.__exit__ = MagicMock(return_value=False)

        result = http_ping("http://example.com")
        assert result.status_code == 404

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=None)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_dns_failure_still_attempts_request(self, mock_session_cls, mock_dns):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = _make_mock_response()
        mock_session.get.return_value.__enter__ = lambda s: mock_resp
        mock_session.get.return_value.__exit__ = MagicMock(return_value=False)

        result = http_ping("http://example.com")
        assert result.dns_ms is None

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_scheme_added_when_missing(self, mock_session_cls, mock_dns):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = _make_mock_response(url="http://example.com")
        mock_session.get.return_value.__enter__ = lambda s: mock_resp
        mock_session.get.return_value.__exit__ = MagicMock(return_value=False)

        result = http_ping("example.com")
        # The url should have been prefixed with http://
        assert result.url.startswith("http://")

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_request_exception_returns_error_result(self, mock_session_cls, mock_dns):
        from requests.exceptions import RequestException

        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.side_effect = RequestException("connection refused")

        result = http_ping("http://example.com")
        assert result.error is not None
        assert result.status_code is None
        assert result.ttfb_ms is None

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_redirect_detected_in_final_url(self, mock_session_cls, mock_dns):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = _make_mock_response(url="http://www.example.com/redirected")
        mock_session.get.return_value.__enter__ = lambda s: mock_resp
        mock_session.get.return_value.__exit__ = MagicMock(return_value=False)

        result = http_ping("http://example.com")
        assert result.final_url == "http://www.example.com/redirected"

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_no_redirect_final_url_is_none(self, mock_session_cls, mock_dns):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = _make_mock_response(url="http://example.com")
        mock_session.get.return_value.__enter__ = lambda s: mock_resp
        mock_session.get.return_value.__exit__ = MagicMock(return_value=False)

        result = http_ping("http://example.com")
        assert result.final_url is None

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_content_length_set(self, mock_session_cls, mock_dns):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = _make_mock_response(content=b"Hello World")
        mock_session.get.return_value.__enter__ = lambda s: mock_resp
        mock_session.get.return_value.__exit__ = MagicMock(return_value=False)

        result = http_ping("http://example.com")
        assert result.content_length == 11

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_headers_excluded_when_flag_false(self, mock_session_cls, mock_dns):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = _make_mock_response()
        mock_session.get.return_value.__enter__ = lambda s: mock_resp
        mock_session.get.return_value.__exit__ = MagicMock(return_value=False)

        result = http_ping("http://example.com", include_headers=False)
        assert result.headers == {}

    @patch("nadzoring.network_base.http_ping._measure_dns", return_value=2.0)
    @patch("nadzoring.network_base.http_ping.Session")
    def test_session_always_closed(self, mock_session_cls, mock_dns):
        """Session.close() must be called even when an exception occurs."""
        from requests.exceptions import RequestException

        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.side_effect = RequestException("err")

        http_ping("http://example.com")
        mock_session.close.assert_called_once()


# ---------------------------------------------------------------------------
# HttpPingResult defaults
# ---------------------------------------------------------------------------


class TestHttpPingResultDefaults:
    def test_headers_defaults_to_empty_dict(self):
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

    def test_error_defaults_to_none(self):
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
