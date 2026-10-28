"""Offline regression tests for package diagnostics and self-management."""

import base64
import json
import socket
import subprocess
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import dns.exception
import pytest
import requests
import yaml
from click.shell_completion import BashComplete
from click.testing import CliRunner

from nadzoring.cli import cli
from nadzoring.core import diagnostics as diag
from nadzoring.core import releases as rel
from nadzoring.core.models import exit_code, result
from nadzoring.utils.timeout import OperationTimeoutError, TimeoutConfig

_current_version = rel.current_version


@pytest.fixture(autouse=True)
def isolate_core(tmp_path, monkeypatch):
    monkeypatch.setattr(rel, "application_dirs", lambda: {"cache": tmp_path / "cache"})
    monkeypatch.setattr(rel, "current_version", lambda: "0.3.0")
    monkeypatch.setattr(
        requests,
        "get",
        MagicMock(side_effect=AssertionError("Unmocked network request")),
    )


@pytest.mark.parametrize("status,code", [("ok", 0), ("warning", 1), ("error", 2), ("update-available", 3)])
def test_exit_codes(status, code):
    assert exit_code([result("test", "detail", status)]) == code
    assert exit_code([result("test", "detail", status), result("test", "bad", "error")]) == 2


@pytest.mark.parametrize("fmt", ["json", "yaml", "table"])
def test_cli_version_formats(fmt):
    response = CliRunner().invoke(cli, ["core", "--quiet", "--no-color", "version", "--format", fmt])
    assert response.exit_code == 0, response.output
    if fmt != "table":
        rows = json.loads(response.output) if fmt == "json" else yaml.safe_load(response.output)
        assert rows == [result("version", "0.3.0")]
    else:
        assert "0.3.0" in response.output


@pytest.mark.parametrize(
    "name,arguments,operation",
    [
        ("doctor", [], "doctor"),
        ("check-deps", ["--strict"], "check_dependencies"),
        ("check-permissions", ["--verbose"], "check_permissions"),
        ("check-network", ["--target", "8.8.8.8"], "check_network"),
        ("version", ["--check"], "version_info"),
        ("changelog", ["--version", "0.2.2"], "changelog"),
        ("update", ["--yes"], "update"),
    ],
)
@pytest.mark.parametrize("status,code", [("ok", 0), ("warning", 1), ("error", 2), ("update-available", 3)])
def test_cli_routes_and_exit_status(monkeypatch, name, arguments, operation, status, code):
    from nadzoring import core

    mock = MagicMock(return_value=[result("probe", "detail", status)])
    monkeypatch.setattr(core, operation, mock)
    response = CliRunner().invoke(cli, ["core", name, *arguments, "--format", "json"])
    assert response.exit_code == code, response.output
    assert json.loads(response.stdout)[0]["status"] == status
    mock.assert_called_once()


@pytest.mark.parametrize(
    "target",
    ["https://example.com", "x/y", "user@host", "a:443", "-x", "", "a..b", "x "],
)
def test_cli_rejects_invalid_targets(target):
    response = CliRunner().invoke(cli, ["core", "check-network", "--target", target])
    assert response.exit_code == 2


@pytest.mark.parametrize("target", ["example.com.", "::1", "127.0.0.1"])
def test_cli_accepts_targets(monkeypatch, target):
    from nadzoring import core

    monkeypatch.setattr(core, "check_network", lambda *args, **kwargs: [result("network", "ok")])
    assert CliRunner().invoke(cli, ["core", "check-network", "--target", target]).exit_code == 0


def test_update_requires_confirmation_and_dry_run_never_spawns(monkeypatch):
    run = MagicMock(side_effect=AssertionError("must not run"))
    monkeypatch.setattr(subprocess, "run", run)
    runner = CliRunner()
    assert runner.invoke(cli, ["core", "update"]).exit_code == 2
    response = runner.invoke(cli, ["core", "update", "--dry-run", "--installer", "pip", "--format", "json"])
    assert response.exit_code == 0, response.output
    command = json.loads(json.loads(response.output)[0]["detail"])
    assert command == [
        rel.sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "nadzoring",
    ]
    run.assert_not_called()


