"""
Get network params on Linux, Windows.

The script returns the result of parsing the execution of standard
Linux and Windows commands. A dictionary with basic
parameters of the default network interface is returned.
The basic parameters include: the name of the network interface,
local v4 and v6 ip addresses, the default gateway address,
and the mac address of the network interface.

On some linux machines, the net-tools package must be installed,
because the route command doesn't work without it (example: Ubuntu):
sudo apt install net-tools

In addition to the above package, no third-party libraries
are required for the script to work.
"""

from ipaddress import IPv4Address
from logging import Logger
from platform import system
from socket import gethostbyname
from subprocess import CalledProcessError, check_output

import requests

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def public_ip() -> str:
    """
    Getting an external IP address by accessing the service api: https://api.ipify.org/.

    Returns:
        str: public IP

    """
    try:
        return requests.get("https://api.ipify.org/", timeout=10).text
    except Exception:
        logger.exception("Raised exception when try to access https://api.ipify.org/")
        return "127.0.0.1"


def _get_linux_network_info() -> dict[str, str | None]:
    """Get network information for Linux systems."""
    interface_info: dict[str, str | None] = _get_linux_interface_info()
    gateway_ip: str | None = _get_linux_gateway()
    mac_address: str | None = _get_linux_mac_address(interface_info.get("name"))

    return {
        "Default Interface": interface_info.get("name"),
        "IPv4 address": interface_info.get("ipv4"),
        "IPv6 address": interface_info.get("ipv6"),
        "Router ip-address": gateway_ip,
        "MAC-address": mac_address,
        "Public IP address": public_ip(),
    }


def _get_linux_interface_info() -> dict[str, str | None]:
    """Extract interface name and IP addresses on Linux."""
    try:
        command_output: str = check_output("ip -h -br a | grep UP", shell=True).decode()  # noqa: S602, S607
        parts: list[str] = command_output.split()

        return {
            "name": parts[0].strip() if len(parts) > 0 else None,
            "ipv4": parts[2].strip().split("/")[0] if len(parts) > 2 else None,
            "ipv6": parts[3].strip().split("/")[0] if len(parts) > 3 else None,
        }
    except (CalledProcessError, IndexError, AttributeError):
        logger.exception("Failed to get Linux interface information")
        return {"name": None, "ipv4": None, "ipv6": None}


def _get_linux_gateway() -> str | None:
    """Get default gateway on Linux."""
    try:
        gateway_candidate: str = (
            check_output("route -n | grep UG", shell=True).decode().split()[1]  # noqa: S602, S607
        )

        try:
            IPv4Address(gateway_candidate)
        except Exception:
            logger.exception("Invalid gateway IP format")
            return None

        try:
            return gethostbyname(gateway_candidate)
        except Exception:
            logger.exception("Failed to resolve gateway hostname")
            return gateway_candidate

    except (CalledProcessError, IndexError):
        logger.exception("Failed to get Linux gateway")
        return None


def _get_linux_mac_address(interface_name: str | None) -> str | None:
    """Get MAC address for a specific interface on Linux."""
    if not interface_name:
        return None

    try:
        mac_output: str = check_output(  # noqa: S602
            f'ifconfig {interface_name} | grep -E "ether|HWaddr"', shell=True
        ).decode()

        parts: list[str] = mac_output.split()
        for i, part in enumerate(parts):
            if part in ("ether", "HWaddr") and i + 1 < len(parts):
                return parts[i + 1]
    except (CalledProcessError, IndexError, AttributeError):
        logger.exception("Failed to get Linux MAC address")
        return None
    else:
        return None


def _get_windows_network_info() -> dict[str, str | None]:
    """Get network information for Windows systems."""
    try:
        network_configs: list[str] = _parse_windows_network_configs()
        enabled_interface: list[str] | None = _find_enabled_interface(network_configs)

        if enabled_interface:
            return _extract_interface_details(enabled_interface)

    except Exception:
        logger.exception("Failed to get Windows network information")

    return _create_empty_network_info()


def _parse_windows_network_configs() -> list[str]:
    """Parse Windows network configuration output."""
    raw_output: str = check_output(  # noqa: S602
        "wmic nicconfig get IPAddress, MACAddress, IPEnabled, SettingID, DefaultIPGateway /value",  # noqa: E501, S607
        shell=True,
    ).decode("cp866")

    config_blocks: list[str] = []
    current_block: list[str] = []

    for line in raw_output.strip().split("\r\r\n"):
        if not line.strip():
            if current_block:
                config_blocks.append("~".join(current_block))
                current_block = []
        else:
            current_block.append(line.strip())

    if current_block:
        config_blocks.append("~".join(current_block))

    return config_blocks


def _find_enabled_interface(config_blocks: list[str]) -> list[str] | None:
    """Find the first enabled network interface."""
    for block in config_blocks:
        parts: list[str] = block.split("~")
        for part in parts:
            if part.startswith("IPEnabled=") and part.split("=")[1] == "TRUE":
                return parts
    return None


def _extract_interface_details(interface_parts: list[str]) -> dict[str, str | None]:
    """Extract detailed information from an interface configuration."""
    details: dict[str, str | None] = {
        "Default Interface": None,
        "IPv4 address": None,
        "IPv6 address": None,
        "Router ip-address": None,
        "MAC-address": None,
        "Public IP address": public_ip(),
    }

    for part in interface_parts:
        if not part or "=" not in part:
            continue

        key, value = part.split("=", 1)
        if not value:
            continue

        if key == "SettingID":
            details["Default Interface"] = value
        elif key == "DefaultIPGateway":
            details["Router ip-address"] = (
                value.replace("{", "").replace("}", "").replace('"', "")
            )
        elif key == "MACAddress":
            details["MAC-address"] = value
        elif key == "IPAddress":
            ip_list: list[str] = value.replace("{", "").replace("}", "").split(",")
            if len(ip_list) > 0:
                details["IPv4 address"] = ip_list[0].replace('"', "")
            if len(ip_list) > 1:
                details["IPv6 address"] = ip_list[1].replace('"', "")

    return details


def _create_empty_network_info() -> dict[str, str | None]:
    """Create empty network information dictionary."""
    return {
        "Default Interface": None,
        "IPv4 address": None,
        "IPv6 address": None,
        "Router ip-address": None,
        "MAC-address": None,
        "Public IP address": None,
    }


def network_param() -> dict[str, str | None] | None:
    """
    Get basic network parameters for the current system.

    Returns:
        Dictionary with network interface information or None if OS not supported.

    """
    operating_system: str = system()

    if operating_system == "Linux":
        return _get_linux_network_info()
    if operating_system == "Windows":
        return _get_windows_network_info()

    logger.warning("Unsupported operating system: %s", operating_system)

    return None
