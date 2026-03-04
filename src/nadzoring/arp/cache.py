"""ARP cache retrieval functionality."""

import re
import subprocess
import sys
from re import Match
from shutil import which
from subprocess import CompletedProcess
from typing import Literal

from nadzoring.arp.models import ARPEntry, ARPEntryState


class ARPCacheRetrievalError(Exception):
    """Raised when ARP cache retrieval fails."""


class ARPCache:
    """
    ARP cache retrieval and parsing.

    Provides platform-specific methods to retrieve and parse ARP cache entries
    from Linux, Windows, and macOS systems. Automatically detects the current
    platform and uses the appropriate command and parser.

    Examples:
        >>> cache = ARPCache()
        >>> entries = cache.get_cache()
        >>> for entry in entries:
        ...     print(f"{entry.ip_address} -> {entry.mac_address}")

    """

    @staticmethod
    def _get_platform() -> str:
        """
        Detect the current platform.

        Returns:
            Platform identifier: 'linux', 'windows', or 'darwin'.

        Raises:
            ARPCacheRetrievalError: If platform is not supported.

        """
        if sys.platform.startswith("linux"):
            return "linux"
        if sys.platform == "win32":
            return "windows"
        if sys.platform == "darwin":
            return "darwin"
        raise ARPCacheRetrievalError(f"Unsupported platform: {sys.platform}")

    def get_cache(self) -> list[ARPEntry]:
        """
        Get ARP cache entries for current platform.

        Automatically selects the appropriate method based on the detected
        platform and returns parsed ARP entries.

        Returns:
            List of ARPEntry objects representing the current ARP cache.

        Raises:
            ARPCacheRetrievalError: If cache retrieval fails or platform is
                unsupported.

        """
        platform: str = self._get_platform()
        method = getattr(self, f"_get_{platform}_cache")
        return method()

    def _get_linux_cache(self) -> list[ARPEntry]:
        """
        Get ARP cache on Linux using 'ip neigh'.

        Executes 'ip neigh show' command and parses the output.

        Returns:
            List of ARPEntry objects from Linux ARP cache.

        Raises:
            ARPCacheRetrievalError: If 'ip' command not found or execution fails.

        """
        ip_path: str | None = which("ip")
        if not ip_path:
            raise ARPCacheRetrievalError("'ip' command not found")

        try:
            result: CompletedProcess[str] = subprocess.run(  # noqa: S603
                [ip_path, "neigh", "show"],
                capture_output=True,
                text=True,
                check=True,
            )
            return self._parse_ip_neigh_output(result.stdout)
        except subprocess.CalledProcessError as e:
            raise ARPCacheRetrievalError(f"Failed to get ARP cache: {e}") from e

    def _get_windows_cache(self) -> list[ARPEntry]:
        """
        Get ARP cache on Windows using 'arp -a'.

        Executes 'arp -a' command and parses the output with Windows-specific
        encoding (CP866).

        Returns:
            List of ARPEntry objects from Windows ARP cache.

        Raises:
            ARPCacheRetrievalError: If 'arp' command not found or execution fails.

        """
        arp_path = which("arp")
        if not arp_path:
            raise ARPCacheRetrievalError("'arp' command not found")

        try:
            result: CompletedProcess[str] = subprocess.run(  # noqa: S603
                [arp_path, "-a"],
                capture_output=True,
                text=True,
                check=True,
                encoding="cp866" if sys.platform == "win32" else None,
            )
            return self._parse_windows_arp_output(result.stdout)
        except subprocess.CalledProcessError as e:
            raise ARPCacheRetrievalError(f"Failed to get ARP cache: {e}") from e

    def _get_darwin_cache(self) -> list[ARPEntry]:
        """
        Get ARP cache on macOS using 'arp -a'.

        Executes 'arp -a' command and parses the output.

        Returns:
            List of ARPEntry objects from macOS ARP cache.

        Raises:
            ARPCacheRetrievalError: If 'arp' command not found or execution fails.

        """
        arp_path: str | None = which("arp")
        if not arp_path:
            raise ARPCacheRetrievalError("'arp' command not found")

        try:
            result: CompletedProcess[str] = subprocess.run(  # noqa: S603
                [arp_path, "-a"],
                capture_output=True,
                text=True,
                check=True,
            )
            return self._parse_darwin_arp_output(result.stdout)
        except subprocess.CalledProcessError as e:
            raise ARPCacheRetrievalError(f"Failed to get ARP cache: {e}") from e

    def _parse_ip_neigh_output(self, output: str) -> list[ARPEntry]:
        """
        Parse 'ip neigh' output on Linux.

        Args:
            output: Raw output from 'ip neigh show' command.

        Returns:
            List of parsed ARPEntry objects.

        """
        entries: list[ARPEntry] = []
        for line in output.splitlines():
            line = line.strip()  # noqa: PLW2901
            if not line:
                continue

            parts = line.split()
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
                elif part in [
                    "REACHABLE",
                    "STALE",
                    "DELAY",
                    "PROBE",
                    "FAILED",
                    "PERMANENT",
                    "NOARP",
                ]:
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
        """
        Parse 'arp -a' output on Windows.

        Args:
            output: Raw output from Windows 'arp -a' command.

        Returns:
            List of parsed ARPEntry objects.

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
            if len(parts) >= 3 and self._is_valid_ip(parts[0]):
                ip: str = parts[0]
                mac: str = parts[1].replace("-", ":")
                state: Literal[ARPEntryState.PERMANENT, ARPEntryState.REACHABLE] = (
                    ARPEntryState.REACHABLE
                    if parts[2].lower() == "dynamic"
                    else ARPEntryState.PERMANENT
                )

                entries.append(
                    ARPEntry(
                        ip_address=ip,
                        mac_address=mac,
                        interface=current_interface or "unknown",
                        state=state,
                    )
                )

        return entries

    def _parse_darwin_arp_output(self, output: str) -> list[ARPEntry]:
        """
        Parse 'arp -a' output on macOS.

        Args:
            output: Raw output from macOS 'arp -a' command.

        Returns:
            List of parsed ARPEntry objects.

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

    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """
        Simple IP validation.

        Args:
            ip: IP address string to validate.

        Returns:
            True if string is a valid IPv4 address, False otherwise.

        """
        parts: list[str] = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
