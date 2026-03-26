"""Tests for nadzoring.network_base.geolocation_ip."""

from unittest.mock import MagicMock, patch

from requests import RequestException

from nadzoring.network_base.geolocation_ip import (
    _fetch_geo_data,
    _parse_geo_response,
    geo_ip,
)

# ---------------------------------------------------------------------------
# _fetch_geo_data
# ---------------------------------------------------------------------------


class TestFetchGeoData:
    @patch("nadzoring.network_base.geolocation_ip.requests.get")
    def test_successful_fetch_returns_dict(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "success",
            "lat": 37.4,
            "lon": -122.0,
            "country": "US",
            "city": "Mountain View",
        }
        mock_get.return_value = mock_resp
        result = _fetch_geo_data("8.8.8.8")
        assert isinstance(result, dict)

    @patch("nadzoring.network_base.geolocation_ip.requests.get")
    def test_request_exception_returns_none(self, mock_get):
        mock_get.side_effect = RequestException("timeout")
        assert _fetch_geo_data("8.8.8.8") is None

    @patch("nadzoring.network_base.geolocation_ip.requests.get")
    def test_json_parse_error_returns_none(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.side_effect = ValueError("not json")
        mock_get.return_value = mock_resp
        assert _fetch_geo_data("8.8.8.8") is None

    @patch("nadzoring.network_base.geolocation_ip.requests.get")
    def test_raise_for_status_called(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_get.return_value = mock_resp
        _fetch_geo_data("1.1.1.1")
        mock_resp.raise_for_status.assert_called_once()


# ---------------------------------------------------------------------------
# _parse_geo_response
# ---------------------------------------------------------------------------


class TestParseGeoResponse:
    def test_success_status_returns_geo_result(self):
        data = {
            "status": "success",
            "lat": 37.4,
            "lon": -122.0,
            "country": "United States",
            "city": "Mountain View",
        }
        result = _parse_geo_response(data, "8.8.8.8")
        assert result is not None
        assert result["country"] == "United States"
        assert result["city"] == "Mountain View"
        assert result["lat"] == "37.4"
        assert result["lon"] == "-122.0"

    def test_fail_status_returns_none(self):
        data = {"status": "fail", "message": "reserved range"}
        assert _parse_geo_response(data, "192.168.1.1") is None

    def test_missing_fields_default_to_empty_string(self):
        data = {"status": "success"}
        result = _parse_geo_response(data, "1.2.3.4")
        assert result is not None
        assert result["lat"] == ""
        assert result["country"] == ""

    def test_all_required_keys_present(self):
        data = {"status": "success", "lat": 0, "lon": 0, "country": "X", "city": "Y"}
        result = _parse_geo_response(data, "1.2.3.4")
        assert {"lat", "lon", "country", "city"} == set(result.keys())

    def test_values_are_strings(self):
        data = {
            "status": "success",
            "lat": 51.5,
            "lon": -0.1,
            "country": "UK",
            "city": "London",
        }
        result = _parse_geo_response(data, "1.2.3.4")
        for v in result.values():
            assert isinstance(v, str)


# ---------------------------------------------------------------------------
# geo_ip (public API)
# ---------------------------------------------------------------------------


class TestGeoIp:
    @patch("nadzoring.network_base.geolocation_ip._fetch_geo_data", return_value=None)
    def test_fetch_failure_returns_empty_dict(self, mock_fetch):
        assert geo_ip("8.8.8.8") == {}

    @patch("nadzoring.network_base.geolocation_ip._fetch_geo_data")
    def test_api_fail_status_returns_empty_dict(self, mock_fetch):
        mock_fetch.return_value = {"status": "fail", "message": "reserved range"}
        assert geo_ip("192.168.1.1") == {}

    @patch("nadzoring.network_base.geolocation_ip._fetch_geo_data")
    def test_successful_lookup_returns_geo_result(self, mock_fetch):
        mock_fetch.return_value = {
            "status": "success",
            "lat": 37.4,
            "lon": -122.1,
            "country": "United States",
            "city": "Mountain View",
        }
        result = geo_ip("8.8.8.8")
        assert result["country"] == "United States"
        assert "lat" in result

    @patch("nadzoring.network_base.geolocation_ip._fetch_geo_data")
    def test_return_is_dict(self, mock_fetch):
        mock_fetch.return_value = {"status": "fail", "message": "x"}
        result = geo_ip("1.2.3.4")
        assert isinstance(result, dict)

    @patch("nadzoring.network_base.geolocation_ip._fetch_geo_data")
    def test_truthiness_check_false_on_failure(self, mock_fetch):
        mock_fetch.return_value = None
        result = geo_ip("bad")
        assert not result

    @patch("nadzoring.network_base.geolocation_ip._fetch_geo_data")
    def test_truthiness_check_true_on_success(self, mock_fetch):
        mock_fetch.return_value = {
            "status": "success",
            "lat": 1.0,
            "lon": 2.0,
            "country": "X",
            "city": "Y",
        }
        result = geo_ip("1.2.3.4")
        assert result
