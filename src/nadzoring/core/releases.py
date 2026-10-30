"""Cached release information and explicit, interpreter-scoped updates."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
from contextlib import suppress
from importlib import metadata
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time
from typing import Any
from urllib.parse import quote

import requests
from packaging.version import Version

from nadzoring.core.diagnostics import application_dirs
from nadzoring.core.models import CheckResult, Status, result
from nadzoring.utils.timeout import OperationTimeoutError, TimeoutConfig, timeout_context

_REPOSITORY = "alexeev-prog/nadzoring"
_CACHE_TTL = 3600


def current_version() -> str:
    """Return the installed distribution version (never a hard-coded release)."""
    return metadata.version("nadzoring")


def _read_cache(path: Path) -> dict[str, Any] | None:
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
        age = time() - cached["timestamp"]
        if 0 <= age < _CACHE_TTL and isinstance(cached["data"], dict):
            return dict(cached["data"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return None


def _write_cache(path: Path, data: dict[str, Any]) -> None:
    temporary: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump({"timestamp": time(), "data": data}, stream)
        temporary.replace(path)
    except OSError:
        # Caching is best-effort; an unwritable cache must not hide fresh data.
        return
    finally:
        if temporary is not None:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)


def _fetch_json(url: str, config: TimeoutConfig) -> dict[str, Any]:
    path = application_dirs()["cache"] / f"{hashlib.sha256(url.encode()).hexdigest()}.json"
    cached = _read_cache(path)
    if cached is not None:
        return cached
    with requests.get(url, timeout=(config.connect, config.read), headers={"Accept": "application/json"}) as response:
        response.raise_for_status()
        data = response.json()
    if not isinstance(data, dict):
        raise TypeError("Expected a JSON object from the release API")
    _write_cache(path, data)
    return data


def version_info(*, check: bool = False, timeout_config: TimeoutConfig | None = None) -> list[CheckResult]:
    """Show the installed version and optionally compare it with stable PyPI releases.

    Args:
        check: Query PyPI for its latest published version when true.
        timeout_config: Connection, read and lifetime limits for the PyPI request.

    Returns:
        An installed-version, update-available or explicit failure observation.
    """
    installed = current_version()
    if not check:
        return [result("version", installed)]
    config = timeout_config or TimeoutConfig()
    try:
        with timeout_context(config):
            data = _fetch_json("https://pypi.org/pypi/nadzoring/json", config)
            latest = Version(data["info"]["version"])
            status: Status = "update-available" if latest > Version(installed) else "ok"
            return [result("version", f"Installed {installed}; latest {latest}", status)]
    except (requests.RequestException, OperationTimeoutError, ValueError, KeyError, TypeError) as exc:
        return [result("version", str(exc), "error")]


def _changelog_section(text: str, version: str) -> str:
    sections = re.split(r"(?m)^(?=## \[)", text)
    for section in sections:
        if re.match(rf"## \[v?{re.escape(version)}\]", section):
            return section.strip()
    raise ValueError(f"No changelog entry for {version}")


def changelog(version: str | None = None, *, timeout_config: TimeoutConfig | None = None) -> list[CheckResult]:
    """Fetch GitHub release notes, falling back to the repository changelog section.

    Args:
        version: Release version, optionally prefixed with v; defaults to installed.
        timeout_config: Connection, read and lifetime limits for GitHub requests.

    Returns:
        Release notes or an explicit failure observation.
    """
    config = timeout_config or TimeoutConfig()
    requested = version or current_version()
    try:
        normalized = str(Version(requested.removeprefix("v")))
        with timeout_context(config):
            try:
                release = _fetch_json(
                    f"https://api.github.com/repos/{_REPOSITORY}/releases/tags/{quote('v' + normalized, safe='')}",
                    config,
                )
                body = release.get("body")
                if isinstance(body, str) and body.strip():
                    return [result("changelog", body)]
            except (requests.RequestException, ValueError, TypeError):
                # Missing releases and rate limits can still use the changelog.
                pass
            data = _fetch_json(f"https://api.github.com/repos/{_REPOSITORY}/contents/CHANGELOG.md", config)
            return [result("changelog", _decode_changelog(data, normalized))]
    except (requests.RequestException, OperationTimeoutError, ValueError, KeyError, TypeError) as exc:
        return [result("changelog", str(exc), "error")]


def _decode_changelog(data: dict[str, Any], version: str) -> str:
    import base64  # ruff: ignore[import-outside-top-level] -- only needed for GitHub Contents API fallback

    return _changelog_section(base64.b64decode(data["content"], validate=False).decode("utf-8"), version)


def update(
    *,
    installer: str = "auto",
    dry_run: bool = False,
    timeout_config: TimeoutConfig | None = None,
) -> list[CheckResult]:
    """Upgrade only this interpreter's installation without shell or elevation.

    Args:
        installer: ``auto`` (prefer uv), ``pip``, or ``uv``.
        dry_run: Report the exact argument vector without spawning a process.
        timeout_config: Subprocess and whole-operation time limit.

    Returns:
        Update result, including command and any subprocess failure.
    """
    config = timeout_config or TimeoutConfig()
    if installer not in {"auto", "pip", "uv"}:
        return [result("update", f"Unsupported installer: {installer}", "error")]
    uv = shutil.which("uv")
    if installer == "uv" and uv is None:
        return [result("update", "uv executable not found", "error")]
    command = (
        [uv, "pip", "install", "--python", sys.executable, "--upgrade", "nadzoring"]
        if uv and installer != "pip"
        else [sys.executable, "-m", "pip", "install", "--upgrade", "nadzoring"]
    )
    if dry_run:
        return [result("update", json.dumps(command))]
    try:
        with timeout_context(config):
            completed = subprocess.run(command, capture_output=True, text=True, timeout=config.lifetime, check=False)
        detail = completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip()
        return [
            result(
                "update",
                detail or f"Installer exited with {completed.returncode}",
                "ok" if completed.returncode == 0 else "error",
            )
        ]
    except (OSError, subprocess.TimeoutExpired, OperationTimeoutError) as exc:
        return [result("update", str(exc), "error")]
