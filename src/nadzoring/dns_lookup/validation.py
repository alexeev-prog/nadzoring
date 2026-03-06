"""DNS record validation functions."""

from typing import Any


def calculate_record_score(
    rtype: str,
    record_result: dict[str, Any],
    result: dict[str, list[str]],
) -> int:
    """
    Calculate a health score for a single DNS record type.

    Starts at 100 and deducts points for errors, missing records, or
    type-specific issues.

    Args:
        rtype: DNS record type (e.g. ``"A"``, ``"MX"``, ``"TXT"``).
        record_result: Dict with optional ``"error"`` and ``"records"`` keys.
        result: Accumulator dict with ``"warnings"`` and ``"issues"`` lists
            updated in-place.

    Returns:
        Score between 0 and 100.

    """
    record_score = 100

    if record_result.get("error"):
        error = record_result["error"]
        if "No " in error and error.endswith("records"):
            record_score -= 30
            result["warnings"].append(f"No {rtype} records found")
        else:
            record_score -= 50
            result["issues"].append(f"{rtype} record error: {error}")
    elif not record_result.get("records"):
        record_score -= 20
        result["warnings"].append(f"Empty {rtype} records")

    return _apply_rtype_specific_checks(rtype, record_result, record_score, result)


def _apply_rtype_specific_checks(
    rtype: str,
    record_result: dict[str, Any],
    record_score: int,
    result: dict[str, list[str]],
) -> int:
    """
    Apply validation rules specific to each DNS record type.

    Args:
        rtype: DNS record type to validate.
        record_result: Dict containing the record data to validate.
        record_score: Current score before applying type-specific checks.
        result: Accumulator dict for issues and warnings.

    Returns:
        Updated score after applying type-specific validations.

    """
    records = record_result.get("records")
    if not records:
        return record_score

    if rtype == "MX":
        return _check_mx_priorities(records, record_score, result)
    if rtype == "TXT":
        return _check_txt_records(records, record_score, result)
    return record_score


def _check_mx_priorities(
    records: list[str],
    record_score: int,
    result: dict[str, list[str]],
) -> int:
    """
    Deduct points for duplicate MX priorities or malformed records.

    Args:
        records: MX record strings in ``"priority mailserver"`` format.
        record_score: Current score.
        result: Accumulator dict for issues.

    Returns:
        Updated score; reduced by 20 for each duplicate or malformed entry.

    Examples:
        >>> r = {"issues": [], "warnings": []}
        >>> _check_mx_priorities(["10 mail1.com", "10 mail2.com"], 100, r)
        80

    """
    priorities: list[int] = []
    for mx in records:
        try:
            priority = int(mx.split()[0])
        except (IndexError, ValueError):
            record_score -= 20
            result["issues"].append(f"Invalid MX record format: {mx}")
            continue

        if priority in priorities:
            record_score -= 20
            result["issues"].append(f"Duplicate MX priority: {priority}")
        else:
            priorities.append(priority)

    return record_score


def _check_txt_records(
    records: list[str],
    record_score: int,
    result: dict[str, list[str]],
) -> int:
    """
    Validate TXT records for SPF and DKIM compliance.

    Args:
        records: List of TXT record strings.
        record_score: Current score.
        result: Accumulator dict for issues and warnings.

    Returns:
        Updated score after SPF and DKIM checks.

    """
    for txt in records:
        if txt.startswith("v=spf1"):
            record_score = _check_spf_record(txt, record_score, result)
        elif txt.startswith("v=DKIM1"):
            record_score = _check_dkim_record(txt, record_score, result)
    return record_score


def _check_spf_record(
    txt: str,
    record_score: int,
    result: dict[str, list[str]],
) -> int:
    """
    Deduct points when an SPF record lacks a ``~all`` or ``-all`` mechanism.

    Args:
        txt: SPF record string starting with ``"v=spf1"``.
        record_score: Current score.
        result: Accumulator dict for warnings.

    Returns:
        Updated score; reduced by 10 when termination mechanism is absent.

    Examples:
        >>> r = {"issues": [], "warnings": []}
        >>> _check_spf_record("v=spf1 include:spf.example.com", 100, r)
        90

    """
    if "~all" not in txt and "-all" not in txt:
        record_score -= 10
        result["warnings"].append("SPF record missing softfail/hardfail")
    return record_score


