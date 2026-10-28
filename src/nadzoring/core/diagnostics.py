"""Environment diagnostics independent of the command-line interface."""

import ipaddress
import os
import shutil
import socket
import sys
from importlib import metadata
from pathlib import Path
from tempfile import TemporaryFile
from time import perf_counter

import dns.resolver
import ping3  # type: ignore[import-untyped]  # ping3 does not ship typing metadata.
import requests
from packaging.requirements import InvalidRequirement, Requirement
from packaging.version import InvalidVersion

from nadzoring.core.models import CheckResult, result
from nadzoring.utils.timeout import OperationTimeoutError, TimeoutConfig, timeout_context


def application_dirs() -> dict[str, Path]:
    """Return native config/cache paths, respecting XDG and Windows overrides."""
    if sys.platform == "win32":
        config = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        cache = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
    elif sys.platform == "darwin":
        config = Path.home() / "Library" / "Application Support"
        cache = Path.home() / "Library" / "Caches"
    else:
        config = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
        cache = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache")))
    return {"config": config / "nadzoring", "cache": cache / "nadzoring"}


def check_dependencies(*, strict: bool = False) -> list[CheckResult]:
    """Validate installed runtime requirements, including markers and extras.

    Requirements come from wheel metadata generated from pyproject.toml. Extra
    distributions are informational unless strict mode is requested; optional
    dependency groups are not required by the base installation.

    Args:
        strict: Treat distributions outside the runtime dependency graph as warnings.

    Returns:
        Dependency observations and an extra-package summary, with explicit errors.
    """
    rows: list[CheckResult] = []
    try:
        requirements = metadata.requires("nadzoring") or []
    except metadata.PackageNotFoundError as exc:
        return [result("dependencies", str(exc), "error")]
    required_names = {"nadzoring"}
    pending = [(text, "", True) for text in requirements]
    visited: set[tuple[str, str]] = set()
    while pending:
        text, extra, direct = pending.pop(0)
        try:
            requirement = Requirement(text)
            if requirement.marker and not requirement.marker.evaluate({"extra": extra}):
                continue
            name = requirement.name.lower().replace("_", "-").replace(".", "-")
            key = (str(requirement), extra)
            if key in visited:
                continue
            visited.add(key)
            required_names.add(name)
            installed = metadata.version(requirement.name)
            if requirement.specifier and not requirement.specifier.contains(installed, prereleases=True):
                rows.append(result(name, f"Installed {installed}; requires {requirement.specifier}", "error"))
            elif direct:
                rows.append(result(name, f"Installed {installed}; requires {requirement.specifier or 'any'}"))
            for dependency in metadata.requires(requirement.name) or []:
                pending.extend((dependency, requested_extra, False) for requested_extra in {"", *requirement.extras})
        except (metadata.PackageNotFoundError, InvalidRequirement, InvalidVersion) as exc:
            rows.append(result("dependencies", str(exc), "error"))
    installed_names = {
        (dist.metadata.get("Name") or "").lower().replace("_", "-").replace(".", "-")
        for dist in metadata.distributions()
    }
    extras = sorted(installed_names - required_names - {""})
    rows.append(result("extra-packages", ", ".join(extras) or "None", "warning" if strict and extras else "ok"))
    return rows