def test_completion_contains_core_commands():
    completer = BashComplete(cli, {}, "nadzoring", "_NADZORING_COMPLETE")
    assert "core" in [item.value for item in completer.get_completions([], "co")]
    names = {item.value for item in completer.get_completions(["core"], "")}
    assert names == {
        "doctor",
        "check-deps",
        "check-permissions",
        "check-network",
        "version",
        "changelog",
        "update",
    }


def test_dependency_requirements_markers_extras_and_transitives(monkeypatch):
    requirements = {
        "nadzoring": [
            "example[extra]>=2",
            "optional; extra == 'interactive'",
            "ignored; python_version < '2'",
        ],
        "example": ["child>=1; extra == 'extra'", "example>=2"],
        "child": [],
    }
    monkeypatch.setattr(metadata, "requires", lambda name: requirements[name])
    monkeypatch.setattr(metadata, "version", lambda name: "2.1")
    monkeypatch.setattr(
        metadata,
        "distributions",
        lambda: [SimpleNamespace(metadata={"Name": n}) for n in ["nadzoring", "example", "child", "dev-tool"]],
    )
    rows = diag.check_dependencies()
    assert rows[0]["check"] == "example"
    assert rows[-1] == result("extra-packages", "dev-tool")
    assert exit_code(diag.check_dependencies(strict=True)) == 1


@pytest.mark.parametrize(
    "requirement,version",
    [("example>=2", "1"), ("not a requirement!", "2"), ("example>=2", "invalid")],
)
def test_dependency_invalid_or_outdated(monkeypatch, requirement, version):
    monkeypatch.setattr(metadata, "requires", lambda name: [requirement] if name == "nadzoring" else [])
    monkeypatch.setattr(metadata, "version", lambda name: version)
    monkeypatch.setattr(metadata, "distributions", list)
    rows = diag.check_dependencies()
    assert rows[0]["error"]
    assert exit_code(rows) == 2


def test_missing_distribution(monkeypatch):
    def missing(name):
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(metadata, "requires", missing)
    assert diag.check_dependencies()[0]["error"]
    monkeypatch.setattr(metadata, "requires", lambda name: ["missing"])
    monkeypatch.setattr(metadata, "version", missing)
    monkeypatch.setattr(metadata, "distributions", list)
    assert diag.check_dependencies()[0]["error"]


@pytest.mark.parametrize("platform", ["linux", "darwin", "win32"])
def test_native_directories(monkeypatch, tmp_path, platform):
    monkeypatch.setattr(diag.sys, "platform", platform)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    for variable in ("XDG_CONFIG_HOME", "XDG_CACHE_HOME", "APPDATA", "LOCALAPPDATA"):
        monkeypatch.delenv(variable, raising=False)
    dirs = diag.application_dirs()
    assert all(path.name == "nadzoring" for path in dirs.values())
    assert all(path.is_relative_to(tmp_path) for path in dirs.values())


def test_permission_probes(monkeypatch, tmp_path):
    monkeypatch.setattr(
        diag,
        "application_dirs",
        lambda: {"config": tmp_path / "missing", "cache": tmp_path},
    )
    monkeypatch.setattr(socket, "socket", MagicMock())
    rows = diag.check_permissions(verbose=True)
    assert exit_code(rows) == 0
    assert not (tmp_path / "missing").exists()
    assert "probed" in rows[0]["detail"]
    monkeypatch.setattr(socket, "socket", MagicMock(side_effect=PermissionError("denied")))
    monkeypatch.setattr(diag.os, "access", lambda *args: False)
    monkeypatch.setattr(diag, "TemporaryFile", MagicMock(side_effect=PermissionError("denied")))
    rows = diag.check_permissions()
    assert [row["status"] for row in rows] == [
        "error",
        "error",
        "error",
        "error",
        "warning",
    ]


