"""
DNS poisoning detection and analysis functionality.

This module provides tools to detect DNS cache poisoning, censorship,
and manipulation by comparing responses from multiple DNS resolvers
across different geographic locations and providers.
"""

import ipaddress
from collections import Counter
from ipaddress import IPv4Address, IPv6Address
from logging import Logger
from typing import Literal, TypedDict

from nadzoring.dns_lookup.types import DNSResult, PoisoningCheckResult
from nadzoring.dns_lookup.utils import get_public_dns_servers, resolve_with_timer
from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


# Mapping of DNS server IPs to their provider names
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
"""Mapping of public DNS server IP addresses to their provider names."""


# Mapping of DNS server IPs to their geographic locations (country codes)
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
"""Mapping of public DNS server IP addresses to their country codes."""


# Known CDN and cloud provider network ranges
CDN_NETWORKS: dict[str, list[str]] = {
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
"""Known CDN and cloud provider network ranges for IP ownership detection."""


class IPAnalysisResult(TypedDict, total=False):
    """
    Result of IP address pattern analysis.

    Contains detailed statistics and classifications for a set of IP addresses
    returned by DNS resolvers.

    Attributes:
        count: Total number of IP addresses analyzed.
        unique: Number of unique IP addresses in the set.
        ipv4: Count of IPv4 addresses.
        ipv6: Count of IPv6 addresses.
        private: Count of private (RFC 1918) IP addresses.
        reserved: Count of reserved IP addresses.
        owners: List of inferred owners for each IP (CDN/provider names).
        countries: List of inferred countries for each IP.

    """

    count: int
    unique: int
    ipv4: int
    ipv6: int
    private: int
    reserved: int
    owners: list[str]
    countries: list[str]


class InconsistencyDetail(TypedDict):
    """
    Detailed information about a DNS response inconsistency.

    Attributes:
        server: IP address of the DNS server that returned inconsistent results.
        server_name: Provider name of the server (from SERVER_NAMES).
        server_country: Country code of the server (from SERVER_COUNTRIES).
        type: Type of inconsistency ('error_mismatch', 'record_mismatch',
              'cdn_variation', 'ttl_mismatch').
        severity: Impact severity ('high', 'medium', 'low', 'info').
        control_error: Error from control server (if any).
        test_error: Error from test server (if any).
        control_records: Records from control server.
        test_records: Records from test server.
        control_ttl: TTL from control server.
        test_ttl: TTL from test server.
        diff: Difference description or value.
        common_records: Records common to both responses (optional).
        control_analysis: IP analysis for control records.
        test_analysis: IP analysis for test records.
        owner: Common owner if applicable (optional).
        control_owner: Owner of control records (optional).
        test_owner: Owner of test records (optional).

    """

    server: str
    server_name: str
    server_country: str
    type: Literal["error_mismatch", "record_mismatch", "cdn_variation", "ttl_mismatch"]
    severity: Literal["high", "medium", "low", "info"]
    control_error: str | None
    test_error: str | None
    control_records: list[str]
    test_records: list[str]
    control_ttl: int | None
    test_ttl: int | None
    diff: str | int | None
    common_records: list[str] | None
    control_analysis: IPAnalysisResult
    test_analysis: IPAnalysisResult
    owner: str | None
    control_owner: str | None
    test_owner: str | None


class MetricsResult(TypedDict):
    """
    Calculated metrics from DNS poisoning test.

    Attributes:
        total_tested: Number of test servers queried.
        poisoned: Boolean indicating if poisoning was detected.
        confidence: Confidence score (0-100) of poisoning detection.
        mismatches: Count of record mismatches found.
        cdn_variations: Count of CDN variations found.
        cdn_detected: Whether CDN usage was detected.
        cdn_owner: Name of detected CDN provider.
        cdn_percentage: Percentage of IPs belonging to CDN.
        unique_ips_seen: Number of unique IPs across all test results.
        ip_diversity: Number of IPs not in control results.
        control_ip_count: Number of IPs in control results.
        consensus_top: Top 3 most common IPs and their counts.
        consensus_rate: Percentage of servers returning the most common IP.
        geo_diversity: Number of unique countries among test servers.
        anycast_likely: Whether anycast routing is likely.
        cdn_likely: Whether CDN usage is likely.
        poisoning_likely: Whether poisoning is likely.

    """

    total_tested: int
    poisoned: bool
    confidence: float
    mismatches: int
    cdn_variations: int
    cdn_detected: bool
    cdn_owner: str
    cdn_percentage: float
    unique_ips_seen: int
    ip_diversity: int
    control_ip_count: int
    consensus_top: list[tuple[str, int]]
    consensus_rate: float
    geo_diversity: int
    anycast_likely: bool
    cdn_likely: bool
    poisoning_likely: bool


def get_ip_owner(ip: str) -> str:
    """
    Determine the owner/provider of an IP address based on known network ranges.

    Checks if the IP address falls within any known CDN or cloud provider
    network ranges defined in CDN_NETWORKS.

    Args:
        ip: IP address string to check (IPv4 or IPv6).

    Returns:
        str: Name of the owner/provider if found in known networks,
             otherwise returns "Unknown".

    Examples:
        >>> get_ip_owner("8.8.8.8")
        'Google'
        >>> get_ip_owner("1.1.1.1")
        'Cloudflare'
        >>> get_ip_owner("192.168.1.1")
        'Unknown'

    Notes:
        - Only IPv4 networks are currently supported in CDN_NETWORKS.
        - IPv6 addresses will always return "Unknown" with current data.
        - Exceptions during IP parsing are logged and result in "Unknown".

    """
    try:
        ip_obj: IPv4Address | IPv6Address = ipaddress.ip_address(ip)
        if ip_obj.version == 4:
            for owner, networks in CDN_NETWORKS.items():
                for network in networks:
                    if ipaddress.ip_address(ip) in ipaddress.ip_network(network):
                        return owner
    except Exception:
        logger.exception("Error determining IP owner for %s", ip)
    return "Unknown"


def is_likely_cdn(ips: list[str]) -> tuple[bool, str, float]:
    """
    Determine if a set of IP addresses likely belongs to a CDN.

    Analyzes IP addresses to detect patterns consistent with Content Delivery
    Network (CDN) usage, such as multiple IPs from the same provider.

    Args:
        ips: List of IP address strings to analyze.

    Returns:
        Tuple[bool, str, float]: A tuple containing:
            - is_cdn: True if more than 50% of IPs belong to the same known CDN.
            - owner: Name of the most common CDN owner found.
            - percentage: Percentage of IPs belonging to that owner (0-100).

    Examples:
        >>> ips = ["1.1.1.1", "1.0.0.1", "8.8.8.8"]
        >>> is_likely_cdn(ips)
        (True, 'Cloudflare', 66.7)

        >>> ips = ["192.168.1.1", "10.0.0.1"]
        >>> is_likely_cdn(ips)
        (False, 'Unknown', 0.0)

    Notes:
        - Returns (False, "Unknown", 0.0) for empty input.
        - The 50% threshold is used to determine CDN likelihood.
        - Only considers IPs from known CDN networks.

    """
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

    is_cdn: bool = percentage > 50 and owner != "Unknown"
    return is_cdn, owner, percentage


def _analyze_ip_patterns(records: list[str]) -> IPAnalysisResult:
    """
    Analyze IP address patterns for anomalies and characteristics.

    Performs detailed analysis of IP addresses returned in DNS responses,
    classifying them by type, ownership, and geographic patterns.

    Args:
        records: List of IP address strings to analyze.

    Returns:
        IPAnalysisResult: Dictionary containing analysis results:
            - count: Total number of records analyzed
            - unique: Number of unique IPs
            - ipv4: Count of IPv4 addresses
            - ipv6: Count of IPv6 addresses
            - private: Count of private IPs (RFC 1918)
            - reserved: Count of reserved IPs
            - owners: List of inferred owners for each IP
            - countries: List of inferred countries for each IP

    Notes:
        - Returns empty dict for empty input.
        - Country inference is simplified based on IP prefixes.
        - Exceptions during analysis are logged and skipped.

    """
    if not records:
        return {}

    result: IPAnalysisResult = {
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

            # Simplified country inference based on IP prefixes
            if record.startswith(("8.", "4.", "64.", "74.")):
                result["countries"].append("US")
            elif record.startswith(("1.", "2.")):
                result["countries"].append("EU")
            elif record.startswith(("3.", "13.")):
                result["countries"].append("Asia")
            else:
                result["countries"].append("Unknown")
        except Exception:
            logger.exception("Error analyzing IP pattern for %s", record)
            continue

    return result


def _compare_results(
    control: DNSResult,
    test: DNSResult,
    server: str,
    domain: str,
) -> InconsistencyDetail | None:
    """
    Compare control and test DNS results for inconsistencies.

    Performs detailed comparison between a trusted control resolver and a
    test resolver, identifying various types of discrepancies.

    Args:
        control: DNSResult from the control (trusted) resolver.
        test: DNSResult from the test resolver to compare.
        server: IP address of the test server.
        domain: Domain name being tested (for context).

    Returns:
        Optional[InconsistencyDetail]: Detailed inconsistency information if
            discrepancies are found, None if results are consistent.

    Types of inconsistencies detected:
        - error_mismatch: Different error states between resolvers
        - record_mismatch: Different record sets returned
        - cdn_variation: Different but CDN-related records (informational)
        - ttl_mismatch: Significant TTL differences (>1 hour)

    Notes:
        - Severity levels: high (potential poisoning), medium (suspicious),
          low (minor), info (informational)
        - CDN variations are flagged as "info" severity
        - Error mismatches with NXDOMAIN are considered high severity

    """
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
            "common_records": [],
            "control_analysis": {},
            "test_analysis": {},
            "owner": None,
            "control_owner": None,
            "test_owner": None,
        }

    if not test["error"] and not control["error"]:
        control_analysis: IPAnalysisResult = _analyze_ip_patterns(control["records"])
        test_analysis: IPAnalysisResult = _analyze_ip_patterns(test["records"])

        if test["records"] != control["records"]:
            control_owners: set[str] = set(control_analysis.get("owners", []))
            test_owners: set[str] = set(test_analysis.get("owners", []))

            # Check if this is a CDN variation (different IPs, same owner)
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
                    "control_owner": None,
                    "test_owner": None,
                }

            # Regular record mismatch
            severity: Literal["high", "medium"] = "high"
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
                "owner": None,
            }

        # Check for significant TTL differences
        ttl_diff: int = abs((test["ttl"] or 0) - (control["ttl"] or 0))
        if ttl_diff > 3600:  # More than 1 hour difference
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
                "common_records": control["records"],
                "control_analysis": control_analysis,
                "test_analysis": test_analysis,
                "owner": None,
                "control_owner": None,
                "test_owner": None,
            }

    return None


