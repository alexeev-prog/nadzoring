# nadzoring/dns_lookup/poisoning.py
"""DNS poisoning."""

import ipaddress
from collections import Counter
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Literal

from nadzoring.dns_lookup.types import DNSResult, PoisoningCheckResult
from nadzoring.dns_lookup.utils import get_public_dns_servers, resolve_with_timer
from nadzoring.logger import get_logger

logger = get_logger(__name__)


SERVER_NAMES: dict[str, str] = {
    "8.8.8.8": "Google",
    "8.8.4.4": "Google",
    "1.1.1.1": "Cloudflare",
    "1.0.0.1": "Cloudflare",
    "208.67.222.222": "OpenDNS",
    "208.67.220.220": "OpenDNS",
    "9.9.9.9": "Quad9",
    "149.112.112.112": "Quad9",
    "64.6.64.6": "Verisign",
    "64.6.65.6": "Verisign",
    "185.228.168.9": "CleanBrowsing",
    "185.228.169.9": "CleanBrowsing",
    "76.76.19.19": "ControlD",
    "94.140.14.14": "AdGuard",
    "94.140.15.15": "AdGuard",
}


SERVER_COUNTRIES: dict[str, str] = {
    "8.8.8.8": "US",
    "8.8.4.4": "US",
    "1.1.1.1": "AU",
    "1.0.0.1": "AU",
    "208.67.222.222": "US",
    "208.67.220.220": "US",
    "9.9.9.9": "CH",
    "149.112.112.112": "CH",
    "64.6.64.6": "US",
    "64.6.65.6": "US",
    "185.228.168.9": "CA",
    "185.228.169.9": "CA",
    "76.76.19.19": "CA",
    "94.140.14.14": "CY",
    "94.140.15.15": "CY",
}


