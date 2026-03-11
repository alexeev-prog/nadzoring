"""
DNS record validation functions.

This module is split into small, single-responsibility validators:

- :func:`calculate_record_score` — score one record type for a health check
- :func:`validate_mx_records` — validate MX priority uniqueness
- :func:`validate_txt_records` — validate SPF / DKIM TXT records
- :func:`determine_status` — map a numeric score to a status label

Each validator returns a plain dict or primitive; none raise exceptions.

Typical usage via :mod:`nadzoring.dns_lookup.health`::

    from nadzoring.dns_lookup.validation import (
        validate_mx_records,
        validate_txt_records,
        determine_status,
    )

    mx_result = validate_mx_records(["10 mail.example.com", "20 backup.example.com"])
    print(mx_result["valid"])  # True
    print(mx_result["issues"])  # []

    status = determine_status(85)  # "healthy"

"""

from typing import Any

_SCORE_HEALTHY = 80
_SCORE_DEGRADED = 50

_STATUS_HEALTHY = "healthy"
_STATUS_DEGRADED = "degraded"
_STATUS_UNHEALTHY = "unhealthy"


def determine_status(score: int) -> str:
    """
    Map a numeric health score to a status label.

    Thresholds:

    - ``score >= 80`` → ``"healthy"``
    - ``score >= 50`` → ``"degraded"``
    - ``score < 50``  → ``"unhealthy"``

    Args:
        score: Numeric score in the range 0-100.

    Returns:
        Status label string.

    Examples:
        >>> determine_status(85)
        'healthy'
        >>> determine_status(65)
        'degraded'
        >>> determine_status(30)
        'unhealthy'

    """
    if score >= _SCORE_HEALTHY:
        return _STATUS_HEALTHY
    if score >= _SCORE_DEGRADED:
        return _STATUS_DEGRADED
    return _STATUS_UNHEALTHY


_MX_DUPLICATE_PENALTY = 20
_MX_FORMAT_PENALTY = 20


def _parse_mx_priority(mx: str) -> int | None:
    """
    Parse the numeric priority from an MX record string.

    Args:
        mx: MX record string in ``"priority mailserver"`` format.

    Returns:
        Integer priority, or ``None`` when the format is invalid.

    """
    try:
        return int(mx.split(maxsplit=1)[0])
    except (IndexError, ValueError):
        return None


def validate_mx_records(
    mx_records: list[str],
) -> dict[str, bool | list[str]]:
    """
    Validate MX records for duplicate priority values.

    Args:
        mx_records: MX record strings in ``"priority mailserver"`` format.

    Returns:
        Dict with ``"valid"`` (bool), ``"issues"`` (list[str]), and
        ``"warnings"`` (list[str]) keys.

    Examples:
        Valid records::

            result = validate_mx_records(
                ["10 mail.example.com", "20 backup.example.com"]
            )
            assert result["valid"] is True
            assert result["issues"] == []

        Duplicate priorities::

            result = validate_mx_records(
                ["10 mail1.example.com", "10 mail2.example.com"]
            )
            assert result["valid"] is False
            assert "Duplicate priority: 10" in result["issues"]

    """
    validation: dict[str, bool | list[str]] = {
        "valid": True,
        "issues": [],
        "warnings": [],
    }

    seen_priorities: list[int] = []

    for mx in mx_records:
        priority: int | None = _parse_mx_priority(mx)

        if priority is None:
            validation["valid"] = False
            issues_list = validation["issues"]
            if isinstance(issues_list, list):
                issues_list.append(f"Invalid MX record format: {mx}")
            continue

        if priority in seen_priorities:
            validation["valid"] = False
            issues_list = validation["issues"]
            if isinstance(issues_list, list):
                issues_list.append(f"Duplicate priority: {priority}")
        else:
            seen_priorities.append(priority)

    return validation


_SPF_PREFIX = "v=spf1"
_DKIM_PREFIX = "v=DKIM1"
_SPF_SOFTFAIL = "~all"
_SPF_HARDFAIL = "-all"
_DKIM_KEY_TAG = "p="

_SPF_MISSING_TERMINATOR_PENALTY = 10
_DKIM_MISSING_KEY_PENALTY = 20


def _validate_spf(txt: str) -> tuple[list[str], list[str]]:
    """Check a single SPF record; return (issues, warnings)."""
    issues: list[str] = []
    warnings: list[str] = []
    if _SPF_SOFTFAIL not in txt and _SPF_HARDFAIL not in txt:
        warnings.append("SPF missing softfail/hardfail (~all or -all)")
    return issues, warnings


def _validate_dkim(txt: str) -> tuple[list[str], list[str]]:
    """Check a single DKIM record; return (issues, warnings)."""
    issues: list[str] = []
    warnings: list[str] = []
    if _DKIM_KEY_TAG not in txt:
        issues.append("DKIM missing public key (p= tag)")
    return issues, warnings