def check_dns_poisoning(
    domain: str,
    control_server: str = "8.8.8.8",
    test_servers: list[str] | None = None,
    record_type: str = "A",
    additional_types: list[str] | None = None,
) -> PoisoningCheckResult:
    """
    Check for signs of DNS poisoning, censorship, or manipulation.

    Comprehensive DNS poisoning detection by comparing responses from multiple
    DNS resolvers against a trusted control resolver. Analyzes patterns,
    identifies inconsistencies, and provides confidence scoring.

    Args:
        domain: Domain name to test for poisoning (e.g., "example.com").
        control_server: Trusted DNS server IP to use as baseline comparison.
                       Defaults to Google DNS (8.8.8.8).
        test_servers: List of DNS server IPs to test. If None, uses
                     get_public_dns_servers() for a comprehensive list.
        record_type: DNS record type to query for poisoning detection.
                    Defaults to "A" records.
        additional_types: Optional list of additional record types to query
                         from the control server for extra context.

    Returns:
        PoisoningCheckResult: Comprehensive poisoning analysis containing:
            - domain: The tested domain
            - record_type: The record type queried
            - control_server: IP of control server used
            - control_result: DNSResult from control server
            - test_results: Dict mapping test servers to their DNSResults
            - inconsistencies: List of detected inconsistencies
            - poisoned: Boolean indicating poisoning detection
            - poisoning_level: Severity level ("NONE", "LOW", "MEDIUM",
                              "HIGH", "CRITICAL", "SUSPICIOUS")
            - confidence: Confidence score (0-100)
            - Additional metrics including CDN detection, geo-diversity,
              consensus analysis, and more

    Examples:
        >>> # Basic poisoning check
        >>> result = check_dns_poisoning("example.com")
        >>> if result["poisoned"]:
        ...     print(f"Poisoning detected! Confidence: {result['confidence']}%")

        >>> # Check multiple record types
        >>> result = check_dns_poisoning("example.com", additional_types=["MX", "TXT"])

        >>> # Custom test servers
        >>> result = check_dns_poisoning(
        ...     "example.com", test_servers=["1.1.1.1", "9.9.9.9"]
        ... )

    Notes:
        - High confidence (>80%) with mismatches indicates probable poisoning
        - CDN variations are flagged as informational, not poisoning
        - Geographic diversity of test servers improves detection accuracy
        - Timeout errors are logged but don't affect poisoning detection

    """
    if test_servers is None:
        test_servers = get_public_dns_servers()

    # Query control server
    control_result: DNSResult = resolve_with_timer(
        domain, record_type, control_server, include_ttl=True
    )

    # Get additional record types if requested
    additional_results: dict[str, DNSResult] | None = _get_additional_records(
        domain, additional_types, control_server
    )

    # Test all DNS servers and collect inconsistencies
    test_results, inconsistencies, mismatches, cdn_variations = _test_dns_servers(
        domain, record_type, test_servers, control_result
    )

    # Calculate metrics
    metrics: MetricsResult = _calculate_metrics(
        test_results, control_result, mismatches, cdn_variations
    )

    # Determine poisoning level
    poisoning_level: str = _determine_poisoning_level(
        metrics["confidence"],
        poisoned=metrics["poisoned"],
        cdn_detected=metrics["cdn_detected"],
    )

    # Build and return final result
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
) -> dict[str, DNSResult] | None:
    """
    Retrieve additional DNS record types from the control server.

    Queries the control server for supplementary record types to provide
    additional context for poisoning analysis.

    Args:
        domain: Domain name to query.
        additional_types: List of record types to query (e.g., ["MX", "TXT"]).
        control_server: IP address of the control DNS server.

    Returns:
        Optional[Dict[str, DNSResult]]: Dictionary mapping record types to
            their DNS results, or None if no additional types requested.

    """
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
    test_servers: list[str],
    control_result: DNSResult,
) -> tuple[dict[str, DNSResult], list[InconsistencyDetail], int, int]:
    """
    Test all DNS servers and collect results and inconsistencies.

    Queries each test server and compares results against the control server
    to identify discrepancies.

    Args:
        domain: Domain name to query.
        record_type: DNS record type to query.
        test_servers: List of test server IP addresses.
        control_result: DNSResult from the control server for comparison.

    Returns:
        Tuple containing:
            - test_results: Dict mapping server IPs to their DNSResults
            - inconsistencies: List of detected inconsistencies
            - mismatches: Count of record mismatches found
            - cdn_variations: Count of CDN variations found

    """
    test_results: dict[str, DNSResult] = {}
    inconsistencies: list[InconsistencyDetail] = []
    mismatches = 0
    cdn_variations = 0

    for server in test_servers:
        # Skip the control server itself
        if server == next(iter(SERVER_NAMES.keys())):  # 8.8.8.8
            continue

        test_result: DNSResult = resolve_with_timer(
            domain, record_type, server, include_ttl=True
        )
        test_results[server] = test_result

        inconsistency: InconsistencyDetail | None = _compare_results(
            control_result, test_result, server, domain
        )
        if inconsistency:
            inconsistencies.append(inconsistency)

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
) -> MetricsResult:
    """
    Calculate various metrics from test results for poisoning analysis.

    Computes statistical measures including confidence scores, diversity
    metrics, and pattern detection for the poisoning check.

    Args:
        test_results: Dict mapping server IPs to their DNSResults.
        control_result: DNSResult from the control server.
        mismatches: Count of record mismatches found.
        cdn_variations: Count of CDN variations found.

    Returns:
        MetricsResult: Comprehensive metrics including confidence scores,
            diversity measures, and detection flags.

    """
    total_tested: int = len(test_results)

    # Collect all IPs from test results
    all_ips: list[str] = []
    for res in test_results.values():
        all_ips.extend(res.get("records", []))

    # Check for CDN usage
    is_cdn, cdn_owner, cdn_percentage = is_likely_cdn(all_ips)

    # Calculate confidence based on CDN detection
    if is_cdn:
        poisoned: bool = mismatches > 0 and cdn_percentage < 50
        confidence: float = (mismatches / total_tested * 100) if total_tested > 0 else 0
        confidence = confidence * (1 - cdn_percentage / 100)
    else:
        poisoned: bool = mismatches > 0
        confidence: float = (mismatches / total_tested * 100) if total_tested > 0 else 0

    # Calculate IP diversity
    control_ips: set[str] = set(control_result.get("records", []))
    all_test_ips: set[str] = set()
    for res in test_results.values():
        all_test_ips.update(res.get("records", []))

    # Find consensus IPs
    consensus_ips: Counter[str] = Counter()
    for res in test_results.values():
        for ip in res.get("records", []):
            consensus_ips[ip] += 1

    top_consensus: list[tuple[str, int]] = consensus_ips.most_common(3)
    consensus_rate: float = (
        (top_consensus[0][1] / total_tested * 100)
        if top_consensus and total_tested > 0
        else 0
    )

    # Geographic diversity
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
    """
    Determine the poisoning level based on confidence and CDN detection.

    Maps numerical confidence and detection flags to a human-readable
    poisoning severity level.

    Args:
        confidence: Confidence score (0-100).
        poisoned: Whether poisoning was detected.
        cdn_detected: Whether CDN usage was detected.

    Returns:
        str: Poisoning level classification:
            - "NONE": No poisoning detected
            - "LOW": Low confidence poisoning or with CDN
            - "MEDIUM": Moderate confidence poisoning
            - "HIGH": High confidence poisoning
            - "CRITICAL": Very high confidence poisoning
            - "SUSPICIOUS": High confidence but CDN detected

    Notes:
        - Returns "NONE" if not poisoned
        - CDN detection downgrades severity to "SUSPICIOUS" for high confidence

    """
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
    additional_results: dict[str, DNSResult] | None,
    inconsistencies: list[InconsistencyDetail],
    mismatches: int,
    cdn_variations: int,
    metrics: MetricsResult,
    poisoning_level: str,
) -> PoisoningCheckResult:
    """
    Build the final poisoning check result dictionary.

    Constructs the comprehensive PoisoningCheckResult by combining all
    collected data, analyses, and metrics.

    Args:
        domain: Tested domain name.
        record_type: DNS record type queried.
        control_server: Control server IP address.
        control_result: DNSResult from control server.
        test_results: Dict of test server results.
        additional_results: Optional additional record type results.
        inconsistencies: List of detected inconsistencies.
        mismatches: Count of record mismatches.
        cdn_variations: Count of CDN variations.
        metrics: Calculated metrics from _calculate_metrics.
        poisoning_level: Determined poisoning level string.

    Returns:
        PoisoningCheckResult: Complete poisoning check result with all fields
            populated according to the type definition.

    """
    # Analyze control server records
    control_analysis: IPAnalysisResult = _analyze_ip_patterns(
        control_result.get("records", [])
    )

    # Format consensus top with additional metadata
    formatted_consensus = []
    if metrics["consensus_top"]:
        for ip, count in metrics["consensus_top"]:
            formatted_consensus.append(
                {
                    "ip": ip,
                    "count": count,
                    "percentage": round(count / metrics["total_tested"] * 100, 1),
                    "owner": get_ip_owner(ip),
                }
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
        "consensus_top": formatted_consensus,
        "consensus_rate": metrics["consensus_rate"],
        "geo_diversity": metrics["geo_diversity"],
        "anycast_likely": metrics["anycast_likely"],
        "cdn_likely": metrics["cdn_likely"],
        "poisoning_likely": metrics["poisoning_likely"],
    }


def _count_severities(inconsistencies: list[InconsistencyDetail]) -> dict[str, int]:
    """
    Count inconsistencies by severity level.

    Aggregates the count of inconsistencies for each severity category.

    Args:
        inconsistencies: List of inconsistency details.

    Returns:
        Dict[str, int]: Dictionary mapping severity levels to their counts:
            - "high": Critical issues
            - "medium": Suspicious issues
            - "low": Minor issues
            - "info": Informational items

    """
    severity_counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for inc in inconsistencies:
        severity_counts[inc.get("severity", "low")] += 1
    return severity_counts
