"""CI/CD category connectors: Docker, Kubernetes, GitHub Actions, GitLab CI, Jenkins."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.result import ProbeResult
from nadzoring.utils.timeout import TimeoutConfig

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _http_get_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> tuple[int, dict]:  # type: ignore[type-arg]
    """Perform a GET request and parse the JSON response body.

    Returns:
        Tuple of ``(http_status_code, parsed_body)``.

    Raises:
        urllib.error.URLError: On network-level failures.
        json.JSONDecodeError: If the body is not valid JSON.
        OSError: On socket-level failures.
    """
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read())


# ---------------------------------------------------------------------------
# Docker Registry
# ---------------------------------------------------------------------------


@dataclass
class DockerRegistryConnector(ConnectorBase):
    """Probe a Docker registry's /v2/ health endpoint.

    Attributes:
        registry_url: Base URL of the registry (e.g. ``"https://registry.example.com"``).
        token: Optional Bearer token for private registries.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="docker-registry",
        category=ConnectorCategory.CICD,
        description="Checks Docker registry /v2/ health endpoint.",
        tags=("docker", "registry", "cicd"),
    )

    registry_url: str
    token: str | None = None
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        """GET ``<registry_url>/v2/`` and verify status 200 or 401.

        A 401 response is accepted as healthy — it means the registry is up
        but requires authentication.

        Returns:
            :class:`ProbeResult` with ``details["registry_url"]``.
        """
        url = self.registry_url.rstrip("/") + "/v2/"
        headers: dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        start = time.perf_counter()
        try:
            status, _ = _http_get_json(url, headers=headers, timeout=self.timeout_config.read)
            latency_ms = (time.perf_counter() - start) * 1000
            return ProbeResult(
                status="ok",
                latency_ms=latency_ms,
                details={"registry_url": self.registry_url, "http_status": status},
            )
        except urllib.error.HTTPError as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            # 401 = registry is alive, auth required
            if exc.code == 401:
                return ProbeResult(
                    status="ok",
                    latency_ms=latency_ms,
                    details={"registry_url": self.registry_url, "http_status": 401},
                )
            return ProbeResult(
                status="error",
                latency_ms=latency_ms,
                error=f"Registry returned HTTP {exc.code}",
                details={"http_status": exc.code},
            )
        except TimeoutError:
            return ProbeResult(status="unreachable", error="Registry probe timed out")
        except urllib.error.URLError as exc:
            return ProbeResult(status="unreachable", error=str(exc.reason))
        except OSError as exc:
            return ProbeResult(status="error", error=str(exc))


# ---------------------------------------------------------------------------
# Kubernetes
# ---------------------------------------------------------------------------


@dataclass
class KubernetesConnector(ConnectorBase):
    """Probe a Kubernetes API server's readiness endpoint.

    Attributes:
        api_url: Base URL of the k8s API server
            (e.g. ``"https://k8s.example.com:6443"``).
        token: Bearer token for cluster authentication.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="kubernetes",
        category=ConnectorCategory.CICD,
        description="Checks Kubernetes API server readiness via /readyz.",
        tags=("k8s", "kubernetes", "cicd"),
    )

    api_url: str
    token: str
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        """GET ``<api_url>/readyz`` and verify ``"ok"`` in the body.

        Returns:
            :class:`ProbeResult` with ``details["api_url"]``.
        """
        url = self.api_url.rstrip("/") + "/readyz"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_config.read) as resp:
                latency_ms = (time.perf_counter() - start) * 1000
                body = resp.read().decode()
                if "ok" in body.lower():
                    return ProbeResult(
                        status="ok",
                        latency_ms=latency_ms,
                        details={"api_url": self.api_url},
                    )
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"Unexpected readyz body: {body[:120]}",
                    details={"api_url": self.api_url},
                )
        except TimeoutError:
            return ProbeResult(status="unreachable", error="Kubernetes API probe timed out")
        except urllib.error.URLError as exc:
            return ProbeResult(status="unreachable", error=str(exc.reason))
        except OSError as exc:
            return ProbeResult(status="error", error=str(exc))


# ---------------------------------------------------------------------------
# GitHub Actions
# ---------------------------------------------------------------------------


@dataclass
class GithubActionsConnector(ConnectorBase):
    """Check the status of the most recent workflow run on a GitHub repository.

    Attributes:
        owner: GitHub organisation or user name.
        repo: Repository name.
        workflow_id: Workflow file name or ID (e.g. ``"ci.yml"``).
        token: GitHub personal access token with ``repo`` scope.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="github-actions",
        category=ConnectorCategory.CICD,
        description="Checks the latest GitHub Actions workflow run status.",
        tags=("github", "actions", "cicd"),
    )

    owner: str
    repo: str
    workflow_id: str
    token: str
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    _API_BASE = "https://api.github.com"

    def probe(self) -> ProbeResult:
        """Fetch the latest workflow run and map its conclusion to a status.

        Returns:
            :class:`ProbeResult` with ``details["conclusion"]`` and
            ``details["run_url"]``.
        """
        url = (
            f"{self._API_BASE}/repos/{self.owner}/{self.repo}"
            f"/actions/workflows/{self.workflow_id}/runs?per_page=1"
        )
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }
        start = time.perf_counter()
        try:
            _, body = _http_get_json(url, headers=headers, timeout=self.timeout_config.read)
            latency_ms = (time.perf_counter() - start) * 1000
            runs = body.get("workflow_runs", [])
            if not runs:
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error="No workflow runs found",
                )
            run = runs[0]
            conclusion = run.get("conclusion") or run.get("status", "unknown")
            details = {
                "conclusion": conclusion,
                "run_url": run.get("html_url"),
                "branch": run.get("head_branch"),
            }
            if conclusion == "success":
                return ProbeResult(status="ok", latency_ms=latency_ms, details=details)
            if conclusion in {"failure", "cancelled"}:
                return ProbeResult(
                    status="error",
                    latency_ms=latency_ms,
                    error=f"Workflow run ended with '{conclusion}'",
                    details=details,
                )
            # in_progress / queued / neutral / skipped
            return ProbeResult(status="degraded", latency_ms=latency_ms, details=details)
        except TimeoutError:
            return ProbeResult(status="unreachable", error="GitHub API probe timed out")
        except urllib.error.URLError as exc:
            return ProbeResult(status="unreachable", error=str(exc.reason))
        except OSError as exc:
            return ProbeResult(status="error", error=str(exc))


