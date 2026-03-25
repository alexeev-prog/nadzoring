"""System routing table retrieval and parsing."""

import shlex
from dataclasses import dataclass
from logging import Logger
from platform import system
from subprocess import PIPE, CalledProcessError, check_output

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


@dataclass
class RouteEntry:
    """Represents a single entry in the system routing table."""

    destination: str
    gateway: str
    netmask: str | None
    interface: str | None
    metric: str | None
    flags: str | None


def _parse_linux_ip_route(raw: str) -> list[RouteEntry]:
    """
    Parse the output of 'ip route' on Linux.

    Each line is of the form:
        <destination> [via <gateway>] dev <iface> [metric <n>] ...

    Args:
        raw: Raw text output from ip route.

    Returns:
        List of RouteEntry objects.

    """
    entries: list[RouteEntry] = []

    for line in raw.strip().splitlines():
        parts: list[str] = line.split()
        if not parts:
            continue

        destination = parts[0]
        gateway: str = "0.0.0.0"
        interface: str | None = None
        metric: str | None = None

        for i, part in enumerate(parts):
            if part == "via" and i + 1 < len(parts):
                gateway = parts[i + 1]
            elif part == "dev" and i + 1 < len(parts):
                interface = parts[i + 1]
            elif part == "metric" and i + 1 < len(parts):
                metric = parts[i + 1]

        entries.append(
            RouteEntry(
                destination=destination,
                gateway=gateway,
                netmask=None,
                interface=interface,
                metric=metric,
                flags=None,
            )
        )

    return entries


def _parse_windows_route_print(raw: str) -> list[RouteEntry]:
    """
    Parse the output of 'route PRINT' on Windows.

    Extracts IPv4 routes from the Active Routes section.

    Args:
        raw: Raw text output from route PRINT.

    Returns:
        List of RouteEntry objects.

    """
    entries: list[RouteEntry] = []
    in_active_section = False

    for line in raw.splitlines():
        stripped: str = line.strip()

        if "Active Routes:" in stripped:
            in_active_section = True
            continue
        if "Persistent Routes:" in stripped or "IPv6 Route Table" in stripped:
            in_active_section = False
            continue
        if not in_active_section or not stripped:
            continue
        if "Network Destination" in stripped or stripped.startswith("="):
            continue

        parts: list[str] = stripped.split()
        if len(parts) >= 5:
            entries.append(
                RouteEntry(
                    destination=parts[0],
                    gateway=parts[2],
                    netmask=parts[1],
                    interface=parts[3],
                    metric=parts[4],
                    flags=None,
                )
            )

    return entries


def _get_linux_routes() -> list[RouteEntry]:
    """Retrieve routing table on Linux using 'ip route'."""
    try:
        raw: str = check_output(
            shlex.split("ip route"),
            stderr=PIPE,
        ).decode(errors="replace")
    except (CalledProcessError, FileNotFoundError):
        logger.exception("Failed to retrieve routing table on Linux")
        return []

    return _parse_linux_ip_route(raw)


def _get_windows_routes() -> list[RouteEntry]:
    """Retrieve routing table on Windows using 'route PRINT'."""
    try:
        raw: str = check_output(
            shlex.split("route PRINT"),
            stderr=PIPE,
        ).decode("cp866", errors="replace")
    except (CalledProcessError, FileNotFoundError):
        logger.exception("Failed to retrieve routing table on Windows")
        return []

    return _parse_windows_route_print(raw)


def get_route_table() -> list[RouteEntry]:
    """
    Retrieve the system's IP routing table.

    Uses 'ip route' on Linux and 'route PRINT' on Windows to fetch
    the current routing table and returns it as structured data.

    Returns:
        List of RouteEntry objects representing all routing table entries,
        or an empty list if the OS is unsupported or the command fails.

    Examples:
        >>> routes = get_route_table()
        >>> any(r.destination == "default" for r in routes)
        True

    """
    os_name: str = system()

    if os_name == "Linux":
        return _get_linux_routes()
    if os_name == "Windows":
        return _get_windows_routes()

    logger.warning("Unsupported OS for route table: %s", os_name)
    return []
