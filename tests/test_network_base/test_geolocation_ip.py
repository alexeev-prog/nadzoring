"""Tests for nadzoring.network_base.geolocation_ip — 100% coverage."""

from requests import RequestException

from nadzoring.network_base.geolocation_ip import (
    _fetch_geo_data,
    _parse_geo_response,
    geo_ip,
)

# ---------------------------------------------------------------------------
# _fetch_geo_data
# ---------------------------------------------------------------------------


def test_fetch_returns_dict_on_success(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {
        "status": "success",
        "lat": 37.4,
        "lon": -122.0,
        "country": "US",
        "city": "MV",
    }
    mocker.patch("nadzoring.network_base.geolocation_ip.requests.get", return_value=mock_resp)
    result = _fetch_geo_data("8.8.8.8")
    assert isinstance(result, dict)


def test_fetch_calls_raise_for_status(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {}
    mocker.patch("nadzoring.network_base.geolocation_ip.requests.get", return_value=mock_resp)
    _fetch_geo_data("1.1.1.1")
    mock_resp.raise_for_status.assert_called_once()


def test_fetch_request_exception_returns_none(mocker):
    mocker.patch(
        "nadzoring.network_base.geolocation_ip.requests.get",
        side_effect=RequestException("timeout"),
    )
    assert _fetch_geo_data("8.8.8.8") is None


def test_fetch_value_error_on_json_returns_none(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.json.side_effect = ValueError("not json")
    mocker.patch("nadzoring.network_base.geolocation_ip.requests.get", return_value=mock_resp)
    assert _fetch_geo_data("8.8.8.8") is None


def test_fetch_raise_for_status_exception_returns_none(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.raise_for_status.side_effect = RequestException("403")
    mocker.patch("nadzoring.network_base.geolocation_ip.requests.get", return_value=mock_resp)
    assert _fetch_geo_data("8.8.8.8") is None


# ---------------------------------------------------------------------------
# _parse_geo_response
# ---------------------------------------------------------------------------


def test_parse_success_returns_geo_result():
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


def test_parse_fail_status_returns_none():
    data = {"status": "fail", "message": "reserved range"}
    assert _parse_geo_response(data, "192.168.1.1") is None


def test_parse_missing_fields_default_empty_string():
    data = {"status": "success"}
    result = _parse_geo_response(data, "1.2.3.4")
    assert result is not None
    assert result["lat"] == ""
    assert result["country"] == ""
    assert result["city"] == ""
    assert result["lon"] == ""


def test_parse_all_required_keys_present():
    data = {"status": "success", "lat": 0.0, "lon": 0.0, "country": "X", "city": "Y"}
    result = _parse_geo_response(data, "1.2.3.4")
    assert {"lat", "lon", "country", "city"} == set(result.keys())


def test_parse_values_are_strings():
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
# geo_ip — public API
# ---------------------------------------------------------------------------


def test_geo_ip_fetch_failure_returns_empty_dict(mocker):
    mocker.patch("nadzoring.network_base.geolocation_ip._fetch_geo_data", return_value=None)
    assert geo_ip("8.8.8.8") == {}


def test_geo_ip_fail_status_returns_empty_dict(mocker):
    mocker.patch(
        "nadzoring.network_base.geolocation_ip._fetch_geo_data",
        return_value={"status": "fail", "message": "private range"},
    )
    assert geo_ip("192.168.1.1") == {}


def test_geo_ip_success_returns_geo_result(mocker):
    mocker.patch(
        "nadzoring.network_base.geolocation_ip._fetch_geo_data",
        return_value={
            "status": "success",
            "lat": 37.4,
            "lon": -122.1,
            "country": "US",
            "city": "MV",
        },
    )
    result = geo_ip("8.8.8.8")
    assert result["country"] == "US"
    assert "lat" in result


def test_geo_ip_returns_dict(mocker):
    mocker.patch("nadzoring.network_base.geolocation_ip._fetch_geo_data", return_value=None)
    assert isinstance(geo_ip("1.2.3.4"), dict)


def test_geo_ip_falsy_on_failure(mocker):
    mocker.patch("nadzoring.network_base.geolocation_ip._fetch_geo_data", return_value=None)
    assert not geo_ip("bad")


def test_geo_ip_truthy_on_success(mocker):
    mocker.patch(
        "nadzoring.network_base.geolocation_ip._fetch_geo_data",
        return_value={
            "status": "success",
            "lat": 1.0,
            "lon": 2.0,
            "country": "X",
            "city": "Y",
        },
    )
    assert geo_ip("1.2.3.4")
