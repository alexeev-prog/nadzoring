# nadzoring/dns_lookup/validation.py
"""DNS record validation functions."""

from typing import Any


def calculate_record_score(rtype: str, record_result: dict, result: dict) -> int:
    """Calculate score for a single DNS record type."""
    record_score = 100

    if record_result.get("error"):
        if "No " in record_result["error"] and record_result["error"].endswith(
            "records"
        ):
            record_score -= 30
            result["warnings"].append(f"No {rtype} records found")
        else:
            record_score -= 50
            result["issues"].append(f"{rtype} record error: {record_result['error']}")
    elif not record_result.get("records"):
        record_score -= 20
        result["warnings"].append(f"Empty {rtype} records")

    return apply_rtype_specific_checks(rtype, record_result, record_score, result)


def apply_rtype_specific_checks(
    rtype: str,
    record_result: dict,
    record_score: int,
    result: dict,
) -> int:
    """Apply record-type specific validation rules."""
    if rtype == "MX" and record_result.get("records"):
        record_score = check_mx_priorities(
            record_result["records"],
            record_score,
            result,
        )
    elif rtype == "TXT" and record_result.get("records"):
        record_score = check_txt_records(
            record_result["records"],
            record_score,
            result,
        )
    return record_score


def check_mx_priorities(records: list, record_score: int, result: dict) -> int:
    """Check MX records for duplicate priorities."""
    priorities: list[int] = []
    for mx in records:
        try:
            priority = int(mx.split()[0])
            if priority in priorities:
                record_score -= 20
                result["issues"].append(f"Duplicate MX priority: {priority}")
            priorities.append(priority)
        except (IndexError, ValueError):
            record_score -= 20
            result["issues"].append(f"Invalid MX record format: {mx}")
    return record_score


def check_txt_records(records: list, record_score: int, result: dict) -> int:
    """Check TXT records for SPF and DKIM compliance."""
    for txt in records:
        if txt.startswith("v=spf1"):
            record_score = check_spf_record(txt, record_score, result)
        elif txt.startswith("v=DKIM1"):
            record_score = check_dkim_record(txt, record_score, result)
    return record_score


def check_spf_record(txt: str, record_score: int, result: dict) -> int:
    """Validate SPF record."""
    if "~all" not in txt and "-all" not in txt:
        record_score -= 10
        result["warnings"].append("SPF record missing softfail/hardfail")
    return record_score


def check_dkim_record(txt: str, record_score: int, result: dict) -> int:
    """Validate DKIM record."""
    if "p=" not in txt:
        record_score -= 20
        result["issues"].append("DKIM record missing public key")
    return record_score


def determine_status(score: int) -> str:
    """Determine health status based on score."""
    if score >= 80:
        return "healthy"
    if score >= 50:
        return "degraded"
    return "unhealthy"


def validate_mx_records(mx_records: list[str]) -> dict[str, Any]:
    """Validate MX records."""
    validation: dict[str, Any] = {
        "valid": True,
        "issues": [],
        "warnings": [],
    }

    priorities: list[int] = []
    for mx in mx_records:
        priority = int(mx.split()[0])
        if priority in priorities:
            validation["valid"] = False
            validation["issues"].append(f"Duplicate priority: {priority}")
        priorities.append(priority)

    return validation


def validate_txt_records(txt_records: list[str]) -> dict[str, Any]:
    """Validate TXT records (SPF, DKIM)."""
    validation: dict[str, Any] = {
        "valid": True,
        "issues": [],
        "warnings": [],
    }

    for txt in txt_records:
        if txt.startswith("v=spf1"):
            if "~all" not in txt and "-all" not in txt:
                validation["warnings"].append("SPF missing softfail/hardfail")
        elif txt.startswith("v=DKIM1") and "p=" not in txt:
            validation["issues"].append("DKIM missing public key")

    return validation
