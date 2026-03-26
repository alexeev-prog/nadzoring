"""Traceroute implementation using system commands."""

import re
import shlex
from dataclasses import dataclass, field
from logging import Logger
from platform import system
from re import Match
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any, Literal

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

_PERMISSION_DENIED_HINTS = ("operation not permitted", "permission denied")


@dataclass
class TraceHop:
    """Represents a single hop in a traceroute."""

    hop: int
    host: str | None
    ip: str | None
    rtt_ms: list[float | None] = field(default_factory=list)


def _parse_linux_traceroute(raw: str) -> list[TraceHop]:
    """
    Parse the output of the Linux traceroute command.

    Args:
        raw: Raw text output from traceroute.

    Returns:
        List of TraceHop objects.

    """
    hops: list[TraceHop] = []

    for line in raw.strip().splitlines():
        line_stripped: str = line.strip()
        if not line_stripped:
            continue

        match: Match[str] | None = re.match(r"^\s*(\d+)\s+(.+)$", line_stripped)
        if not match:
            continue

        hop_num = int(match.group(1))
        rest: str = match.group(2)

        if re.match(r"^(\*\s*)+$", rest):
            hops.append(TraceHop(hop=hop_num, host=None, ip=None, rtt_ms=[None]))
            continue

        host: str | None = None
        ip: str | None = None
        rtts: list[float | None] = []

        host_match: Match[str] | None = re.match(r"^([^\s(]+)\s*\(([^)]+)\)\s*(.*)", rest)
        if host_match:
            host = host_match.group(1)
            ip = host_match.group(2)
            rtt_str: str | Any = host_match.group(3)
        else:
            parts: list[str] = rest.split()
            if parts:
                ip = parts[0]
                host = parts[0]
                rtt_str = " ".join(parts[1:])
            else:
                rtt_str = ""

        for rtt_match in re.finditer(r"([\d.]+)\s*ms", rtt_str):
            try:
                rtts.append(float(rtt_match.group(1)))
            except ValueError:
                rtts.append(None)

        hops.append(
            TraceHop(
                hop=hop_num,
                host=host,
                ip=ip,
                rtt_ms=rtts or [None],
            )
        )

    return hops


def _parse_windows_tracert(raw: str) -> list[TraceHop]:
    """
    Parse the output of the Windows tracert command.

    Args:
        raw: Raw text output from tracert.

    Returns:
        List of TraceHop objects.

    """
    hops: list[TraceHop] = []

    for line in raw.strip().splitlines():
        line_stripped: str = line.strip()
        match: Match[str] | None = re.match(r"^\s*(\d+)\s+(.+)$", line_stripped)
        if not match:
            continue

        hop_num = int(match.group(1))
        rest: str = match.group(2)

        if re.match(r"^(\*\s*)+$", rest):
            hops.append(TraceHop(hop=hop_num, host=None, ip=None, rtt_ms=[None]))
            continue

        rtts: list[float | None] = []
        for rtt_match in re.finditer(r"(\d+)\s*ms", rest):
            try:
                rtts.append(float(rtt_match.group(1)))
            except ValueError:
                rtts.append(None)

        ip_match: Match[str] | None = re.search(r"([\d.]+)\s*$", rest)
        ip: str | None = ip_match.group(1) if ip_match else None

        host_match: Match[str] | None = re.search(r"([a-zA-Z][^\s]+)\s+[\d.]+\s*$", rest)
        host: str | None = host_match.group(1) if host_match else ip

        hops.append(
            TraceHop(
                hop=hop_num,
                host=host,
                ip=ip,
                rtt_ms=rtts or [None],
            )
        )

    return hops


def _stream_process(cmd: str, *, wall_timeout: float) -> tuple[str, str]:
    """
    Run a shell command and collect its output, returning partial output on timeout.

    Using ``Popen`` instead of ``check_output`` lets us collect whatever
    stdout was written before the wall-clock deadline fires.

    Args:
        cmd: Shell command to execute.
        wall_timeout: Maximum total wall-clock seconds to wait.

    Returns:
        Tuple of (stdout_text, stderr_text). stdout_text may be partial if
        the process was still running when the timeout fired.

    """
    with Popen(
        shlex.split(cmd),
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        errors="replace",
    ) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=wall_timeout)
        except TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            logger.warning("Command timed out after %.0f s, returning partial output", wall_timeout)

    return stdout or "", stderr or ""


def _is_permission_error(stderr: str) -> bool:
    """Return True if stderr indicates a permissions problem."""
    return any(hint in stderr.lower() for hint in _PERMISSION_DENIED_HINTS)


