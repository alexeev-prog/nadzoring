"""Framework-specific connectors for Flask, Django, and FastAPI.

Each connector goes beyond a simple health check and exposes probes for the
most common operational concerns:

Flask
-----
- ``/health``         — liveness / readiness
- ``/metrics``        — Prometheus-compatible metrics endpoint (flask-prometheus-metrics)
- Any custom endpoint  via ``extra_checks``

Django
------
- ``/health/``        — django-health-check per-plugin status
- ``/admin/``         — Django admin login page reachability
- Any custom endpoint  via ``extra_checks``

FastAPI
-------
- ``/health``         — liveness (fastapi-health or custom)
- ``/openapi.json``   — schema availability (app fully started)
- ``/metrics``        — Prometheus metrics (prometheus-fastapi-instrumentator)
- Any custom endpoint  via ``extra_checks``

All connectors share the same probe contract:
- ``status="ok"``          — all checks passed
- ``status="degraded"``    — app responds but reports a problem
- ``status="unreachable"`` — network-level failure
- ``status="error"``       — unexpected HTTP status or exception
- Never raise for expected failures — errors go in ``ProbeResult.error``.

Usage::

    from nadzoring.plugins.examples import FlaskConnector, DjangoConnector, FastAPIConnector
    from nadzoring.plugins import PluginRegistry

    registry = PluginRegistry()
    registry.register(FlaskConnector)
    registry.register(DjangoConnector)
    registry.register(FastAPIConnector)

    result = registry.build("fastapi", base_url="http://localhost:8000").probe()
    print(result.status, result.details)
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.result import ProbeResult
from nadzoring.utils.timeout import TimeoutConfig

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    timeout: float = 10.0,
) -> tuple[int, str]:
    """Execute an HTTP request and return ``(status_code, body_text)``.

    Raises:
        urllib.error.HTTPError: On 4xx/5xx.
        urllib.error.URLError: On network-level failures.
        OSError: On socket errors.
    """
    req = urllib.request.Request(url, headers=headers or {}, data=data, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode(errors="replace")


def _json(body: str) -> dict[str, Any]:
    try:
        return json.loads(body)  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        return {}


def _check_extra(
    checks: list[str],
    base_url: str,
    timeout: float,
) -> list[dict[str, Any]]:
    """Probe each path in *checks* and return a list of result dicts."""
    results = []
    for path in checks:
        url = base_url.rstrip("/") + path
        try:
            status, _ = _request(url, timeout=timeout)
            results.append({"path": path, "http_status": status, "ok": status < 400})
        except urllib.error.HTTPError as exc:
            results.append({"path": path, "http_status": exc.code, "ok": False})
        except (urllib.error.URLError, OSError) as exc:
            results.append({"path": path, "http_status": None, "ok": False, "error": str(exc)})
    return results


# ---------------------------------------------------------------------------
# Flask
# ---------------------------------------------------------------------------


@dataclass
class FlaskConnector(ConnectorBase):
    """Comprehensive connector for a Flask application.

    Checks performed (in order):

    1. **Liveness** — ``GET <health_path>`` must return HTTP 200 and
       ``{"status": "ok"}`` (configurable).
    2. **Metrics endpoint** — ``GET <metrics_path>`` when ``check_metrics=True``.
       Accepts HTTP 200 with a non-empty body.
    3. **Extra checks** — any additional paths listed in ``extra_checks``.

    Attributes:
        base_url: Application root URL (e.g. ``"http://localhost:5000"``).
        health_path: Health endpoint path. Defaults to ``"/health"``.
        check_json: Verify ``{"status": "ok"}`` in the health response body.
        check_metrics: Also probe ``metrics_path``. Defaults to ``False``.
        metrics_path: Prometheus metrics path. Defaults to ``"/metrics"``.
        extra_checks: Additional paths to GET and assert HTTP < 400.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="flask",
        category=ConnectorCategory.WEB,
        description="Health, metrics, and custom endpoint checks for Flask.",
        tags=("flask", "python", "web"),
    )

    base_url: str
    health_path: str = "/health"
    check_json: bool = True
    check_metrics: bool = False
    metrics_path: str = "/metrics"
    extra_checks: list[str] = field(default_factory=list)
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        t = self.timeout_config.read
        details: dict[str, Any] = {}
        start = time.perf_counter()

        # --- 1. Liveness ---
        health_url = self.base_url.rstrip("/") + self.health_path
        try:
            http_status, body = _request(health_url, timeout=t)
            latency_ms = (time.perf_counter() - start) * 1000
            details["health"] = {"http_status": http_status, "latency_ms": round(latency_ms, 2)}

            if self.check_json:
                data = _json(body)
                body_status = str(data.get("status", "")).lower()
                details["health"]["body_status"] = body_status
                if body_status not in {"ok", "healthy", ""}:
                    return ProbeResult(
                        status="degraded",
                        latency_ms=latency_ms,
                        error=f"Flask reported status '{body_status}'",
                        details=details,
                    )
        except urllib.error.HTTPError as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            details["health"] = {"http_status": exc.code}
            return ProbeResult(
                status="error",
                latency_ms=latency_ms,
                error=f"Flask health returned HTTP {exc.code}",
                details=details,
            )
        except TimeoutError:
            return ProbeResult(status="unreachable", error="Flask health check timed out", details=details)
        except (urllib.error.URLError, OSError) as exc:
            return ProbeResult(status="unreachable", error=str(exc), details=details)

        # --- 2. Metrics (optional) ---
        if self.check_metrics:
            metrics_url = self.base_url.rstrip("/") + self.metrics_path
            try:
                m_status, m_body = _request(metrics_url, timeout=t)
                details["metrics"] = {
                    "http_status": m_status,
                    "non_empty": bool(m_body.strip()),
                }
            except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
                code = exc.code if isinstance(exc, urllib.error.HTTPError) else None
                details["metrics"] = {"http_status": code, "error": str(exc)}

        # --- 3. Extra checks ---
        if self.extra_checks:
            extra = _check_extra(self.extra_checks, self.base_url, t)
            details["extra_checks"] = extra
            failed_extra = [e for e in extra if not e["ok"]]
            if failed_extra:
                paths = ", ".join(e["path"] for e in failed_extra)
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"Extra checks failed: {paths}",
                    details=details,
                )

        return ProbeResult(status="ok", latency_ms=latency_ms, details=details)