def test_network_success_and_timeouts(monkeypatch):
    resolver = MagicMock()
    resolver.resolve.return_value = ["1.2.3.4"]
    monkeypatch.setattr(diag.dns.resolver, "Resolver", lambda: resolver)
    response = MagicMock()
    response.__enter__.return_value.status_code = 200
    get = MagicMock(return_value=response)
    monkeypatch.setattr(requests, "get", get)
    monkeypatch.setattr(diag.ping3, "ping", lambda *args, **kwargs: 0.0)
    config = TimeoutConfig(connect=2, read=3, lifetime=10)
    assert exit_code(diag.check_network(timeout_config=config)) == 0
    assert get.call_args.kwargs["timeout"] == (2, 3)
    assert resolver.timeout == 3
    assert resolver.resolve.call_args.kwargs["lifetime"] == 2
    assert diag._probe_dns("::1", config)["status"] == "ok"
    assert diag._probe_https("::1", config)["status"] == "ok"
    assert get.call_args.args[0] == "https://[::1]/"


@pytest.mark.parametrize("icmp", [None, False, PermissionError("denied")])
def test_network_failures(monkeypatch, icmp):
    resolver = MagicMock()
    resolver.resolve.side_effect = dns.exception.Timeout()
    monkeypatch.setattr(diag.dns.resolver, "Resolver", lambda: resolver)
    monkeypatch.setattr(requests, "get", MagicMock(side_effect=requests.ConnectionError("offline")))
    ping = MagicMock(side_effect=icmp) if isinstance(icmp, Exception) else MagicMock(return_value=icmp)
    monkeypatch.setattr(diag.ping3, "ping", ping)
    rows = diag.check_network()
    assert [row["status"] for row in rows] == ["error", "error", "warning"]
    assert all(row["error"] for row in rows)


def test_network_lifetime_timeout(monkeypatch):
    monkeypatch.setattr(diag, "_probe_dns", MagicMock(side_effect=OperationTimeoutError()))
    assert diag.check_network()[0]["check"] == "network"


def test_missing_dns_configuration_is_expected_failure(monkeypatch):
    monkeypatch.setattr(
        diag.dns.resolver,
        "Resolver",
        MagicMock(side_effect=dns.resolver.NoResolverConfiguration()),
    )
    assert diag._probe_dns("example.com", TimeoutConfig())["error"] is not None


def test_doctor_aggregates_without_invoking_cli(monkeypatch):
    for name in ("check_dependencies", "check_permissions", "check_network"):
        monkeypatch.setattr(diag, name, lambda **kwargs: [result("probe", "passed")])
    monkeypatch.setattr(diag.shutil, "which", lambda tool: "/bin/uv" if tool == "uv" else None)
    rows = diag.doctor()
    assert rows[-1]["check"] == "summary"
    assert rows[-1]["detail"] == "5/8 checks passed (62%)"
    monkeypatch.setattr(diag.sys, "version_info", (3, 11))
    assert diag.doctor()[0]["status"] == "error"


def test_version_comparison_and_cache(monkeypatch):
    response = MagicMock()
    response.__enter__.return_value.json.return_value = {"info": {"version": "0.10.0"}}
    get = MagicMock(return_value=response)
    monkeypatch.setattr(requests, "get", get)
    assert exit_code(rel.version_info(check=True)) == 3
    assert exit_code(rel.version_info(check=True)) == 3
    get.assert_called_once()
    monkeypatch.setattr(rel, "current_version", lambda: "1.0.0")
    assert exit_code(rel.version_info(check=True)) == 0


@pytest.mark.parametrize("data", [{}, {"info": {"version": "invalid"}}, [], {"info": None}])
def test_malformed_release_data(monkeypatch, data):
    response = MagicMock()
    response.__enter__.return_value.json.return_value = data
    monkeypatch.setattr(requests, "get", MagicMock(return_value=response))
    assert rel.version_info(check=True)[0]["error"]


@pytest.mark.parametrize(
    "failure",
    [requests.Timeout("timeout"), OperationTimeoutError(), ValueError("json")],
)
def test_release_errors(monkeypatch, failure):
    monkeypatch.setattr(rel, "_fetch_json", MagicMock(side_effect=failure))
    assert rel.version_info(check=True)[0]["error"]
    assert rel.changelog()[0]["error"]