def check_permissions(*, verbose: bool = False) -> list[CheckResult]:
    """Probe directory access, interpreter executability, and socket creation.

    Missing directories are checked through their nearest existing parent, not
    created. Temporary write probes are automatically removed. Raw socket
    permissions are optional and never trigger privilege elevation.

    Args:
        verbose: Include application and probed parent paths in successful rows.

    Returns:
        Directory, interpreter and socket permission observations.
    """
    rows: list[CheckResult] = []
    for name, directory in application_dirs().items():
        parent = directory
        while not parent.exists() and parent != parent.parent:
            parent = parent.parent
        try:
            with os.scandir(parent) as entries:
                next(entries, None)
            with TemporaryFile(dir=parent) as stream:
                stream.write(b"nadzoring permission probe")
                stream.flush()
            detail = f"Read/write access: {directory} (probed {parent})" if verbose else "Read/write access available"
            rows.append(result(name, detail))
        except OSError as exc:
            rows.append(result(name, str(exc), "error"))
    executable = os.access(sys.executable, os.X_OK)
    rows.append(result("executable", sys.executable, "ok" if executable else "error"))
    socket_types = (("socket", socket.SOCK_STREAM, 0), ("raw-socket", socket.SOCK_RAW, socket.IPPROTO_ICMP))
    for name, kind, protocol in socket_types:
        try:
            with socket.socket(socket.AF_INET, kind, protocol):
                rows.append(result(name, "Available"))
        except OSError as exc:
            rows.append(result(name, str(exc), "warning" if name == "raw-socket" else "error"))
    return rows


def check_network(target: str = "pypi.org", *, timeout_config: TimeoutConfig | None = None) -> list[CheckResult]:
    """Probe DNS, certificate-verified HTTPS, and optional ICMP for a host.

    Args:
        target: Hostname or IP address, without a URL scheme or path.
        timeout_config: Connection, read, and overall operation limits.

    Returns:
        Diagnostic rows with latency in milliseconds or an explicit error.
    """
    config = timeout_config or TimeoutConfig()
    rows: list[CheckResult] = []
    try:
        with timeout_context(config):
            rows.extend(probe(target, config) for probe in (_probe_dns, _probe_https, _probe_icmp))
    except OperationTimeoutError as exc:
        rows.append(result("network", str(exc), "error"))
    return rows


def _probe_dns(target: str, config: TimeoutConfig) -> CheckResult:
    try:
        address = ipaddress.ip_address(target)
    except ValueError:
        pass
    else:
        return result("dns", f"IP literal {address}; DNS lookup not required")
    start = perf_counter()
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = config.read
        answer = resolver.resolve(target, "A", lifetime=min(config.connect, config.lifetime))
        return result("dns", f"{answer[0]} ({(perf_counter() - start) * 1000:.2f} ms)")
    except dns.exception.DNSException as exc:
        return result("dns", str(exc), "error")


def _probe_https(target: str, config: TimeoutConfig) -> CheckResult:
    start = perf_counter()
    host = f"[{target}]" if ":" in target else target
    try:
        with requests.get(f"https://{host}/", timeout=(config.connect, config.read), stream=True) as response:
            response.raise_for_status()
            return result("https", f"HTTP {response.status_code} ({(perf_counter() - start) * 1000:.2f} ms)")
    except requests.RequestException as exc:
        return result("https", str(exc), "error")


def _probe_icmp(target: str, config: TimeoutConfig) -> CheckResult:
    try:
        latency = ping3.ping(target, timeout=min(config.read, config.lifetime), unit="ms")
        if latency is None or latency is False:
            return result("icmp", "No reply or insufficient ICMP permissions", "warning")
        return result("icmp", f"{latency:.2f} ms")
    except OSError as exc:
        return result("icmp", str(exc), "warning")


def doctor(*, timeout_config: TimeoutConfig | None = None) -> list[CheckResult]:
    """Aggregate Python, dependency, permission, network, and optional tool checks.

    Args:
        timeout_config: Limits applied to the aggregated network probes.

    Returns:
        All diagnostic observations followed by a successful-check summary.
    """
    rows = [result("python", sys.version.split()[0], "ok" if sys.version_info >= (3, 12) else "error")]
    rows.extend(check_dependencies())
    rows.extend(check_permissions())
    rows.extend(check_network(timeout_config=timeout_config))
    for tool in ("ping", "traceroute", "whois", "uv"):
        path = shutil.which(tool)
        rows.append(result(f"tool:{tool}", path or "Optional tool not found", "ok" if path else "warning"))
    passed = sum(row["status"] == "ok" for row in rows)
    rows.append(result("summary", f"{passed}/{len(rows)} checks passed ({100 * passed // len(rows)}%)"))
    return rows
