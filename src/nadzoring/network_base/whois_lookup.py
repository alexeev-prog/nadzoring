"""WHOIS information lookup for domains and IP addresses."""

import shlex
from ipaddress import ip_address
from logging import Logger
from platform import system
from subprocess import PIPE, CalledProcessError, check_output
from typing import Literal

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

_WHOIS_FIELD_MAP: dict[str, list[str]] = {
    "registrar": ["Registrar:", "registrar:"],
    "creation_date": ["Creation Date:", "created:", "Created:"],
    "expiry_date": [
        "Registry Expiry Date:",
        "Expiry Date:",
        "expires:",
        "Expiration Date:",
    ],
    "updated_date": ["Updated Date:", "last-modified:", "Last Modified:"],
    "name_servers": ["Name Server:", "nserver:"],
    "status": ["Domain Status:", "status:"],
    "registrant_org": ["Registrant Organization:", "org:", "Organisation:"],
    "country": ["Registrant Country:", "country:"],
    "abuse_email": ["Abuse Contact Email:", "abuse-mailbox:"],
    "netrange": ["NetRange:", "inetnum:"],
    "org_name": ["OrgName:", "org-name:", "OrgName:"],
    "cidr": ["CIDR:"],
    "asn": ["OriginAS:", "origin:"],
}


def _is_ip(target: str) -> bool:
    """Return True if target is a valid IP address."""
    try:
        ip_address(target)
    except ValueError:
        return False
    return True


def _run_whois_command(target: str) -> str | None:
    """
    Execute the system whois command for the given target.

    Args:
        target: Domain or IP address to query.

    Returns:
        Raw WHOIS output string, or None if the command failed.

    """
    os_name: str = system()
    encoding: Literal["cp866", "utf-8"] = "cp866" if os_name == "Windows" else "utf-8"

    try:
        return check_output(
            shlex.split(f"whois {target}"),
            stderr=PIPE,
            timeout=15,
        ).decode(encoding, errors="replace")
    except (CalledProcessError, FileNotFoundError, TimeoutError):
        logger.exception("Failed to run whois for %s", target)
        return None


def _parse_whois_output(raw: str) -> dict[str, str | None]:
    """
    Parse raw WHOIS text into a structured dictionary.

    Extracts known fields from the WHOIS output by matching line prefixes
    against a predefined field mapping. Only the first occurrence of each
    field is captured.

    Args:
        raw: Raw text output from the whois command.

    Returns:
        Dictionary mapping field names to extracted values.

    """
    result: dict[str, str | None] = dict.fromkeys(_WHOIS_FIELD_MAP)

    for line in raw.splitlines():
        stripped: str = line.strip()
        if not stripped or stripped.startswith(("%", "#")):
            continue
        for field_key, prefixes in _WHOIS_FIELD_MAP.items():
            if result[field_key] is not None:
                continue
            for prefix in prefixes:
                if stripped.lower().startswith(prefix.lower()):
                    value: str = stripped[len(prefix) :].strip()
                    if value:
                        result[field_key] = value
                        break

    return result


def whois_lookup(target: str) -> dict[str, str | None]:
    """
    Perform a WHOIS lookup for a domain or IP address.

    Uses the system whois command to retrieve ownership and registration
    information, then parses the output into a structured dictionary.

    Args:
        target: Domain name or IP address to look up.

    Returns:
        Dictionary with parsed WHOIS fields. Contains an 'error' key
        if the lookup failed (e.g., whois is not installed).

    Examples:
        >>> result = whois_lookup("example.com")
        >>> result["registrar"]
        'RESERVED-Internet Assigned Numbers Authority'

    """
    raw: str | None = _run_whois_command(target)
    if raw is None:
        return {
            "target": target,
            "type": "ip" if _is_ip(target) else "domain",
            "error": "WHOIS lookup failed. Ensure 'whois' is installed.",
        }

    parsed: dict[str, str | None] = _parse_whois_output(raw)
    parsed["target"] = target
    parsed["type"] = "ip" if _is_ip(target) else "domain"
    return parsed