# Known CDN and cloud provider networks
CDN_NETWORKS = {
    "Google": [
        "8.8.8.0/24",
        "8.8.4.0/24",
        "64.233.160.0/19",
        "66.102.0.0/20",
        "66.249.64.0/19",
        "72.14.192.0/18",
        "74.125.0.0/16",
        "108.177.8.0/21",
        "142.250.0.0/15",
        "172.217.0.0/16",
        "173.194.0.0/16",
        "207.126.144.0/20",
        "209.85.128.0/17",
        "216.58.192.0/19",
        "216.239.32.0/19",
    ],
    "Cloudflare": [
        "1.1.1.0/24",
        "1.0.0.0/24",
        "104.16.0.0/12",
        "172.64.0.0/13",
        "141.101.64.0/18",
        "108.162.192.0/18",
        "190.93.240.0/20",
        "188.114.96.0/20",
        "197.234.240.0/22",
        "198.41.128.0/17",
        "162.158.0.0/15",
        "173.245.48.0/20",
        "103.21.244.0/22",
        "103.22.200.0/22",
        "103.31.4.0/22",
        "141.101.64.0/18",
        "108.162.192.0/18",
        "190.93.240.0/20",
        "188.114.96.0/20",
        "197.234.240.0/22",
        "198.41.128.0/17",
    ],
    "Akamai": [
        "23.32.0.0/11",
        "23.64.0.0/14",
        "23.72.0.0/13",
        "23.192.0.0/11",
        "23.224.0.0/13",
        "23.248.0.0/14",
        "2.16.0.0/13",
        "2.20.0.0/14",
        "2.22.0.0/15",
        "2.23.0.0/16",
        "69.192.0.0/16",
        "95.100.0.0/15",
        "96.6.0.0/15",
        "104.64.0.0/10",
    ],
    "Fastly": [
        "23.235.32.0/20",
        "104.156.80.0/20",
        "151.101.0.0/16",
        "157.52.64.0/18",
        "172.111.64.0/18",
        "185.31.16.0/22",
        "199.27.72.0/21",
        "199.232.0.0/16",
    ],
    "Amazon AWS": [
        "13.32.0.0/15",
        "13.224.0.0/14",
        "52.84.0.0/15",
        "54.182.0.0/16",
        "54.192.0.0/16",
        "54.230.0.0/16",
        "54.239.128.0/18",
        "99.84.0.0/15",
        "143.204.0.0/16",
        "144.220.0.0/16",
        "13.248.0.0/14",
        "15.248.0.0/16",
        "18.64.0.0/14",
        "52.124.0.0/14",
        "52.222.0.0/15",
        "54.230.0.0/16",
        "54.239.128.0/18",
    ],
    "CloudFront": [
        "13.32.0.0/15",
        "13.224.0.0/14",
        "13.249.0.0/16",
        "18.64.0.0/14",
        "18.154.0.0/15",
        "52.84.0.0/15",
        "54.182.0.0/16",
        "54.192.0.0/16",
        "54.230.0.0/16",
        "54.239.128.0/18",
        "99.84.0.0/15",
        "143.204.0.0/16",
        "144.220.0.0/16",
        "146.254.0.0/16",
    ],
    "Microsoft": [
        "13.64.0.0/11",
        "13.96.0.0/13",
        "13.104.0.0/14",
        "20.0.0.0/8",
        "40.64.0.0/10",
        "52.96.0.0/14",
        "52.112.0.0/14",
        "52.120.0.0/14",
        "104.40.0.0/13",
        "104.208.0.0/13",
    ],
    "Azure CDN": [
        "13.73.0.0/16",
        "13.80.0.0/15",
        "13.88.0.0/16",
        "13.104.0.0/14",
        "13.107.128.0/22",
        "40.90.0.0/15",
        "40.126.0.0/18",
        "52.168.0.0/14",
        "52.224.0.0/14",
        "52.239.0.0/15",
    ],
    "Facebook": [
        "31.13.24.0/21",
        "31.13.64.0/18",
        "45.64.40.0/22",
        "66.220.144.0/20",
        "69.63.176.0/20",
        "69.171.224.0/19",
        "74.119.76.0/22",
        "102.132.96.0/20",
        "103.4.96.0/22",
        "129.134.0.0/17",
        "157.240.0.0/17",
        "173.252.64.0/18",
        "179.60.192.0/22",
        "185.60.216.0/22",
        "204.15.20.0/22",
    ],
    "Twitter": [
        "104.244.40.0/21",
        "199.16.156.0/22",
        "199.59.148.0/22",
        "192.133.76.0/22",
        "209.237.192.0/19",
        "69.195.160.0/19",
    ],
    "Netflix": [
        "3.160.0.0/12",
        "23.192.0.0/11",
        "34.192.0.0/10",
        "52.48.0.0/12",
        "54.144.0.0/12",
        "108.128.0.0/12",
        "184.72.0.0/14",
        "185.2.220.0/22",
        "185.48.244.0/22",
    ],
    "Yandex": [
        "5.45.192.0/18",
        "37.9.64.0/18",
        "77.88.0.0/18",
        "84.252.128.0/17",
        "87.250.224.0/19",
        "93.158.128.0/18",
        "95.108.128.0/17",
        "141.8.128.0/18",
        "199.21.96.0/22",
        "213.180.192.0/19",
    ],
    "Mail.ru": [
        "94.100.176.0/20",
        "95.163.0.0/16",
        "185.5.128.0/22",
        "185.30.176.0/22",
        "185.86.176.0/22",
        "217.69.128.0/20",
    ],
}


def get_ip_owner(ip: str) -> str:
    """Determine owner of IP address based on known networks."""
    try:
        ip_obj: IPv4Address | IPv6Address = ipaddress.ip_address(ip)
        if ip_obj.version == 4:
            for owner, networks in CDN_NETWORKS.items():
                for network in networks:
                    if ipaddress.ip_address(ip) in ipaddress.ip_network(network):
                        return owner
    except Exception:
        logger.exception("Get error when get ip owner")
    return "Unknown"


def is_likely_cdn(ips: list[str]) -> tuple[bool, str, float]:
    """Check if a set of IPs belongs to a CDN."""
    if not ips:
        return False, "Unknown", 0.0

    owners: list[str] = []
    for ip in ips:
        owner: str = get_ip_owner(ip)
        if owner != "Unknown":
            owners.append(owner)

    if not owners:
        return False, "Unknown", 0.0

    owner_counts: Counter[str] = Counter(owners)
    most_common: tuple[str, int] = owner_counts.most_common(1)[0]
    owner = most_common[0]
    percentage: float = (most_common[1] / len(ips)) * 100

    is_cdn: Literal[False] | str = percentage > 50 and owner != "Unknown"
    return is_cdn, owner, percentage