def _run_linux_traceroute(
    target: str,
    *,
    max_hops: int,
    per_hop_timeout: float,
    use_sudo: bool,
) -> list[TraceHop]:
    """
    Execute traceroute on Linux, falling back to tracepath if unavailable.

    Args:
        target: Hostname or IP address.
        max_hops: Maximum number of hops.
        per_hop_timeout: Per-hop timeout passed to traceroute -w.
        use_sudo: Prefix the command with sudo.

    Returns:
        List of TraceHop objects (may be partial on timeout).

    """
    timeout_int: int = max(1, int(per_hop_timeout))
    wall_timeout: float = max_hops * per_hop_timeout * 3 + 5

    prefix: Literal["", "sudo "] = "sudo " if use_sudo else ""
    cmd: str = f"{prefix}traceroute -m {max_hops} -w {timeout_int} {target}"

    stdout, stderr = _stream_process(cmd, wall_timeout=wall_timeout)

    if not stdout and _is_permission_error(stderr):
        logger.error(
            "Traceroute failed for %s due to insufficient permissions.\n\n"
            "Possible fixes:\n"
            "  • Re-run with sudo: --sudo flag or 'sudo traceroute %s'\n"
            "  • Run as root user\n"
            "  • Grant capability (Linux): sudo setcap cap_net_raw+ep $(which traceroute)",
            target,
            target,
        )
        return []

    if stdout:
        return _parse_linux_traceroute(stdout)

    if "not found" in stderr.lower() or "no such file" in stderr.lower():
        logger.warning(
            "Traceroute command not found.\n\n"
            "Possible fixes:\n"
            "  • Install traceroute:\n"
            "    - Ubuntu/Debian: sudo apt install traceroute\n"
            "    - macOS: brew install traceroute\n"
            "    - RHEL/Fedora: sudo dnf install traceroute\n"
            "  • Falling back to 'tracepath'"
        )
        return _run_tracepath(target, max_hops=max_hops, per_hop_timeout=per_hop_timeout)

    logger.warning(
        "Traceroute produced no output for %s.\n\n"
        "Possible causes:\n"
        "  • Network unreachable or blocked\n"
        "  • DNS resolution issues\n"
        "  • Firewall restrictions\n\n"
        "stderr: %s",
        target,
        stderr.strip(),
    )
    return []


def _run_tracepath(
    target: str,
    *,
    max_hops: int,
    per_hop_timeout: float,
) -> list[TraceHop]:
    """
    Fallback to tracepath (does not require root on Linux).

    Args:
        target: Hostname or IP address.
        max_hops: Maximum number of hops.
        per_hop_timeout: Used to calculate the wall-clock budget.

    Returns:
        List of TraceHop objects (may be partial on timeout).

    """
    wall_timeout: float = max_hops * per_hop_timeout * 3 + 5
    stdout, stderr = _stream_process(
        f"tracepath -m {max_hops} -n {target}",
        wall_timeout=wall_timeout,
    )

    if stdout:
        return _parse_linux_traceroute(stdout)

    logger.error(
        "Tracepath also failed for %s.\n\n"
        "Possible fixes:\n"
        "  • Ensure 'tracepath' is installed (iputils package)\n"
        "  • Check network connectivity\n"
        "  • Try running with elevated privileges\n\n"
        "stderr: %s",
        target,
        stderr.strip(),
    )
    return []


def _run_windows_tracert(
    target: str,
    *,
    max_hops: int,
    per_hop_timeout: float,
) -> list[TraceHop]:
    """
    Execute tracert on Windows.

    Args:
        target: Hostname or IP address.
        max_hops: Maximum number of hops.
        per_hop_timeout: Used to calculate the wall-clock budget.

    Returns:
        List of TraceHop objects (may be partial on timeout).

    """
    wall_timeout: float = max_hops * per_hop_timeout * 3 + 5
    cmd: str = f"tracert -h {max_hops} {target}"

    try:
        with Popen(
            cmd,
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
        ) as proc:
            try:
                stdout_b, _ = proc.communicate(timeout=wall_timeout)
            except TimeoutExpired:
                proc.kill()
                stdout_b, _ = proc.communicate()
    except Exception:
        logger.exception(
            "Failed to run tracert for %s.\n\n"
            "Possible fixes:\n"
            "  • Ensure 'tracert' is available (Windows default)\n"
            "  • Run command prompt as Administrator\n"
            "  • Check network connectivity",
            target,
        )
        return []

    raw: str = stdout_b.decode("cp866", errors="replace") if stdout_b else ""
    return _parse_windows_tracert(raw)


def traceroute(
    target: str,
    *,
    max_hops: int = 30,
    per_hop_timeout: float = 2.0,
    use_sudo: bool = False,
) -> list[TraceHop]:
    """
    Perform a traceroute to the specified target host.

    Uses 'traceroute' (with 'tracepath' fallback) on Linux and 'tracert'
    on Windows. Partial results are returned if the overall timeout fires
    before the trace completes.

    On Linux, ``traceroute`` requires raw-socket privileges.  Either run the
    process as root, pass ``use_sudo=True``, or grant the capability:
    ``sudo setcap cap_net_raw+ep $(which traceroute)``.
    ``tracepath`` is tried automatically as a root-free fallback.

    Args:
        target: Hostname or IP address to trace.
        max_hops: Maximum number of hops before stopping. Defaults to 30.
        per_hop_timeout: Per-hop timeout in seconds passed to the underlying
            tool. The overall wall-clock budget is ``max_hops * per_hop_timeout
            * 3 + 5``. Defaults to 2.0.
        use_sudo: Prefix the command with ``sudo`` on Linux. Defaults to False.

    Returns:
        List of TraceHop objects. Unreachable hops have None for host/ip and
        rtt_ms contains [None].

    Examples:
        >>> hops = traceroute("8.8.8.8", max_hops=5)
        >>> hops[0].hop
        1

    """
    os_name: str = system()

    if os_name == "Linux":
        return _run_linux_traceroute(
            target,
            max_hops=max_hops,
            per_hop_timeout=per_hop_timeout,
            use_sudo=use_sudo,
        )
    if os_name == "Windows":
        return _run_windows_tracert(
            target,
            max_hops=max_hops,
            per_hop_timeout=per_hop_timeout,
        )

    logger.warning("Unsupported OS for traceroute: %s", os_name)
    return []