# ---------------------------------------------------------------------------
# Django
# ---------------------------------------------------------------------------


@dataclass
class DjangoConnector(ConnectorBase):
    """Comprehensive connector for a Django application.

    Checks performed (in order):

    1. **Health** — ``GET <health_path>`` (django-health-check compatible).
       Parses ``{"DatabaseBackend": "working", ...}`` and reports failing plugins.
    2. **Admin reachability** — ``GET <admin_path>`` when ``check_admin=True``.
       Accepts HTTP 200 or 302 (redirect to login).
    3. **Static files** — ``GET <static_check_path>`` when set.
    4. **Extra checks** — any additional paths listed in ``extra_checks``.

    Attributes:
        base_url: Application root URL (e.g. ``"http://localhost:8000"``).
        health_path: Health endpoint path. Defaults to ``"/health/"``.
        check_json: Parse health response as JSON. Defaults to ``True``.
        check_admin: Probe the Django admin URL. Defaults to ``False``.
        admin_path: Admin URL. Defaults to ``"/admin/"``.
        static_check_path: Optional path to a static file to verify
            ``collectstatic`` was run. E.g. ``"/static/admin/css/base.css"``.
        extra_checks: Additional paths to GET and assert HTTP < 400.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="django",
        category=ConnectorCategory.WEB,
        description="Health, admin, static, and custom endpoint checks for Django.",
        tags=("django", "python", "web"),
    )

    base_url: str
    health_path: str = "/health/"
    check_json: bool = True
    check_admin: bool = False
    admin_path: str = "/admin/"
    static_check_path: str | None = None
    extra_checks: list[str] = field(default_factory=list)
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:  # noqa: C901
        t = self.timeout_config.read
        details: dict[str, Any] = {}
        start = time.perf_counter()

        # --- 1. Health ---
        health_url = self.base_url.rstrip("/") + self.health_path
        try:
            http_status, body = _request(
                health_url,
                headers={"Accept": "application/json"},
                timeout=t,
            )
            latency_ms = (time.perf_counter() - start) * 1000
            details["health"] = {"http_status": http_status, "latency_ms": round(latency_ms, 2)}

            if self.check_json:
                data = _json(body)
                failed = {k: v for k, v in data.items() if v != "working"}
                details["health"]["checks"] = data
                if failed:
                    return ProbeResult(
                        status="degraded",
                        latency_ms=latency_ms,
                        error=f"Failing health checks: {', '.join(failed)}",
                        details=details,
                    )
        except urllib.error.HTTPError as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            body_text = exc.read().decode(errors="replace") if exc.fp else ""
            details["health"] = {"http_status": exc.code}
            if self.check_json:
                data = _json(body_text)
                failed = {k: v for k, v in data.items() if v != "working"}
                details["health"]["checks"] = data
                if failed:
                    return ProbeResult(
                        status="error",
                        latency_ms=latency_ms,
                        error=f"Failing health checks: {', '.join(failed)}",
                        details=details,
                    )
            return ProbeResult(
                status="error",
                latency_ms=latency_ms,
                error=f"Django health returned HTTP {exc.code}",
                details=details,
            )
        except TimeoutError:
            return ProbeResult(status="unreachable", error="Django health check timed out", details=details)
        except (urllib.error.URLError, OSError) as exc:
            return ProbeResult(status="unreachable", error=str(exc), details=details)

        # --- 2. Admin (optional) ---
        if self.check_admin:
            admin_url = self.base_url.rstrip("/") + self.admin_path
            try:
                admin_status, _ = _request(admin_url, timeout=t)
                # 200 = login page served; 302 = redirect to login (also fine)
                details["admin"] = {"http_status": admin_status, "ok": admin_status in {200, 302}}
            except urllib.error.HTTPError as exc:
                details["admin"] = {"http_status": exc.code, "ok": False}
            except (urllib.error.URLError, OSError) as exc:
                details["admin"] = {"ok": False, "error": str(exc)}

        # --- 3. Static file (optional) ---
        if self.static_check_path:
            static_url = self.base_url.rstrip("/") + self.static_check_path
            try:
                s_status, _ = _request(static_url, timeout=t)
                details["static"] = {"http_status": s_status, "ok": s_status == 200}
            except urllib.error.HTTPError as exc:
                details["static"] = {"http_status": exc.code, "ok": False}
            except (urllib.error.URLError, OSError) as exc:
                details["static"] = {"ok": False, "error": str(exc)}

        # --- 4. Extra checks ---
        if self.extra_checks:
            extra = _check_extra(self.extra_checks, self.base_url, t)
            details["extra_checks"] = extra
            failed_extra = [e for e in extra if not e["ok"]]
            if failed_extra:
                paths = ", ".join(e["path"] for e in failed_extra)
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"Extra checks failed: {paths}",
                    details=details,
                )

        return ProbeResult(status="ok", latency_ms=latency_ms, details=details)


# ---------------------------------------------------------------------------
# FastAPI
# ---------------------------------------------------------------------------


@dataclass
class FastAPIConnector(ConnectorBase):
    """Comprehensive connector for a FastAPI application.

    Checks performed (in order):

    1. **Liveness** — ``GET <health_path>`` must return 200 and
       ``{"status": "ok"|"healthy"}`` (fastapi-health compatible).
    2. **Schema availability** — ``GET <openapi_path>`` when not ``None``.
       Verifies the app is fully initialised (all routes registered).
    3. **Metrics endpoint** — ``GET <metrics_path>`` when ``check_metrics=True``
       (prometheus-fastapi-instrumentator).
    4. **Extra checks** — any additional paths listed in ``extra_checks``.

    Attributes:
        base_url: Application root URL (e.g. ``"http://localhost:8000"``).
        health_path: Health endpoint path. Defaults to ``"/health"``.
        openapi_path: OpenAPI schema path. ``None`` skips this check.
            Defaults to ``"/openapi.json"``.
        check_metrics: Also probe ``metrics_path``. Defaults to ``False``.
        metrics_path: Prometheus metrics path. Defaults to ``"/metrics"``.
        extra_checks: Additional paths to GET and assert HTTP < 400.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="fastapi",
        category=ConnectorCategory.WEB,
        description="Health, OpenAPI schema, metrics, and custom checks for FastAPI.",
        tags=("fastapi", "python", "web", "openapi"),
    )

    base_url: str
    health_path: str = "/health"
    openapi_path: str | None = "/openapi.json"
    check_metrics: bool = False
    metrics_path: str = "/metrics"
    extra_checks: list[str] = field(default_factory=list)
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:  # noqa: C901
        t = self.timeout_config.read
        details: dict[str, Any] = {}
        start = time.perf_counter()

        # --- 1. Liveness ---
        health_url = self.base_url.rstrip("/") + self.health_path
        try:
            http_status, body = _request(health_url, timeout=t)
            latency_ms = (time.perf_counter() - start) * 1000
            data = _json(body)
            body_status = str(data.get("status", "")).lower()
            details["health"] = {
                "http_status": http_status,
                "body_status": body_status,
                "latency_ms": round(latency_ms, 2),
            }
            if body_status and body_status not in {"ok", "healthy"}:
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"FastAPI reported status '{body_status}'",
                    details=details,
                )
        except urllib.error.HTTPError as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            body_text = exc.read().decode(errors="replace") if exc.fp else ""
            data = _json(body_text)
            body_status = str(data.get("status", "")).lower()
            details["health"] = {"http_status": exc.code, "body_status": body_status}
            return ProbeResult(
                status="error",
                latency_ms=latency_ms,
                error=f"FastAPI health returned HTTP {exc.code} (status='{body_status}')",
                details=details,
            )
        except TimeoutError:
            return ProbeResult(status="unreachable", error="FastAPI health check timed out", details=details)
        except (urllib.error.URLError, OSError) as exc:
            return ProbeResult(status="unreachable", error=str(exc), details=details)

        # --- 2. OpenAPI schema ---
        if self.openapi_path:
            schema_url = self.base_url.rstrip("/") + self.openapi_path
            try:
                s_status, s_body = _request(schema_url, timeout=t)
                schema_data = _json(s_body)
                details["openapi"] = {
                    "http_status": s_status,
                    "ok": s_status == 200,
                    "title": schema_data.get("info", {}).get("title"),
                    "version": schema_data.get("info", {}).get("version"),
                    "routes": len(schema_data.get("paths", {})),
                }
            except urllib.error.HTTPError as exc:
                details["openapi"] = {"http_status": exc.code, "ok": False}
            except (urllib.error.URLError, OSError) as exc:
                details["openapi"] = {"ok": False, "error": str(exc)}

        # --- 3. Metrics (optional) ---
        if self.check_metrics:
            metrics_url = self.base_url.rstrip("/") + self.metrics_path
            try:
                m_status, m_body = _request(metrics_url, timeout=t)
                details["metrics"] = {
                    "http_status": m_status,
                    "non_empty": bool(m_body.strip()),
                }
            except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
                code = exc.code if isinstance(exc, urllib.error.HTTPError) else None
                details["metrics"] = {"http_status": code, "error": str(exc)}

        # --- 4. Extra checks ---
        if self.extra_checks:
            extra = _check_extra(self.extra_checks, self.base_url, t)
            details["extra_checks"] = extra
            failed_extra = [e for e in extra if not e["ok"]]
            if failed_extra:
                paths = ", ".join(e["path"] for e in failed_extra)
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"Extra checks failed: {paths}",
                    details=details,
                )

        return ProbeResult(status="ok", latency_ms=latency_ms, details=details)
