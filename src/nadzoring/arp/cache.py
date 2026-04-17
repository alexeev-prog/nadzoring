"""ARP cache retrieval functionality."""

import ipaddress
import re
import subprocess
import sys
from collections.abc import Callable
from re import Match
from shutil import which
from subprocess import CompletedProcess

from nadzoring.arp.models import ARPEntry, ARPEntryState
from nadzoring.utils.errors import ARPCacheRetrievalError


class ARPCache:
    """ARP cache retrieval and parsing.

    Provides platform-specific methods to retrieve and parse ARP cache entries
    from Linux, Windows, and macOS systems. Automatically detects the current
    platform and uses the appropriate command and parser.
    """

    @staticmethod
    def _get_platform() -> str:
        """Detect the current platform.

        Returns:
            Platform identifier: ``"linux"``, ``"windows"``, or ``"darwin"``.

        Raises:
            ARPCacheRetrievalError: If the platform is not supported.
        """
        if sys.platform.startswith("linux"):
            return "linux"
        if sys.platform == "win32":
            return "windows"
        if sys.platform == "darwin":
            return "darwin"
        raise ARPCacheRetrievalError("Unsupported platform")

    def get_cache(self) -> list[ARPEntry]:
        """Get ARP cache entries for the current platform.

        Automatically selects the appropriate method based on the detected
        platform and returns parsed ARP entries.

        Returns:
            List of :class:`ARPEntry` objects representing the current ARP cache.

        Raises:
            ARPCacheRetrievalError: If cache retrieval fails or platform is
                unsupported.
        """
        platform: str = self._get_platform()
        dispatch: dict[str, Callable[[], list[ARPEntry]]] = {
            "linux": self._get_linux_cache,
            "windows": self._get_windows_cache,
            "darwin": self._get_darwin_cache,
        }
        return dispatch[platform]()

    def _get_linux_cache(self) -> list[ARPEntry]:
        """Get ARP cache on Linux using ``ip neigh``.

        Returns:
            List of :class:`ARPEntry` objects from the Linux ARP cache.

        Raises:
            ARPCacheRetrievalError: If ``ip`` command not found or fails.
        """
        ip_path: str | None = which("ip")
        if not ip_path:
            raise ARPCacheRetrievalError("Command not found")

        try:
            result: CompletedProcess[str] = subprocess.run(
                [ip_path, "neigh", "show"],
                capture_output=True,
                text=True,
                check=True,
            )
            return self._parse_ip_neigh_output(result.stdout)
        except subprocess.CalledProcessError as exc:
            if "ermission" in (exc.stderr or ""):
                raise ARPCacheRetrievalError("Permission denied (needs root)") from exc
            raise ARPCacheRetrievalError("Failed to parse ARP cache output") from exc

    def _get_windows_cache(self) -> list[ARPEntry]:
        """Get ARP cache on Windows using ``arp -a``.

        Returns:
            List of :class:`ARPEntry` objects from the Windows ARP cache.

        Raises:
            ARPCacheRetrievalError: If ``arp`` command not found or fails.
        """
        arp_path = which("arp")
        if not arp_path:
            raise ARPCacheRetrievalError("Command not found")

        try:
            result: CompletedProcess[str] = subprocess.run(
                [arp_path, "-a"],
                capture_output=True,
                text=True,
                check=True,
                encoding="cp866" if sys.platform == "win32" else None,
            )
            return self._parse_windows_arp_output(result.stdout)
        except subprocess.CalledProcessError as exc:
            raise ARPCacheRetrievalError("Permission denied (needs root)") from exc

    def _get_darwin_cache(self) -> list[ARPEntry]:
        """Get ARP cache on macOS using ``arp -a``.

        Returns:
            List of :class:`ARPEntry` objects from the macOS ARP cache.

        Raises:
            ARPCacheRetrievalError: If ``arp`` command not found or fails.
        """
        arp_path: str | None = which("arp")
        if not arp_path:
            raise ARPCacheRetrievalError("Command not found")

        try:
            result: CompletedProcess[str] = subprocess.run(
                [arp_path, "-a"],
                capture_output=True,
                text=True,
                check=True,
            )
            return self._parse_darwin_arp_output(result.stdout)
        except subprocess.CalledProcessError as exc:
            if "ermission" in (exc.stderr or ""):
                raise ARPCacheRetrievalError("Permission denied (needs root)") from exc
            raise ARPCacheRetrievalError("Failed to parse ARP cache output") from exc

    def _parse_ip_neigh_output(self, output: str) -> list[ARPEntry]:
        """Parse ``ip neigh`` output on Linux.

        Args:
            output: Raw output from ``ip neigh show``.

        Returns:
            List of parsed :class:`ARPEntry` objects.
        """
        entries: list[ARPEntry] = []
        for line in output.splitlines():
            line_stripped: str = line.strip()
            if not line_stripped:
                continue

            parts: list[str] = line_stripped.split()
            if len(parts) < 3:
                continue

            ip: str = parts[0]
            interface = None
            mac = None
            state = ARPEntryState.UNKNOWN

            for i, part in enumerate(parts):
                if part == "dev" and i + 1 < len(parts):
                    interface = parts[i + 1]
                elif part == "lladdr" and i + 1 < len(parts):
                    mac = parts[i + 1]
                elif part in {
                    "REACHABLE",
                    "STALE",
                    "DELAY",
                    "PROBE",
                    "FAILED",
                    "PERMANENT",
                    "NOARP",
                }:
                    state = ARPEntryState(part.lower())

            if interface:
                entries.append(
                    ARPEntry(
                        ip_address=ip,
                        mac_address=mac,
                        interface=interface,
                        state=state,
                    )
                )

        return entries

    def _parse_windows_arp_output(self, output: str) -> list[ARPEntry]:
        """Parse ``arp -a`` output on Windows.

        Args:
            output: Raw output from Windows ``arp -a``.

        Returns:
            List of parsed :class:`ARPEntry` objects.
        """
        entries: list[ARPEntry] = []
        current_interface = None

        for raw_line in output.splitlines():
            line: str = raw_line.strip()
            if not line:
                continue

            if line.startswith("Interface:"):
                parts: list[str] = line.split()
                if len(parts) >= 2:
                    current_interface = parts[1]
                continue

            parts = line.split()
            if len(parts) >= 3 and _is_valid_ip(parts[0]):
                ip: str = parts[0]
                mac_value: str = parts[1].replace("-", ":")
                state: ARPEntryState = (
                    ARPEntryState.REACHABLE if parts[2].lower() == "dynamic" else ARPEntryState.PERMANENT
                )

                entries.append(
                    ARPEntry(
                        ip_address=ip,
                        mac_address=mac_value,
                        interface=current_interface or "unknown",
                        state=state,
                    )
                )

        return entries

    def _parse_darwin_arp_output(self, output: str) -> list[ARPEntry]:
        """Parse ``arp -a`` output on macOS.

        Args:
            output: Raw output from macOS ``arp -a``.

        Returns:
            List of parsed :class:`ARPEntry` objects.
        """
        entries: list[ARPEntry] = []
        pattern = r"\? \((\d+\.\d+\.\d+\.\d+)\) at ([\da-f:]+) on (\w+)"

        for raw_line in output.splitlines():
            match: Match[str] | None = re.search(pattern, raw_line, re.IGNORECASE)
            if match:
                ip, mac, interface = match.groups()
                entries.append(
                    ARPEntry(
                        ip_address=ip,
                        mac_address=mac,
                        interface=interface,
                        state=ARPEntryState.REACHABLE,
                    )
                )

        return entries


def _is_valid_ip(ip: str) -> bool:
    """Check whether *ip* is a valid IPv4 address string.

    Args:
        ip: String to validate.

    Returns:
        ``True`` if the string represents a valid IPv4 address.
    """
    try:
        return ipaddress.ip_address(ip).version == 4
    except ValueError:
        return False
