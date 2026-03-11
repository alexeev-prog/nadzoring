"""Active network connections listing (netstat/ss equivalent)."""

import contextlib
import re
from dataclasses import dataclass
from logging import Logger
from platform import system
from re import Match
from subprocess import PIPE, CalledProcessError, check_output

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


@dataclass
class ConnectionEntry:
    """Represents a single active network connection."""

    protocol: str
    local_address: str
    remote_address: str
    state: str
    pid: str | None = None
    process: str | None = None


def _parse_ss_output(raw: str) -> list[ConnectionEntry]:
    """
    Parse the output of the Linux 'ss' command.

    Args:
        raw: Raw text output from ss command.

    Returns:
        List of parsed ConnectionEntry objects.

    """
    entries: list[ConnectionEntry] = []
    lines: list[str] = raw.strip().splitlines()
    if len(lines) < 2:
        return entries

    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 5:
            continue

        proto: str = parts[0]
        state: str = parts[1]
        local: str = parts[4] if len(parts) > 4 else ""
        remote: str = parts[5] if len(parts) > 5 else ""

        pid: str | None = None
        process: str | None = None
        for part in parts[6:]:
            if "pid=" in part:
                with contextlib.suppress(IndexError):
                    pid = part.split("pid=")[1].split(",")[0].rstrip(")")
            if part.startswith('users:(("'):
                proc_match: Match[str] | None = re.search(r'users:\(\("([^"]+)"', part)
                if proc_match:
                    process = proc_match.group(1)

        entries.append(
            ConnectionEntry(
                protocol=proto,
                local_address=local,
                remote_address=remote,
                state=state,
                pid=pid,
                process=process,
            )
        )

    return entries


def _parse_netstat_output(raw: str) -> list[ConnectionEntry]:
    """
    Parse the output of the Windows 'netstat -ano' command.

    Args:
        raw: Raw text output from netstat -ano.

    Returns:
        List of parsed ConnectionEntry objects.

    """
    entries: list[ConnectionEntry] = []

    for line in raw.splitlines():
        parts: list[str] = line.split()
        if not parts or parts[0] not in ("TCP", "UDP"):
            continue

        proto_value: str = parts[0]
        if proto_value == "TCP" and len(parts) >= 5:
            entries.append(
                ConnectionEntry(
                    protocol=proto_value,
                    local_address=parts[1],
                    remote_address=parts[2],
                    state=parts[3],
                    pid=parts[4],
                )
            )
        elif proto_value == "UDP" and len(parts) >= 4:
            entries.append(
                ConnectionEntry(
                    protocol=proto_value,
                    local_address=parts[1],
                    remote_address=parts[2],
                    state="",
                    pid=parts[3],
                )
            )

    return entries


def _filter_entries(
    entries: list[ConnectionEntry],
    *,
    protocol: str,
    state_filter: str | None,
) -> list[ConnectionEntry]:
    """
    Filter connection entries by protocol and state.

    Args:
        entries: List of connection entries to filter.
        protocol: Protocol filter - 'tcp', 'udp', or 'all'.
        state_filter: Optional state substring filter (case-insensitive).

    Returns:
        Filtered list of ConnectionEntry objects.

    """
    if protocol != "all":
        entries = [e for e in entries if e.protocol.lower() == protocol.lower()]
    if state_filter:
        entries = [e for e in entries if state_filter.upper() in e.state.upper()]
    return entries


def _get_linux_connections(
    *,
    protocol: str,
    state_filter: str | None,
    include_process: bool,
) -> list[ConnectionEntry]:
    """Get active connections on Linux using ss."""
    flags: str = "-tuna" + ("p" if include_process else "")
    try:
        raw: str = check_output(  # noqa: S602
            f"ss {flags}",
            shell=True,
            stderr=PIPE,
        ).decode(errors="replace")
    except (CalledProcessError, FileNotFoundError):
        logger.exception("Failed to run ss on Linux")
        return []

    entries: list[ConnectionEntry] = _parse_ss_output(raw)
    return _filter_entries(entries, protocol=protocol, state_filter=state_filter)


def _get_windows_connections(
    *,
    protocol: str,
    state_filter: str | None,
) -> list[ConnectionEntry]:
    """Get active connections on Windows using netstat."""
    try:
        raw: str = check_output(  # noqa: S602
            "netstat -ano",  # noqa: S607
            shell=True,
            stderr=PIPE,
        ).decode("cp866", errors="replace")
    except (CalledProcessError, FileNotFoundError):
        logger.exception("Failed to run netstat on Windows")
        return []

    entries: list[ConnectionEntry] = _parse_netstat_output(raw)
    return _filter_entries(entries, protocol=protocol, state_filter=state_filter)


def get_connections(
    *,
    protocol: str = "all",
    state_filter: str | None = None,
    include_process: bool = True,
) -> list[ConnectionEntry]:
    """
    List active network connections on the current system.

    On Linux, uses 'ss'. On Windows, uses 'netstat -ano'.
    Process information may require elevated permissions on some systems.

    Args:
        protocol: Protocol to filter by - 'tcp', 'udp', or 'all'. Defaults to 'all'.
        state_filter: Case-insensitive state substring filter, e.g. 'LISTEN' or
            'ESTABLISHED'. Defaults to None (no filter).
        include_process: Whether to include PID/process name (may need root on
            Linux). Defaults to True.

    Returns:
        List of ConnectionEntry objects, one per active connection.

    Examples:
        >>> listening = get_connections(state_filter="LISTEN")
        >>> len(listening) > 0
        True

    """
    os_name: str = system()

    if os_name == "Linux":
        return _get_linux_connections(
            protocol=protocol,
            state_filter=state_filter,
            include_process=include_process,
        )
    if os_name == "Windows":
        return _get_windows_connections(
            protocol=protocol,
            state_filter=state_filter,
        )

    logger.warning("Unsupported OS for connections listing: %s", os_name)
    return []