def _analyze_ip_patterns(records: list[str]) -> dict[str, Any]:
    """Analyze IP patterns for anomalies."""
    if not records:
        return {}

    result: dict[str, int | list[str]] = {
        "count": len(records),
        "unique": len(set(records)),
        "ipv4": 0,
        "ipv6": 0,
        "private": 0,
        "reserved": 0,
        "owners": [],
        "countries": [],
    }

    for record in records:
        try:
            ip: IPv4Address | IPv6Address = ipaddress.ip_address(record)
            if ip.version == 4:
                result["ipv4"] += 1
            else:
                result["ipv6"] += 1

            if ip.is_private:
                result["private"] += 1
            if ip.is_reserved:
                result["reserved"] += 1

            owner: str = get_ip_owner(record)
            result["owners"].append(owner)

            if record.startswith(("8.", "4.", "64.", "74.")):
                result["countries"].append("US")
            elif record.startswith(("1.", "2.")):
                result["countries"].append("EU")
            elif record.startswith(("3.", "13.")):
                result["countries"].append("Asia")
            else:
                result["countries"].append("Unknown")
        except Exception:
            logger.exception("Error analyzing IP pattern")
            continue

    return result


def _compare_results(
    control: DNSResult,
    test: DNSResult,
    server: str,
    domain: str,
) -> dict[str, Any] | None:
    """Compare control and test results for inconsistencies."""
    if test["error"] != control["error"]:
        severity: Literal["high", "medium"] = (
            "high" if "NXDOMAIN" in str(test["error"]) else "medium"
        )
        return {
            "server": server,
            "server_name": SERVER_NAMES.get(server, "Unknown"),
            "server_country": SERVER_COUNTRIES.get(server, "Unknown"),
            "type": "error_mismatch",
            "severity": severity,
            "control_error": control["error"],
            "test_error": test["error"],
            "control_records": [],
            "test_records": [],
            "control_ttl": control["ttl"],
            "test_ttl": test["ttl"],
            "diff": None,
            "control_analysis": {},
            "test_analysis": {},
        }

    if not test["error"] and not control["error"]:
        control_analysis: dict[str, Any] = _analyze_ip_patterns(control["records"])
        test_analysis: dict[str, Any] = _analyze_ip_patterns(test["records"])

        if test["records"] != control["records"]:
            control_owners: set[str] = set(control_analysis.get("owners", []))
            test_owners: set[str] = set(test_analysis.get("owners", []))

            if control_owners and test_owners and control_owners == test_owners:
                return {
                    "server": server,
                    "server_name": SERVER_NAMES.get(server, "Unknown"),
                    "server_country": SERVER_COUNTRIES.get(server, "Unknown"),
                    "type": "cdn_variation",
                    "severity": "info",
                    "control_error": None,
                    "test_error": None,
                    "control_records": control["records"],
                    "test_records": test["records"],
                    "control_ttl": control["ttl"],
                    "test_ttl": test["ttl"],
                    "diff": "cdn_nodes",
                    "common_records": list(
                        set(control["records"]).intersection(set(test["records"]))
                    ),
                    "control_analysis": control_analysis,
                    "test_analysis": test_analysis,
                    "owner": (
                        next(iter(control_owners)) if control_owners else "Unknown"
                    ),
                }

            severity = "high"
            common: set[str] = set(control["records"]).intersection(
                set(test["records"])
            )
            if common:
                severity = "medium"

            return {
                "server": server,
                "server_name": SERVER_NAMES.get(server, "Unknown"),
                "server_country": SERVER_COUNTRIES.get(server, "Unknown"),
                "type": "record_mismatch",
                "severity": severity,
                "control_error": None,
                "test_error": None,
                "control_records": control["records"],
                "test_records": test["records"],
                "control_ttl": control["ttl"],
                "test_ttl": test["ttl"],
                "diff": "records_differ",
                "common_records": list(common) if common else [],
                "control_analysis": control_analysis,
                "test_analysis": test_analysis,
                "control_owner": (
                    control_analysis.get("owners", ["Unknown"])[0]
                    if control_analysis.get("owners")
                    else "Unknown"
                ),
                "test_owner": (
                    test_analysis.get("owners", ["Unknown"])[0]
                    if test_analysis.get("owners")
                    else "Unknown"
                ),
            }

        ttl_diff: int = abs((test["ttl"] or 0) - (control["ttl"] or 0))
        if ttl_diff > 3600:
            return {
                "server": server,
                "server_name": SERVER_NAMES.get(server, "Unknown"),
                "server_country": SERVER_COUNTRIES.get(server, "Unknown"),
                "type": "ttl_mismatch",
                "severity": "low",
                "control_error": None,
                "test_error": None,
                "control_records": control["records"],
                "test_records": test["records"],
                "control_ttl": control["ttl"],
                "test_ttl": test["ttl"],
                "diff": ttl_diff,
                "control_analysis": control_analysis,
                "test_analysis": test_analysis,
            }

    return None