def test_changelog_release_and_fallback(monkeypatch):
    fetch = MagicMock(return_value={"body": "Release notes"})
    monkeypatch.setattr(rel, "_fetch_json", fetch)
    assert rel.changelog("v0.2.2")[0]["detail"] == "Release notes"
    assert fetch.call_args.args[0].endswith("/tags/v0.2.2")
    text = "# Changelog\n## [0.3.0](url) - date\nNew\n## [0.2.2](url)\nOld\n"
    content = {"content": base64.b64encode(text.encode()).decode()}
    fetch.side_effect = [requests.HTTPError("404"), content]
    assert rel.changelog()[0]["detail"].endswith("New")
    fetch.side_effect = [{"body": None}, content]
    assert rel.changelog()[0]["status"] == "ok"
    fetch.side_effect = [{}, content]
    assert rel.changelog("9.9.9")[0]["error"]
    assert rel.changelog("invalid")[0]["error"]


@pytest.mark.parametrize(
    "content",
    [
        "garbage",
        "{}",
        "[]",
        '{"timestamp": 0, "data": {}}',
        '{"timestamp": "invalid", "data": {}}',
    ],
)
def test_cache_invalid_entries(tmp_path, content):
    path = tmp_path / "cache.json"
    path.write_text(content)
    assert rel._read_cache(path) is None


def test_cache_ttl_and_optional_write_failure(tmp_path, monkeypatch):
    path = tmp_path / "cache.json"
    monkeypatch.setattr(rel, "time", lambda: 10000)
    rel._write_cache(path, {"body": "notes"})
    assert rel._read_cache(path) == {"body": "notes"}
    monkeypatch.setattr(rel, "time", lambda: 13600)
    assert rel._read_cache(path) is None
    monkeypatch.setattr(rel, "time", lambda: 9999)
    assert rel._read_cache(path) is None
    parent_file = tmp_path / "file"
    parent_file.write_text("not a directory")
    rel._write_cache(parent_file / "cache.json", {})


def test_installed_version_uses_metadata(monkeypatch):
    monkeypatch.setattr(metadata, "version", lambda name: "4.5.6")
    assert _current_version() == "4.5.6"


def test_cache_cleanup_failure_is_optional(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "unlink", MagicMock(side_effect=PermissionError("denied")))
    rel._write_cache(tmp_path / "cache.json", {})


@pytest.mark.parametrize("installer", ["pip", "uv", "auto"])
def test_update_scoped_command(monkeypatch, installer):
    monkeypatch.setattr(rel.shutil, "which", lambda name: "/bin/uv")
    run = MagicMock(return_value=SimpleNamespace(returncode=0, stdout="updated", stderr=""))
    monkeypatch.setattr(subprocess, "run", run)
    assert rel.update(installer=installer)[0]["status"] == "ok"
    command = run.call_args.args[0]
    assert rel.sys.executable in command
    assert run.call_args.kwargs["timeout"] == 120
    assert "shell" not in run.call_args.kwargs


def test_update_missing_installer_and_failures(monkeypatch):
    monkeypatch.setattr(rel.shutil, "which", lambda name: None)
    assert rel.update(installer="uv")[0]["error"]
    assert rel.update(installer="invalid")[0]["error"]
    assert "pip" in rel.update(dry_run=True)[0]["detail"]
    run = MagicMock(return_value=SimpleNamespace(returncode=1, stdout="", stderr="denied"))
    monkeypatch.setattr(subprocess, "run", run)
    assert rel.update()[0]["error"] == "denied"
    run.return_value = SimpleNamespace(returncode=1, stdout="", stderr="")
    assert "exited with 1" in rel.update()[0]["error"]
    for failure in (
        OSError("missing"),
        subprocess.TimeoutExpired("pip", 1),
        OperationTimeoutError(),
    ):
        run.side_effect = failure
        assert rel.update()[0]["error"]
