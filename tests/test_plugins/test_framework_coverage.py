"""Framework connector failure and optional-endpoint coverage."""

import io
import urllib.error
from unittest.mock import MagicMock, Mock

import pytest

from nadzoring.plugins.examples import frameworks as framework


@pytest.mark.parametrize("connector", [framework.FlaskConnector, framework.DjangoConnector, framework.FastAPIConnector])
@pytest.mark.parametrize(
    "failure,status",
    [
        (TimeoutError("timeout"), "unreachable"),
        (OSError("offline"), "unreachable"),
        (urllib.error.HTTPError("https://example.com", 500, "failed", {}, None), "error"),
    ],
)
def test_framework_health_errors(monkeypatch, connector, failure, status):
    """Return stable status and error fields for expected HTTP failures."""
    monkeypatch.setattr(framework, "_request", Mock(side_effect=failure))
    result = connector("https://example.com").probe()
    assert result.status == status
    assert result.error


@pytest.mark.parametrize("connector", [framework.FlaskConnector, framework.DjangoConnector, framework.FastAPIConnector])
def test_framework_unhealthy_body(monkeypatch, connector):
    """Report degraded status from application-level health failures."""
    monkeypatch.setattr(framework, "_request", Mock(return_value=(200, '{"status":"failed"}')))
    assert connector("https://example.com").probe().status == "degraded"


@pytest.mark.parametrize("connector", [framework.FlaskConnector, framework.DjangoConnector, framework.FastAPIConnector])
@pytest.mark.parametrize("failure", [None, "http", "network"])
def test_framework_optional_checks(monkeypatch, connector, failure):
    """Inspect optional endpoints and expose unsuccessful extra checks."""

    def request(url, **kwargs):
        if "/health" in url:
            return 200, "{}"
        if failure == "http":
            raise urllib.error.HTTPError(url, 500, "failed", {}, None)
        if failure == "network":
            raise OSError("offline")
        return 200, '{"paths":{},"info":{"title":"test"}}'

    monkeypatch.setattr(framework, "_request", request)
    kwargs = {"extra_checks": ["/extra"]}
    if connector is framework.DjangoConnector:
        kwargs.update(check_admin=True, static_check_path="/static/test.css")
    else:
        kwargs["check_metrics"] = True
    result = connector("https://example.com", **kwargs).probe()
    assert result.status == ("degraded" if failure else "ok")
    assert result.details["extra_checks"][0]["ok"] is (failure is None)


def test_django_error_body(monkeypatch):
    """Preserve failing plugin names from an HTTP error response body."""
    error = urllib.error.HTTPError("https://example.com", 500, "failed", {}, io.BytesIO(b'{"database":"failed"}'))
    monkeypatch.setattr(framework, "_request", Mock(side_effect=error))
    assert "database" in framework.DjangoConnector("https://example.com").probe().error


def test_framework_request_helper(monkeypatch):
    """Decode HTTP bodies and tolerate malformed health JSON."""
    response = MagicMock()
    response.__enter__.return_value.status = 200
    response.__enter__.return_value.read.return_value = b"hello"
    monkeypatch.setattr(framework.urllib.request, "urlopen", Mock(return_value=response))
    assert framework._request("https://example.com") == (200, "hello")
    assert framework._json("invalid") == {}