def check_dns_poisoning(
    domain: str,
    control_server: str = "8.8.8.8",
    test_servers: list[str] | None = None,
    record_type: str = "A",
    additional_types: list[str] | None = None,
) -> PoisoningCheckResult:
    """Check for signs of DNS poisoning or censorship."""
    if test_servers is None:
        test_servers = get_public_dns_servers()

    control_result: DNSResult = resolve_with_timer(
        domain, record_type, control_server, include_ttl=True
    )

    additional_results: dict[str, str] | None = _get_additional_records(
        domain, additional_types, control_server
    )

    test_results, inconsistencies, mismatches, cdn_variations = _test_dns_servers(
        domain, record_type, control_server, test_servers, control_result
    )

    metrics: dict[str, str] = _calculate_metrics(
        test_results, control_result, test_servers, mismatches, cdn_variations
    )

    poisoning_level: str = _determine_poisoning_level(
        metrics["confidence"],
        poisoned=metrics["poisoned"],
        cdn_detected=metrics["cdn_detected"],
    )

    return _build_result(
        domain=domain,
        record_type=record_type,
        control_server=control_server,
        control_result=control_result,
        test_results=test_results,
        additional_results=additional_results,
        inconsistencies=inconsistencies,
        mismatches=mismatches,
        cdn_variations=cdn_variations,
        metrics=metrics,
        poisoning_level=poisoning_level,
    )


def _get_additional_records(
    domain: str, additional_types: list[str] | None, control_server: str
) -> dict | None:
    """Get additional record types from control server."""
    if not additional_types:
        return None

    additional_results: dict[str, DNSResult] = {}
    for rtype in additional_types:
        additional_results[rtype] = resolve_with_timer(
            domain, rtype, control_server, include_ttl=True
        )
    return additional_results


def _test_dns_servers(
    domain: str,
    record_type: str,
    control_server: str,
    test_servers: list[str],
    control_result: DNSResult,
) -> tuple[dict[str, DNSResult], list[dict[str, Any]], int, int]:
    """Test all DNS servers and collect results."""
    test_results: dict[str, DNSResult] = {}
    inconsistencies: list[dict[str, Any]] = []
    mismatches = 0
    cdn_variations = 0
    severity_counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0, "info": 0}

    for server in test_servers:
        if server == control_server:
            continue

        test_result: DNSResult = resolve_with_timer(
            domain, record_type, server, include_ttl=True
        )
        test_results[server] = test_result

        inconsistency: dict[str, Any] | None = _compare_results(
            control_result, test_result, server, domain
        )
        if inconsistency:
            inconsistencies.append(inconsistency)
            severity = inconsistency.get("severity", "low")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            if inconsistency["type"] == "record_mismatch":
                mismatches += 1
            elif inconsistency["type"] == "cdn_variation":
                cdn_variations += 1

    return test_results, inconsistencies, mismatches, cdn_variations


