"""DNS record validation functions."""

from typing import Any


def calculate_record_score(
    rtype: str, record_result: dict[str, Any], result: dict[str, list[str]]
) -> int:
    """
    Calculate a health score for a single DNS record type.

    Evaluates DNS records based on their presence, errors, and content,
    applying a scoring system that penalizes issues and missing records.

    Args:
        rtype: DNS record type (e.g., 'A', 'MX', 'TXT', 'CNAME').
        record_result: Dictionary containing record data and potential errors.
                      Expected keys: 'error' (optional), 'records' (optional).
        result: Result dictionary to collect warnings and issues during validation.
               Must contain 'warnings' and 'issues' lists.

    Returns:
        int: Calculated score between 0-100, where:
             - 100: Perfect configuration
             - 80-99: Minor issues (warnings only)
             - 50-79: Significant issues
             - Below 50: Critical issues

    Notes:
        The function delegates record-type specific checks to
        apply_rtype_specific_checks() for further validation.

    """
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
    record_result: dict[str, Any],
    record_score: int,
    result: dict[str, list[str]],
) -> int:
    """
    Apply validation rules specific to each DNS record type.

    Delegates to specialized validation functions based on the record type.

    Args:
        rtype: DNS record type to validate.
        record_result: Dictionary containing the record data to validate.
        record_score: Current score before applying type-specific checks.
        result: Result dictionary for collecting issues and warnings.

    Returns:
        int: Updated score after applying type-specific validations.

    See Also:
        check_mx_priorities: Validates MX record priorities.
        check_txt_records: Validates TXT record content (SPF, DKIM).

    """
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


def check_mx_priorities(
    records: list[str], record_score: int, result: dict[str, list[str]]
) -> int:
    """
    Validate MX record priorities for duplicate entries.

    Checks MX records for duplicate priority values, which can cause
    undetermined mail server selection behavior.

    Args:
        records: List of MX record strings in format "priority mailserver".
                Example: "10 mail.example.com"
        record_score: Current score before validation.
        result: Result dictionary for collecting issues.

    Returns:
        int: Updated score, reduced by 20 points for each duplicate
             priority or malformed record.

    Example:
        >>> result = {"issues": [], "warnings": []}
        >>> check_mx_priorities(["10 mail1.com", "10 mail2.com"], 100, result)
        80
        >>> result["issues"]
        ['Duplicate MX priority: 10']

    """
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


def check_txt_records(
    records: list[str], record_score: int, result: dict[str, list[str]]
) -> int:
    """
    Validate TXT records for email authentication compliance.

    Examines TXT records for SPF (Sender Policy Framework) and DKIM
    (DomainKeys Identified Mail) standards compliance.

    Args:
        records: List of TXT record strings.
        record_score: Current score before validation.
        result: Result dictionary for collecting issues and warnings.

    Returns:
        int: Updated score after applying SPF and DKIM validations.

    See Also:
        check_spf_record: Validates SPF record syntax and requirements.
        check_dkim_record: Validates DKIM record presence of public key.

    """
    for txt in records:
        if txt.startswith("v=spf1"):
            record_score = check_spf_record(txt, record_score, result)
        elif txt.startswith("v=DKIM1"):
            record_score = check_dkim_record(txt, record_score, result)
    return record_score


def check_spf_record(txt: str, record_score: int, result: dict[str, list[str]]) -> int:
    """
    Validate SPF (Sender Policy Framework) record.

    Checks if the SPF record includes a required termination mechanism
    (~all or -all) to specify how to handle unauthorized senders.

    Args:
        txt: SPF record string starting with 'v=spf1'.
        record_score: Current score before validation.
        result: Result dictionary for collecting warnings.

    Returns:
        int: Updated score, reduced by 10 points if missing softfail/hardfail.

    Example:
        >>> result = {"issues": [], "warnings": []}
        >>> check_spf_record("v=spf1 include:spf.example.com", 100, result)
        90
        >>> result["warnings"]
        ['SPF record missing softfail/hardfail']

    """
    if "~all" not in txt and "-all" not in txt:
        record_score -= 10
        result["warnings"].append("SPF record missing softfail/hardfail")
    return record_score


def check_dkim_record(txt: str, record_score: int, result: dict[str, list[str]]) -> int:
    """
    Validate DKIM (DomainKeys Identified Mail) record.

    Verifies that the DKIM record contains a public key (p= tag),
    which is required for email signing and verification.

    Args:
        txt: DKIM record string starting with 'v=DKIM1'.
        record_score: Current score before validation.
        result: Result dictionary for collecting issues.

    Returns:
        int: Updated score, reduced by 20 points if public key is missing.

    Example:
        >>> result = {"issues": [], "warnings": []}
        >>> check_dkim_record("v=DKIM1; k=rsa;", 100, result)
        80
        >>> result["issues"]
        ['DKIM record missing public key']

    """
    if "p=" not in txt:
        record_score -= 20
        result["issues"].append("DKIM record missing public key")
    return record_score


def determine_status(score: int) -> str:
    """
    Determine health status category based on numerical score.

    Maps a numerical score to a human-readable health status.

    Args:
        score: Numerical score (typically 0-100) from DNS validation.

    Returns:
        str: Health status:
             - "healthy": Score >= 80 (good configuration)
             - "degraded": 50 <= Score < 80 (issues need attention)
             - "unhealthy": Score < 50 (critical issues)

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
    Validate MX records for proper configuration.

    Checks MX records for duplicate priorities, which can cause
    unpredictable mail server selection.

    Args:
        mx_records: List of MX record strings in format "priority mailserver".
                   Example: ["10 mail1.example.com", "20 mail2.example.com"]

    Returns:
        Dict[str, Union[bool, List[str]]]: Validation result containing:
            - valid (bool): True if all checks pass
            - issues (List[str]): List of critical issues found
            - warnings (List[str]): List of non-critical warnings (always empty)

    Example:
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
        priority = int(mx.split()[0])
        if priority in priorities:
            validation["valid"] = False
            validation["issues"].append(f"Duplicate priority: {priority}")
        priorities.append(priority)

    return validation


def validate_txt_records(txt_records: list[str]) -> dict[str, bool | list[str]]:
    """
    Validate TXT records for email authentication compliance.

    Checks TXT records for SPF and DKIM compliance, identifying common
    configuration issues.

    Args:
        txt_records: List of TXT record strings to validate.
                    Example: ["v=spf1 include:spf.example.com ~all",
                             "v=DKIM1; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQ..."]

    Returns:
        Dict[str, Union[bool, List[str]]]: Validation result containing:
            - valid (bool): True if all critical checks pass
            - issues (List[str]): List of critical issues (invalid DKIM)
            - warnings (List[str]): List of warnings (SPF missing ~all/-all)

    Example:
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
                validation["warnings"].append("SPF missing softfail/hardfail")
        elif txt.startswith("v=DKIM1") and "p=" not in txt:
            validation["issues"].append("DKIM missing public key")
            validation["valid"] = False

    return validation
