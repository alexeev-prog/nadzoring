# nadzoring/dns_lookup/health.py
"""DNS health check functionality."""

from typing import Any

from nadzoring.dns_lookup.types import DNSResult
from nadzoring.dns_lookup.utils import resolve_with_timer
from nadzoring.dns_lookup.validation import (
    calculate_record_score,
    determine_status,
    validate_mx_records,
    validate_txt_records,
)


def health_check_dns(domain: str, nameserver: str | None = None) -> dict[str, Any]:
    """Perform comprehensive DNS health check."""
    result: dict[str, Any] = {
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
            record_score = calculate_record_score(rtype, record_result, result)
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
) -> dict[str, Any]:
    """Comprehensive DNS check."""
    if record_types is None:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]

    results: dict[str, Any] = {
        "domain": domain,
        "records": {},
        "errors": {},
        "response_times": {},
        "validations": {},
    }

    for record_type in record_types:
        record_result = resolve_with_timer(domain, record_type, nameserver)

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