def validate_txt_records(
    txt_records: list[str],
) -> dict[str, bool | list[str]]:
    """
    Validate TXT records for SPF and DKIM compliance.

    Checks:

    - **SPF** — warns when ``~all`` or ``-all`` mechanism is absent
    - **DKIM** — marks invalid when the ``p=`` public-key tag is missing

    Args:
        txt_records: List of TXT record strings.

    Returns:
        Dict with ``"valid"`` (bool), ``"issues"`` (list[str]), and
        ``"warnings"`` (list[str]) keys.

    Examples:
        SPF without terminator::

            result = validate_txt_records(["v=spf1 include:spf.example.com"])
            assert result["valid"] is True  # SPF warning only
            assert result["warnings"] != []

        Missing DKIM key::

            result = validate_txt_records(["v=DKIM1; k=rsa;"])
            assert result["valid"] is False
            assert result["issues"] != []

        All good::

            result = validate_txt_records(
                [
                    "v=spf1 include:spf.example.com ~all",
                    "v=DKIM1; k=rsa; p=MIIBIjANBg...",
                ]
            )
            assert result["valid"] is True
            assert result["issues"] == []

    """
    validation: dict[str, bool | list[str]] = {
        "valid": True,
        "issues": [],
        "warnings": [],
    }

    for txt in txt_records:
        if txt.startswith(_SPF_PREFIX):
            issues, warnings = _validate_spf(txt)
        elif txt.startswith(_DKIM_PREFIX):
            issues, warnings = _validate_dkim(txt)
        else:
            continue

        issues_list = validation["issues"]
        if isinstance(issues_list, list):
            issues_list.extend(issues)
        warnings_list = validation["warnings"]
        if isinstance(warnings_list, list):
            warnings_list.extend(warnings)
        if issues:
            validation["valid"] = False

    return validation


_ERROR_MISSING_PENALTY = 30
_ERROR_QUERY_PENALTY = 50
_EMPTY_RECORDS_PENALTY = 20


def calculate_record_score(
    rtype: str,
    record_result: dict[str, Any],
    accumulator: dict[str, list[str]],
) -> int:
    """
    Calculate a health score for a single DNS record type.

    Starts at 100 and deducts points for errors, missing records, or
    type-specific issues.  Side-effects: appends messages to
    ``accumulator["issues"]`` and ``accumulator["warnings"]``.

    Args:
        rtype: DNS record type (e.g. ``"A"``, ``"MX"``, ``"TXT"``).
        record_result: Dict with optional ``"error"`` and ``"records"``
            keys (a :class:`~.types.DNSResult`).
        accumulator: Dict with ``"issues"`` and ``"warnings"`` lists
            that are updated in-place.

    Returns:
        Score between 0 and 100.

    """
    score = 100

    error: str | None = record_result.get("error")
    if error:
        if error.startswith("No ") and error.endswith("records"):
            score -= _ERROR_MISSING_PENALTY
            accumulator["warnings"].append(f"No {rtype} records found")
        else:
            score -= _ERROR_QUERY_PENALTY
            accumulator["issues"].append(f"{rtype} record error: {error}")
    elif not record_result.get("records"):
        score -= _EMPTY_RECORDS_PENALTY
        accumulator["warnings"].append(f"Empty {rtype} records")

    score = _apply_type_specific_checks(rtype, record_result, score, accumulator)
    return max(0, score)


def _apply_type_specific_checks(
    rtype: str,
    record_result: dict[str, Any],
    score: int,
    accumulator: dict[str, list[str]],
) -> int:
    """
    Apply record-type-specific scoring rules.

    Args:
        rtype: DNS record type.
        record_result: Dict with record data.
        score: Current score before type-specific adjustments.
        accumulator: Issues/warnings accumulator updated in-place.

    Returns:
        Adjusted score.

    """
    records: list[str] | None = record_result.get("records")
    if not records:
        return score

    if rtype == "MX":
        return _score_mx(records, score, accumulator)
    if rtype == "TXT":
        return _score_txt(records, score, accumulator)
    return score


def _score_mx(
    records: list[str],
    score: int,
    accumulator: dict[str, list[str]],
) -> int:
    """Deduct points for duplicate MX priorities or malformed records."""
    seen: list[int] = []
    for mx in records:
        priority: int | None = _parse_mx_priority(mx)
        if priority is None:
            score -= _MX_FORMAT_PENALTY
            accumulator["issues"].append(f"Invalid MX record format: {mx}")
        elif priority in seen:
            score -= _MX_DUPLICATE_PENALTY
            accumulator["issues"].append(f"Duplicate MX priority: {priority}")
        else:
            seen.append(priority)
    return score


def _score_txt(
    records: list[str],
    score: int,
    accumulator: dict[str, list[str]],
) -> int:
    """Deduct points for SPF / DKIM issues in TXT records."""
    for txt in records:
        if txt.startswith(_SPF_PREFIX):
            if _SPF_SOFTFAIL not in txt and _SPF_HARDFAIL not in txt:
                score -= _SPF_MISSING_TERMINATOR_PENALTY
                accumulator["warnings"].append("SPF record missing softfail/hardfail")
        elif txt.startswith(_DKIM_PREFIX) and _DKIM_KEY_TAG not in txt:
            score -= _DKIM_MISSING_KEY_PENALTY
            accumulator["issues"].append("DKIM record missing public key")
    return score