def _calculate_metrics(
    test_results: dict[str, DNSResult],
    control_result: DNSResult,
    mismatches: int,
    cdn_variations: int,
) -> dict:
    """Calculate various metrics from test results."""
    total_tested: int = len(test_results)

    all_ips: list[str] = []
    for res in test_results.values():
        all_ips.extend(res.get("records", []))

    is_cdn, cdn_owner, cdn_percentage = is_likely_cdn(all_ips)

    if is_cdn:
        poisoned: bool = mismatches > 0 and cdn_percentage < 50
        confidence: Literal[0] | float = (
            (mismatches / total_tested * 100) if total_tested > 0 else 0
        )
        confidence = confidence * (1 - cdn_percentage / 100)
    else:
        poisoned: bool = mismatches > 0
        confidence: Literal[0] | float = (
            (mismatches / total_tested * 100) if total_tested > 0 else 0
        )

    control_ips: set[str] = set(control_result.get("records", []))
    all_test_ips: set[str] = set()
    for res in test_results.values():
        all_test_ips.update(res.get("records", []))

    consensus_ips: Counter[str | str] = Counter()
    for res in test_results.values():
        for ip in res.get("records", []):
            consensus_ips[ip] += 1

    top_consensus: list[tuple[str, int]] = consensus_ips.most_common(3)
    consensus_rate: Literal[0] | float = (
        (top_consensus[0][1] / total_tested * 100)
        if top_consensus and total_tested > 0
        else 0
    )

    geo_diversity: int = len({SERVER_COUNTRIES.get(s, "Unknown") for s in test_results})

    return {
        "total_tested": total_tested,
        "poisoned": poisoned,
        "confidence": round(confidence, 1),
        "mismatches": mismatches,
        "cdn_variations": cdn_variations,
        "cdn_detected": is_cdn,
        "cdn_owner": cdn_owner,
        "cdn_percentage": round(cdn_percentage, 1),
        "unique_ips_seen": len(all_test_ips),
        "ip_diversity": len(all_test_ips - control_ips),
        "control_ip_count": len(control_ips),
        "consensus_top": top_consensus,
        "consensus_rate": round(consensus_rate, 1),
        "geo_diversity": geo_diversity,
        "anycast_likely": len(all_test_ips) > 3 and len(control_ips) == 1,
        "cdn_likely": is_cdn,
        "poisoning_likely": mismatches == total_tested
        and not is_cdn
        and len(control_ips) > 1
        and len(all_test_ips) == 1,
    }


def _determine_poisoning_level(
    confidence: float, *, poisoned: bool, cdn_detected: bool
) -> str:
    """Determine the poisoning level based on confidence and CDN detection."""
    if not poisoned:
        return "NONE"
    if cdn_detected:
        if confidence > 80:
            return "SUSPICIOUS"
        return "LOW"
    if confidence > 80:
        return "CRITICAL"
    if confidence > 50:
        return "HIGH"
    if confidence > 20:
        return "MEDIUM"
    return "LOW"


def _build_result(
    domain: str,
    record_type: str,
    control_server: str,
    control_result: DNSResult,
    test_results: dict[str, DNSResult],
    additional_results: dict | None,
    inconsistencies: list[dict[str, Any]],
    mismatches: int,
    cdn_variations: int,
    metrics: dict,
    poisoning_level: str,
) -> PoisoningCheckResult:
    """Build the final result dictionary."""
    control_analysis: dict[str, Any] = _analyze_ip_patterns(
        control_result.get("records", [])
    )

    return {
        "domain": domain,
        "record_type": record_type,
        "control_server": control_server,
        "control_name": SERVER_NAMES.get(control_server, "Unknown"),
        "control_country": SERVER_COUNTRIES.get(control_server, "Unknown"),
        "control_result": control_result,
        "control_analysis": control_analysis,
        "control_owner": (
            control_analysis.get("owners", ["Unknown"])[0]
            if control_analysis.get("owners")
            else "Unknown"
        ),
        "additional_records": additional_results,
        "test_results": test_results,
        "test_servers_count": metrics["total_tested"],
        "inconsistencies": inconsistencies,
        "poisoned": metrics["poisoned"],
        "poisoning_level": poisoning_level,
        "confidence": metrics["confidence"],
        "mismatches": mismatches,
        "cdn_variations": cdn_variations,
        "cdn_detected": metrics["cdn_detected"],
        "cdn_owner": metrics["cdn_owner"],
        "cdn_percentage": metrics["cdn_percentage"],
        "severity": _count_severities(inconsistencies),
        "unique_ips_seen": metrics["unique_ips_seen"],
        "ip_diversity": metrics["ip_diversity"],
        "control_ip_count": metrics["control_ip_count"],
        "consensus_top": (
            [
                {
                    "ip": ip,
                    "count": count,
                    "percentage": round(count / metrics["total_tested"] * 100, 1),
                    "owner": get_ip_owner(ip),
                }
                for ip, count in metrics["consensus_top"]
            ]
            if metrics["consensus_top"]
            else []
        ),
        "consensus_rate": metrics["consensus_rate"],
        "geo_diversity": metrics["geo_diversity"],
        "anycast_likely": metrics["anycast_likely"],
        "cdn_likely": metrics["cdn_likely"],
        "poisoning_likely": metrics["poisoning_likely"],
    }


def _count_severities(inconsistencies: list[dict[str, Any]]) -> dict[str, int]:
    """Count inconsistencies by severity level."""
    severity_counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for inc in inconsistencies:
        severity_counts[inc.get("severity", "low")] += 1
    return severity_counts
