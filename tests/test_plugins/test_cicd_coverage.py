"""CI/CD connector status and transport failure tests."""

import urllib.error
from unittest.mock import MagicMock, Mock

import pytest

from nadzoring.plugins.connectors import cicd


def connectors():
    """Construct all CI/CD connectors with non-sensitive test credentials."""
    return [
        cicd.DockerRegistryConnector("https://registry.example", token="test"),
        cicd.KubernetesConnector("https://cluster.example", "test"),
        cicd.GithubActionsConnector("owner", "repo", "ci.yml", "test"),
        cicd.GitlabCIConnector("https://gitlab.example", 1, "test"),
        cicd.JenkinsConnector("https://jenkins.example", "folder/job", "user", "test"),
    ]


@pytest.mark.parametrize("index", range(5))
@pytest.mark.parametrize(
    "failure,status",
    [
        (TimeoutError("timeout"), "unreachable"),
        (urllib.error.URLError("offline"), "unreachable"),
        (OSError("failed"), "error"),
    ],
)
def test_cicd_transport_errors(monkeypatch, index, failure, status):
    """Map timeout, URL, and operating-system errors consistently."""
    monkeypatch.setattr(cicd, "_http_get_json", Mock(side_effect=failure))
    monkeypatch.setattr(cicd.urllib.request, "urlopen", Mock(side_effect=failure))
    result = connectors()[index].probe()
    assert result.status == status
    assert result.error


def test_registry_statuses(monkeypatch):
    """Accept healthy and authentication-required registry endpoints."""
    connector = connectors()[0]
    monkeypatch.setattr(cicd, "_http_get_json", Mock(return_value=(200, {})))
    assert connector.probe().status == "ok"
    for code, expected in [(401, "ok"), (500, "error")]:
        monkeypatch.setattr(
            cicd,
            "_http_get_json",
            Mock(
                side_effect=urllib.error.HTTPError(
                    "https://registry.example",
                    code,
                    "failed",
                    {},
                    None,
                )
            ),
        )
        assert connector.probe().status == expected


@pytest.mark.parametrize("body,status", [(b"ok", "ok"), (b"not ready", "degraded")])
def test_kubernetes_readiness(monkeypatch, body, status):
    """Interpret readiness response bodies."""
    response = MagicMock()
    response.__enter__.return_value.read.return_value = body
    monkeypatch.setattr(cicd.urllib.request, "urlopen", Mock(return_value=response))
    assert connectors()[1].probe().status == status


@pytest.mark.parametrize(
    "body,status",
    [
        ({}, "degraded"),
        ({"workflow_runs": [{"conclusion": "success"}]}, "ok"),
        ({"workflow_runs": [{"conclusion": "failure"}]}, "error"),
        ({"workflow_runs": [{"status": "in_progress"}]}, "degraded"),
    ],
)
def test_github_workflow_status(monkeypatch, body, status):
    """Interpret missing, completed, failed, and active workflow runs."""
    monkeypatch.setattr(cicd, "_http_get_json", Mock(return_value=(200, body)))
    assert connectors()[2].probe().status == status


@pytest.mark.parametrize(
    "body,status",
    [
        ([], "degraded"),
        ([{"status": "success"}], "ok"),
        ([{"status": "failed"}], "error"),
        ([{"status": "running"}], "degraded"),
    ],
)
def test_gitlab_pipeline_status(monkeypatch, body, status):
    """Interpret pipeline status independently of the GitLab service."""
    monkeypatch.setattr(cicd, "_http_get_json", Mock(return_value=(200, body)))
    assert connectors()[3].probe().status == status


@pytest.mark.parametrize(
    "body,status",
    [
        ({"building": True}, "degraded"),
        ({"result": "SUCCESS"}, "ok"),
        ({"result": "FAILURE"}, "error"),
        ({}, "degraded"),
    ],
)
def test_jenkins_build_status(monkeypatch, body, status):
    """Interpret running and completed Jenkins builds."""
    monkeypatch.setattr(cicd, "_http_get_json", Mock(return_value=(200, body)))
    assert connectors()[4].probe().status == status


def test_json_http_helper(monkeypatch):
    """Parse JSON and forward request headers and read timeout."""
    response = MagicMock()
    response.__enter__.return_value.status = 200
    response.__enter__.return_value.read.return_value = b'{"ok": true}'
    opener = Mock(return_value=response)
    monkeypatch.setattr(cicd.urllib.request, "urlopen", opener)
    assert cicd._http_get_json("https://example.com", headers={"X-Test": "test"}, timeout=2) == (200, {"ok": True})
    assert opener.call_args.kwargs["timeout"] == 2
