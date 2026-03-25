"""
Get local IP address using OS utils.

Script for obtaining the local IP address using standard OS utilities.
Supports Linux and Windows operating systems by parsing command outputs.
No additional library installations required.
"""

from logging import Logger
from platform import system
from subprocess import CalledProcessError, check_output

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def _get_linux_ip() -> str | None:
    """
    Retrieves local IPv4 address on Linux systems by parsing 'ip' command output.

    Returns:
        str | None: Local IPv4 address if found, None otherwise.

    """
    try:
        output: str = check_output("ip -h -br a | grep UP", shell=True, text=True)
        parts: list[str] = output.strip().split()

        if len(parts) >= 3:
            ip_with_mask: str = parts[2]
            return ip_with_mask.split("/", maxsplit=1)[0]
    except (CalledProcessError, FileNotFoundError, IndexError):
        return None
    else:
        return None


def _parse_windows_network_config(config_lines: list[str]) -> str | None:
    """
    Parses Windows network configuration output to extract IPv4 address.

    Args:
        config_lines: List of configuration lines from wmic command.

    Returns:
        str | None: Local IPv4 address if found, None otherwise.

    """
    current_device: list[str] = []
    parsed_devices: list[list[str]] = []

    for line in config_lines:
        if not line.strip():
            if current_device:
                parsed_devices.append(current_device)
                current_device = []
        else:
            current_device.append(line.strip())

    if current_device:
        parsed_devices.append(current_device)

    for device in parsed_devices:
        properties: dict[str, str] = {}
        for prop in device:
            if "=" in prop:
                key, value = prop.split("=", 1)
                properties[key] = value

        if properties.get("IPEnabled") != "TRUE":
            continue

        ip_address: str = properties.get("IPAddress", "")
        if ip_address:
            cleaned_ip: str = (
                ip_address.replace('"', "").replace("{", "").replace("}", "")
            )
            return cleaned_ip.split(",", maxsplit=1)[0].strip()

    return None


def _get_windows_ip() -> str | None:
    """
    Retrieves local IPv4 address on Windows systems using wmic command.

    Returns:
        str | None: Local IPv4 address if found, None otherwise.

    """
    try:
        output: str = check_output(
            "wmic nicconfig get IPAddress, IPEnabled /value",
            shell=True,
            text=True,
            encoding="cp866",
        )
        config_lines: list[str] = output.strip().split("\r\r\n")
        return _parse_windows_network_config(config_lines)

    except (CalledProcessError, FileNotFoundError, UnicodeDecodeError):
        return None


def get_local_ipv4() -> str | None:
    """
    Main function to get local IPv4 address based on the operating system.

    Returns:
        str | None: Local IPv4 address if found, None otherwise.

    Raises:
        NotImplementedError: If running on an unsupported operating system.

    """
    os_name: str = system()

    if os_name == "Linux":
        return _get_linux_ip()
    if os_name == "Windows":
        return _get_windows_ip()

    logger.warning("Operation system %s not supported fot get local ipv4", os_name)

    return None
