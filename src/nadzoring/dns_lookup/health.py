"""
DNS health check functionality for comprehensive domain DNS evaluation.

This module provides functions to perform health checks on DNS configurations,
including scoring, validation, and detailed analysis of various record types.
"""

from typing import Any

from nadzoring.dns_lookup.types import DNSResult
from nadzoring.dns_lookup.utils import resolve_with_timer
from nadzoring.dns_lookup.validation import (
    calculate_record_score,
    determine_status,
    validate_mx_records,
    validate_txt_records,
)


class HealthCheckResult(dict[str, Any]):
    """
    Comprehensive DNS health check result.

    Contains overall health score, status, and detailed breakdown by record type.

    Attributes:
        domain: The domain name that was checked.
        score: Overall health score (0-100).
        status: Health status ('healthy', 'degraded', 'unhealthy').
        issues: List of critical issues found.
        warnings: List of warnings found.
        record_scores: Dictionary mapping record types to their individual scores.

    """

    domain: str
    score: int
    status: str
    issues: list[str]
    warnings: list[str]
    record_scores: dict[str, int]


class DetailedCheckResult(dict[str, Any]):
    """
    Detailed DNS check result with per-record type information.

    Provides granular information about each queried record type including
    actual records, response times, errors, and validations.

    Attributes:
        domain: The domain name that was checked.
        records: Dictionary mapping record types to their resolved records.
        errors: Dictionary mapping record types to any errors encountered.
        response_times: Dictionary mapping record types to response times in ms.
        validations: Dictionary containing validation results for MX and TXT records.

    """

    domain: str
    records: dict[str, list[str]]
    errors: dict[str, str]
    response_times: dict[str, float | None]
    validations: dict[str, dict[str, bool | list[str]]]


def health_check_dns(domain: str, nameserver: str | None = None) -> HealthCheckResult:
    """
    Perform a comprehensive DNS health check with scoring.

    Evaluates the health of a domain's DNS configuration by checking multiple
    record types, calculating individual scores, and producing an overall
    health score and status.

    Args:
        domain: Domain name to check (e.g., "example.com").
        nameserver: Optional specific nameserver IP to use for queries.
                   If None, uses system default resolvers.

    Returns:
        HealthCheckResult: Dictionary containing health check results:
            - domain: The domain that was checked
            - score: Overall health score (0-100)
            - status: Health status ('healthy', 'degraded', 'unhealthy')
            - issues: List of critical issues found during checks
            - warnings: List of non-critical warnings found
            - record_scores: Dict with scores for each record type:
                * A: IPv4 address records score
                * AAAA: IPv6 address records score
                * MX: Mail exchange records score
                * NS: Nameserver records score
                * TXT: Text records score
                * CNAME: Canonical name records score (if applicable)

    Examples:
        >>> # Basic health check
        >>> result = health_check_dns("example.com")
        >>> print(f"Health score: {result['score']} - {result['status']}")
        >>> for rtype, score in result["record_scores"].items():
        ...     print(f"  {rtype}: {score}")

        >>> # Using specific nameserver
        >>> result = health_check_dns("example.com", nameserver="8.8.8.8")
        >>> if result["issues"]:
        ...     print("Issues found:", result["issues"])

    Notes:
        - Checks all major record types: A, AAAA, MX, NS, TXT, CNAME
        - CNAME records are only scored for subdomains (as per DNS standards)
        - Scores are calculated using validation rules from validation module
        - The final score is the average of all non-CNAME record scores
        - Status is determined by the overall score:
            * >= 80: healthy
            * 50-79: degraded
            * < 50: unhealthy

    """
    result: HealthCheckResult = {
        "domain": domain,
        "score": 0,
        "status": "healthy",
        "issues": [],
        "warnings": [],
        "record_scores": {},
    }

    total_score = 0
    record_count = 0
    is_subdomain: bool = len(domain.split(".")) > 2

    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        record_result: DNSResult = resolve_with_timer(domain, rtype, nameserver)

        if rtype == "CNAME" and not is_subdomain:
            if record_result.get("records"):
                record_score = 100
            else:
                record_score = 100
                continue
        else:
            record_score: int = calculate_record_score(rtype, record_result, result)
            total_score += record_score
            record_count += 1

        result["record_scores"][rtype] = max(0, record_score)

    result["score"] = total_score // record_count if record_count > 0 else 0
    result["status"] = determine_status(result["score"])

    return result


def check_dns(
    domain: str,
    nameserver: str | None = None,
    record_types: list[str] | None = None,
    *,
    validate_mx: bool = False,
    validate_txt: bool = False,
) -> DetailedCheckResult:
    """
    Perform a comprehensive DNS check with detailed per-record information.

    Queries specified DNS record types for a domain and returns detailed
    information including actual records, response times, errors, and optional
    validation results for MX and TXT records.

    Args:
        domain: Domain name to check (e.g., "example.com").
        nameserver: Optional specific nameserver IP to use for queries.
                   If None, uses system default resolvers.
        record_types: List of DNS record types to query.
                     If None, defaults to ["A", "AAAA", "MX", "NS", "TXT", "CNAME"].
        validate_mx: If True, perform additional validation on MX records
                    (checks for duplicate priorities).
        validate_txt: If True, perform additional validation on TXT records
                     (checks SPF and DKIM compliance).

    Returns:
        DetailedCheckResult: Dictionary containing detailed check results:
            - domain: The domain that was checked
            - records: Dict mapping record types to lists of resolved records
            - errors: Dict mapping record types to error messages (if any)
            - response_times: Dict mapping record types to response times in ms
            - validations: Dict containing validation results:
                * mx: MX validation result (if validate_mx=True and MX records exist)
                * txt: TXT validation result (if validate_txt=True, TXT records exist)

    Examples:
        >>> # Basic check with default record types
        >>> result = check_dns("example.com")
        >>> if "A" in result["records"]:
        ...     print(f"A records: {result['records']['A']}")

        >>> # Check specific record types with validation
        >>> result = check_dns(
        ...     "example.com",
        ...     record_types=["MX", "TXT"],
        ...     validate_mx=True,
        ...     validate_txt=True,
        ... )
        >>> if "validations" in result:
        ...     mx_valid = result["validations"].get("mx", {})
        ...     if not mx_valid.get("valid", True):
        ...         print("MX issues:", mx_valid.get("issues", []))

        >>> # Check with custom nameserver
        >>> result = check_dns(
        ...     "example.com", nameserver="1.1.1.1", record_types=["A", "AAAA"]
        ... )
        >>> for rtype, time in result["response_times"].items():
        ...     print(f"{rtype} resolved in {time}ms")

    Notes:
        - Response times are in milliseconds, rounded to 2 decimal places
        - Records without trailing dots for consistency
        - MX validation checks for duplicate priorities
        - TXT validation checks SPF for missing all and DKIM for missing public key
        - Errors are recorded per record type if resolution fails

    """
    if record_types is None:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]

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
