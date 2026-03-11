"""DNS health check functionality for comprehensive domain DNS evaluation."""

from typing import Any

from nadzoring.dns_lookup.types import DNSResult, RecordType
from nadzoring.dns_lookup.utils import resolve_with_timer
from nadzoring.dns_lookup.validation import (
    calculate_record_score,
    determine_status,
    validate_mx_records,
    validate_txt_records,
)

_HEALTH_RECORD_TYPES: list[RecordType] = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
_DEFAULT_CHECK_TYPES: list[RecordType] = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]


class HealthCheckResult(dict[str, Any]):
    """
    Comprehensive DNS health check result.

    A dict subclass carrying overall health score, status, and a per-record-type
    score breakdown.

    Attributes:
        domain: Domain name that was checked.
        score: Overall health score (0-100).
        status: Health status — ``"healthy"``, ``"degraded"``, or ``"unhealthy"``.
        issues: Critical issues found during validation.
        warnings: Non-critical warnings found during validation.
        record_scores: Map of record type to its individual score.

    """

    domain: str
    score: int
    status: str
    issues: list[str]
    warnings: list[str]
    record_scores: dict[str, int]


class DetailedCheckResult(dict[str, Any]):
    """
    Detailed DNS check result with per-record-type information.

    A dict subclass providing granular information about each queried record
    type including resolved records, response times, errors, and optional
    validation results.

    Attributes:
        domain: Domain name that was checked.
        records: Map of record type to list of resolved record strings.
        errors: Map of record type to error message when resolution failed.
        response_times: Map of record type to response time in milliseconds.
        validations: Validation results for MX and TXT records when requested.

    """

    domain: str
    records: dict[str, list[str]]
    errors: dict[str, str]
    response_times: dict[str, float | None]
    validations: dict[str, dict[str, bool | list[str]]]


def health_check_dns(domain: str, nameserver: str | None = None) -> HealthCheckResult:
    """
    Perform a comprehensive DNS health check with scoring.

    Evaluates ``A``, ``AAAA``, ``MX``, ``NS``, ``TXT``, and ``CNAME`` records,
    computes per-type scores, and derives an overall health score and status.

    ``CNAME`` at the apex (non-subdomain) is stored as 100 but excluded from
    the score average, since the record type is only meaningful for subdomains.

    Args:
        domain: Domain name to check (e.g. ``"example.com"``).
        nameserver: Optional nameserver IP. ``None`` uses the system default.

    Returns:
        :class:`HealthCheckResult` dict with ``domain``, ``score``, ``status``,
        ``issues``, ``warnings``, and ``record_scores`` keys.

    Examples:
        >>> result = health_check_dns("example.com")
        >>> print(result["score"], result["status"])
        >>> for rtype, score in result["record_scores"].items():
        ...     print(f"  {rtype}: {score}")

    """
    result: HealthCheckResult = {
        "domain": domain,
        "score": 0,
        "status": "healthy",
        "issues": [],
        "warnings": [],
        "record_scores": {},
    }

    is_subdomain: bool = len(domain.split(".")) > 2
    total_score = 0
    record_count = 0

    for rtype in _HEALTH_RECORD_TYPES:
        if rtype == "CNAME" and not is_subdomain:
            result["record_scores"][rtype] = 100
            continue

        record_result: DNSResult = resolve_with_timer(domain, rtype, nameserver)
        record_score: int = max(
            0, calculate_record_score(rtype, dict(record_result), result)
        )

        result["record_scores"][rtype] = record_score
        total_score += record_score
        record_count += 1

    result["score"] = total_score // record_count if record_count > 0 else 0
    result["status"] = determine_status(result["score"])

    return result


def check_dns(
    domain: str,
    nameserver: str | None = None,
    record_types: list[RecordType] | None = None,
    *,
    validate_mx: bool = False,
    validate_txt: bool = False,
) -> DetailedCheckResult:
    """
    Perform a comprehensive DNS check with detailed per-record information.

    Queries the specified record types and optionally validates MX priorities
    and SPF/DKIM TXT records.

    Args:
        domain: Domain name to check (e.g. ``"example.com"``).
        nameserver: Optional nameserver IP. ``None`` uses the system default.
        record_types: Record types to query. Defaults to
            ``["A", "AAAA", "MX", "NS", "TXT", "CNAME"]``.
        validate_mx: Validate MX record priorities when ``True``.
        validate_txt: Validate SPF and DKIM in TXT records when ``True``.

    Returns:
        :class:`DetailedCheckResult` dict with ``domain``, ``records``,
        ``errors``, ``response_times``, and ``validations`` keys.

    Examples:
        >>> result = check_dns(
        ...     "example.com",
        ...     record_types=["MX", "TXT"],
        ...     validate_mx=True,
        ...     validate_txt=True,
        ... )
        >>> result["validations"].get("mx", {}).get("valid")
        True

    """
    if record_types is None:
        record_types = list(_DEFAULT_CHECK_TYPES)

    results: DetailedCheckResult = {
        "domain": domain,
        "records": {},
        "errors": {},
        "response_times": {},
        "validations": {},
    }

    for record_type in record_types:
        record_result: DNSResult = resolve_with_timer(domain, record_type, nameserver)

        if record_result.get("records"):
            results["records"][record_type] = record_result["records"]
            results["response_times"][record_type] = record_result["response_time"]

            if validate_mx and record_type == "MX":
                results["validations"]["mx"] = validate_mx_records(
                    record_result["records"],
                )
            elif validate_txt and record_type == "TXT":
                results["validations"]["txt"] = validate_txt_records(
                    record_result["records"],
                )

        if record_result.get("error"):
            results["errors"][record_type] = record_result["error"]

    return results