def _check_dkim_record(
    txt: str,
    record_score: int,
    result: dict[str, list[str]],
) -> int:
    """
    Deduct points when a DKIM record is missing the ``p=`` public-key tag.

    Args:
        txt: DKIM record string starting with ``"v=DKIM1"``.
        record_score: Current score.
        result: Accumulator dict for issues.

    Returns:
        Updated score; reduced by 20 when the public key is absent.

    Examples:
        >>> r = {"issues": [], "warnings": []}
        >>> _check_dkim_record("v=DKIM1; k=rsa;", 100, r)
        80

    """
    if "p=" not in txt:
        record_score -= 20
        result["issues"].append("DKIM record missing public key")
    return record_score


def determine_status(score: int) -> str:
    """
    Map a numeric health score to a status label.

    Args:
        score: Numeric score in the range 0-100.

    Returns:
        ``"healthy"`` for score ≥ 80, ``"degraded"`` for 50-79, or
        ``"unhealthy"`` for scores below 50.

    Examples:
        >>> determine_status(85)
        'healthy'
        >>> determine_status(65)
        'degraded'
        >>> determine_status(30)
        'unhealthy'

    """
    if score >= 80:
        return "healthy"
    if score >= 50:
        return "degraded"
    return "unhealthy"


def validate_mx_records(mx_records: list[str]) -> dict[str, bool | list[str]]:
    """
    Validate MX records for duplicate priority values.

    Args:
        mx_records: MX record strings in ``"priority mailserver"`` format.

    Returns:
        Dict with ``"valid"`` (bool), ``"issues"`` (list), and
        ``"warnings"`` (list) keys.

    Examples:
        >>> validate_mx_records(["10 mail1.com", "10 mail2.com"])
        {'valid': False, 'issues': ['Duplicate priority: 10'], 'warnings': []}

    """
    validation: dict[str, bool | list[str]] = {
        "valid": True,
        "issues": [],
        "warnings": [],
    }

    priorities: list[int] = []
    for mx in mx_records:
        try:
            priority = int(mx.split()[0])
        except (IndexError, ValueError):
            validation["valid"] = False
            # type: ignore[union-attr]
            validation["issues"].append(f"Invalid MX record format: {mx}")
            continue

        if priority in priorities:
            validation["valid"] = False
            # type: ignore[union-attr]
            validation["issues"].append(f"Duplicate priority: {priority}")
        else:
            priorities.append(priority)

    return validation


def validate_txt_records(txt_records: list[str]) -> dict[str, bool | list[str]]:
    """
    Validate TXT records for SPF and DKIM compliance.

    Checks for SPF (missing ``~all``/``-all``) and DKIM (missing ``p=`` key).

    Args:
        txt_records: List of TXT record strings.

    Returns:
        Dict with ``"valid"`` (bool), ``"issues"`` (list), and
        ``"warnings"`` (list) keys.

    Examples:
        >>> result = validate_txt_records(["v=spf1 include:spf.com"])
        >>> result["valid"]
        True
        >>> result["warnings"]
        ['SPF missing softfail/hardfail']

    """
    validation: dict[str, bool | list[str]] = {
        "valid": True,
        "issues": [],
        "warnings": [],
    }

    for txt in txt_records:
        if txt.startswith("v=spf1"):
            if "~all" not in txt and "-all" not in txt:
                validation["warnings"].append(
                    # type: ignore[union-attr]
                    "SPF missing softfail/hardfail"
                )
        elif txt.startswith("v=DKIM1") and "p=" not in txt:
            # type: ignore[union-attr]
            validation["issues"].append("DKIM missing public key")
            validation["valid"] = False

    return validation
