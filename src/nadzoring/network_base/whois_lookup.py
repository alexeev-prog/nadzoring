"""WHOIS information lookup for domains and IP addresses."""

import shlex
from ipaddress import ip_address
from logging import Logger
from platform import system
from subprocess import PIPE, CalledProcessError, check_output
from typing import Literal

import whois  # type: ignore

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


def _run_whois_command(target: str) -> str:
    """Execute the system whois command for the given target.

    Args:
        target: Domain or IP address to query.

    Returns:
        Raw WHOIS output string.

    Raises:
        FileNotFoundError: The 'whois' command is not installed.
        TimeoutError: The WHOIS query exceeded the timeout period.
        CalledProcessError: The whois command returned a non-zero exit code.
    """
    os_name: str = system()
    encoding: Literal["cp866", "utf-8"] = "cp866" if os_name == "Windows" else "utf-8"

    return check_output(
        shlex.split(f"whois {target}"),
        stderr=PIPE,
        timeout=15,
    ).decode(encoding, errors="replace")


def _parse_whois_output(raw: str) -> dict[str, str | None]:
    """Parse raw WHOIS text into a structured dictionary.

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


def _format_whois_value(value: object) -> str:
    """Convert python-whois values into display-friendly strings."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(_format_whois_value(item) for item in value)
    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


def whois_domain_lookup(domain: str) -> list[dict[str, str]]:
    """Perform a structured WHOIS lookup for a domain using python-whois.

    Args:
        domain: Domain name to look up.

    Returns:
        List of field/value dictionaries formatted for CLI output handling.
    """
    try:
        info = whois.whois(domain)
    except Exception as e:
        return [{"error": f"Error fetching WHOIS for {domain}: {e}"}]

    return [{"Field": str(key), "Value": _format_whois_value(value)} for key, value in info.items()]


def whois_lookup(target: str) -> dict[str, str | None]:
    """Perform a WHOIS lookup for a domain or IP address.

    Uses the system whois command to retrieve ownership and registration
    information, then parses the output into a structured dictionary.

    The returned dictionary's ``"error"`` key, if present, contains one of
    the literals defined in :data:`nadzoring.network_base.errors.WHOISError`.

    Args:
        target: Domain name or IP address to look up.

    Returns:
        Dictionary with parsed WHOIS fields. Contains an 'error' key
        if the lookup failed (e.g., whois is not installed).
    """
    target_type: str = "ip" if _is_ip(target) else "domain"

    try:
        raw: str = _run_whois_command(target)
    except FileNotFoundError:
        logger.exception("WHOIS command not found. Please install whois.")
        return {
            "target": target,
            "type": target_type,
            "error": "Command not found",
        }
    except TimeoutError:
        logger.exception("WHOIS lookup timed out for %s", target)
        return {
            "target": target,
            "type": target_type,
            "error": "Query timeout",
        }
    except CalledProcessError as e:
        # whois command returned non-zero exit code
        # This often means the target doesn't exist or isn't registered
        logger.exception("WHOIS lookup failed for %s with exit code %d", target, e.returncode)

        # Try to extract meaningful error from stderr
        stderr = e.stderr.decode() if e.stderr else ""
        if "No match" in stderr or "NOT FOUND" in stderr:
            return {
                "target": target,
                "type": target_type,
                "error": "No information found",
            }
        return {
            "target": target,
            "type": target_type,
            "error": "No information found",  # Default to no info for other errors
        }

    parsed: dict[str, str | None] = _parse_whois_output(raw)
    parsed["target"] = target
    parsed["type"] = target_type

    whois_fields: dict[str, str | None] = {k: parsed[k] for k in _WHOIS_FIELD_MAP}
    if not any(whois_fields.values()):
        parsed["error"] = "No information found"

    return parsed