# ---------------------------------------------------------------------------
# GitLab CI
# ---------------------------------------------------------------------------


@dataclass
class GitlabCIConnector(ConnectorBase):
    """Check the status of the latest pipeline on a GitLab project.

    Attributes:
        gitlab_url: Base URL of the GitLab instance
            (e.g. ``"https://gitlab.com"``).
        project_id: Numeric GitLab project ID.
        token: Private token or Job token with ``read_api`` scope.
        ref: Branch or tag name to filter pipelines. Defaults to ``"main"``.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="gitlab-ci",
        category=ConnectorCategory.CICD,
        description="Checks the latest GitLab CI pipeline status.",
        tags=("gitlab", "ci", "cicd"),
    )

    gitlab_url: str
    project_id: int
    token: str
    ref: str = "main"
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        """Fetch the latest pipeline and map its status to a :class:`ProbeResult`.

        Returns:
            :class:`ProbeResult` with ``details["pipeline_status"]`` and
            ``details["pipeline_url"]``.
        """
        base = self.gitlab_url.rstrip("/")
        url = (
            f"{base}/api/v4/projects/{self.project_id}"
            f"/pipelines?ref={self.ref}&per_page=1&order_by=id&sort=desc"
        )
        headers = {"PRIVATE-TOKEN": self.token}
        start = time.perf_counter()
        try:
            _, pipelines = _http_get_json(url, headers=headers, timeout=self.timeout_config.read)
            latency_ms = (time.perf_counter() - start) * 1000
            if not pipelines:
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"No pipelines found for ref '{self.ref}'",
                )
            pipeline = pipelines[0]
            pipeline_status = pipeline.get("status", "unknown")
            details = {
                "pipeline_status": pipeline_status,
                "pipeline_url": pipeline.get("web_url"),
                "ref": self.ref,
            }
            if pipeline_status == "success":
                return ProbeResult(status="ok", latency_ms=latency_ms, details=details)
            if pipeline_status in {"failed", "canceled"}:
                return ProbeResult(
                    status="error",
                    latency_ms=latency_ms,
                    error=f"Pipeline status: '{pipeline_status}'",
                    details=details,
                )
            return ProbeResult(status="degraded", latency_ms=latency_ms, details=details)
        except TimeoutError:
            return ProbeResult(status="unreachable", error="GitLab API probe timed out")
        except urllib.error.URLError as exc:
            return ProbeResult(status="unreachable", error=str(exc.reason))
        except OSError as exc:
            return ProbeResult(status="error", error=str(exc))


# ---------------------------------------------------------------------------
# Jenkins
# ---------------------------------------------------------------------------


@dataclass
class JenkinsConnector(ConnectorBase):
    """Check the last build status for a Jenkins job.

    Attributes:
        jenkins_url: Base URL of the Jenkins server
            (e.g. ``"https://jenkins.example.com"``).
        job_name: Full job name, using ``/`` for folder-nested jobs
            (e.g. ``"my-folder/my-job"``).
        username: Jenkins username for Basic auth.
        api_token: Jenkins API token.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="jenkins",
        category=ConnectorCategory.CICD,
        description="Checks the last Jenkins build status for a job.",
        tags=("jenkins", "cicd"),
    )

    jenkins_url: str
    job_name: str
    username: str
    api_token: str
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        """Fetch ``/lastBuild/api/json`` for the given job.

        Returns:
            :class:`ProbeResult` with ``details["result"]`` and
            ``details["build_url"]``.
        """
        import base64

        job_path = "/job/".join(self.job_name.split("/"))
        url = (
            self.jenkins_url.rstrip("/")
            + f"/job/{job_path}/lastBuild/api/json"
        )
        credentials = base64.b64encode(
            f"{self.username}:{self.api_token}".encode()
        ).decode()
        headers = {"Authorization": f"Basic {credentials}"}

        start = time.perf_counter()
        try:
            _, body = _http_get_json(url, headers=headers, timeout=self.timeout_config.read)
            latency_ms = (time.perf_counter() - start) * 1000
            result = body.get("result")
            details = {
                "result": result,
                "build_url": body.get("url"),
                "building": body.get("building", False),
            }
            if body.get("building"):
                return ProbeResult(status="degraded", latency_ms=latency_ms, details=details)
            if result == "SUCCESS":
                return ProbeResult(status="ok", latency_ms=latency_ms, details=details)
            if result in {"FAILURE", "ABORTED"}:
                return ProbeResult(
                    status="error",
                    latency_ms=latency_ms,
                    error=f"Build result: '{result}'",
                    details=details,
                )
            return ProbeResult(status="degraded", latency_ms=latency_ms, details=details)
        except TimeoutError:
            return ProbeResult(status="unreachable", error="Jenkins probe timed out")
        except urllib.error.URLError as exc:
            return ProbeResult(status="unreachable", error=str(exc.reason))
        except OSError as exc:
            return ProbeResult(status="error", error=str(exc))
