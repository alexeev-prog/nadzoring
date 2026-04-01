"""
DNS poisoning detection and analysis functionality.

This module detects DNS cache poisoning, censorship, and manipulation by
comparing responses from multiple resolvers across different geographic
locations and providers.
"""

import ipaddress
from collections import Counter
from ipaddress import IPv4Address, IPv6Address
from logging import Logger
from typing import Literal, TypedDict

from nadzoring.dns_lookup.types import DNSResult, PoisoningCheckResult, RecordType
from nadzoring.dns_lookup.utils import get_public_dns_servers, resolve_with_timer
from nadzoring.logger import get_logger
from nadzoring.utils.timeout import TimeoutConfig

logger: Logger = get_logger(__name__)

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
"""Mapping of public DNS server IPs to their provider names."""

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
"""Mapping of public DNS server IPs to their country codes."""

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

    Attributes:
        count: Total number of IP addresses analysed.
        unique: Number of unique IP addresses.
        ipv4: Count of IPv4 addresses.
        ipv6: Count of IPv6 addresses.
        private: Count of private (RFC 1918) addresses.
        reserved: Count of reserved addresses.
        owners: Inferred provider name for each IP.
        countries: Inferred country for each IP (simplified heuristic).

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
        server: IP of the DNS server that returned inconsistent results.
        server_name: Provider name from :data:`SERVER_NAMES`.
        server_country: Country code from :data:`SERVER_COUNTRIES`.
        type: Inconsistency class — ``"error_mismatch"``,
            ``"record_mismatch"``, ``"cdn_variation"``, or
            ``"ttl_mismatch"``.
        severity: Impact level — ``"high"``, ``"medium"``, ``"low"``,
            or ``"info"``.
        control_error: Error from the control server, if any.
        test_error: Error from the test server, if any.
        control_records: Records returned by the control server.
        test_records: Records returned by the test server.
        control_ttl: TTL from the control server.
        test_ttl: TTL from the test server.
        diff: Description or numeric magnitude of the difference.
        common_records: Records present in both responses.
        control_analysis: IP analysis for the control records.
        test_analysis: IP analysis for the test records.
        owner: Shared owner when both sides belong to the same network.
        control_owner: Inferred owner of the control records.
        test_owner: Inferred owner of the test records.

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
    Aggregated metrics from a DNS poisoning test run.

    Attributes:
        total_tested: Number of test servers queried.
        poisoned: Whether poisoning indicators exceed the threshold.
        confidence: Confidence score (0-100).
        mismatches: Count of record mismatches.
        cdn_variations: Count of CDN-related IP variations.
        cdn_detected: Whether CDN usage was identified.
        cdn_owner: Name of the detected CDN provider.
        cdn_percentage: Percentage of IPs belonging to the CDN.
        unique_ips_seen: Unique IPs across all test results.
        ip_diversity: IPs not present in the control result.
        control_ip_count: IPs returned by the control server.
        consensus_top: Top-3 most common IPs with counts.
        consensus_rate: Percentage of servers returning the most common IP.
        geo_diversity: Unique countries among test servers.
        anycast_likely: Whether anycast routing is probable.
        cdn_likely: Whether CDN usage is probable.
        poisoning_likely: Whether deliberate poisoning is probable.

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
    Determine the CDN/cloud provider for an IP address.

    Only IPv4 addresses are matched against :data:`CDN_NETWORKS`; IPv6
    always returns ``"Unknown"``.

    Args:
        ip: IP address string to check.

    Returns:
        Provider name if a match is found, otherwise ``"Unknown"``.

    Examples:
        >>> get_ip_owner("8.8.8.8")
        'Google'
        >>> get_ip_owner("192.168.1.1")
        'Unknown'

    """
    try:
        ip_obj: IPv4Address | IPv6Address = ipaddress.ip_address(ip)
        if ip_obj.version != 4:
            return "Unknown"
        for owner, networks in CDN_NETWORKS.items():
            for network in networks:
                if ip_obj in ipaddress.ip_network(network):
                    return owner
    except Exception:
        logger.exception("Error determining IP owner for %s", ip)
    return "Unknown"


def is_likely_cdn(ips: list[str]) -> tuple[bool, str, float]:
    """
    Determine whether a set of IP addresses likely belongs to a CDN.

    More than 50 % of IPs belonging to the same known provider is treated
    as CDN usage.

    Args:
        ips: IP address strings to analyse.

    Returns:
        Three-tuple of ``(is_cdn, owner_name, percentage)``.
        Returns ``(False, "Unknown", 0.0)`` for empty input.

    Examples:
        >>> is_likely_cdn(["1.1.1.1", "1.0.0.1", "8.8.8.8"])
        (True, 'Cloudflare', 66.7)

    """
    if not ips:
        return False, "Unknown", 0.0

    known_owners: list[str] = [get_ip_owner(ip) for ip in ips if get_ip_owner(ip) != "Unknown"]

    if not known_owners:
        return False, "Unknown", 0.0

    most_common_owner, most_common_count = Counter(known_owners).most_common(1)[0]
    percentage: float = (most_common_count / len(ips)) * 100
    is_cdn: bool = percentage > 50 and most_common_owner != "Unknown"

    return is_cdn, most_common_owner, percentage


def _analyze_ip_patterns(records: list[str]) -> IPAnalysisResult:
    """
    Analyse IP address patterns for characteristics and ownership.

    Args:
        records: IP address strings to analyse.

    Returns:
        :class:`IPAnalysisResult` dict, or an empty dict for empty input.

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
        except ValueError:
            logger.debug("Skipping invalid IP in pattern analysis: %s", record)
            continue

        if ip.version == 4:
            result["ipv4"] += 1
        else:
            result["ipv6"] += 1

        if ip.is_private:
            result["private"] += 1
        if ip.is_reserved:
            result["reserved"] += 1

        result["owners"].append(get_ip_owner(record))

        if record.startswith(("8.", "4.", "64.", "74.")):
            result["countries"].append("US")
        elif record.startswith(("1.", "2.")):
            result["countries"].append("EU")
        elif record.startswith(("3.", "13.")):
            result["countries"].append("Asia")
        else:
            result["countries"].append("Unknown")

    return result


def _compare_results(
    control: DNSResult,
    test: DNSResult,
    server: str,
) -> InconsistencyDetail | None:
    """
    Compare control and test DNS results and return an inconsistency if found.

    Detects ``error_mismatch``, ``record_mismatch``, ``cdn_variation``, and
    ``ttl_mismatch`` (> 1 hour) types.

    Args:
        control: DNS result from the trusted control resolver.
        test: DNS result from the test resolver.
        server: IP address of the test server.

    Returns:
        :class:`InconsistencyDetail` when a discrepancy is found,
        ``None`` when results are consistent.

    """
    if test.get("error") != control.get("error"):
        level: Literal["high", "medium"] = "high" if "NXDOMAIN" in str(test.get("error")) else "medium"
        return InconsistencyDetail(
            server=server,
            server_name=SERVER_NAMES.get(server, "Unknown"),
            server_country=SERVER_COUNTRIES.get(server, "Unknown"),
            type="error_mismatch",
            severity=level,
            control_error=control.get("error"),
            test_error=test.get("error"),
            control_records=control.get("records", []),
            test_records=test.get("records", []),
            control_ttl=control.get("ttl"),
            test_ttl=test.get("ttl"),
            diff=None,
            common_records=[],
            control_analysis={},
            test_analysis={},
            owner=None,
            control_owner=None,
            test_owner=None,
        )

    if test.get("error") or control.get("error"):
        return None

    control_analysis: IPAnalysisResult = _analyze_ip_patterns(control.get("records", []))
    test_analysis: IPAnalysisResult = _analyze_ip_patterns(test.get("records", []))

    if test.get("records") != control.get("records"):
        control_owners: set[str] = set(control_analysis.get("owners", []))
        test_owners: set[str] = set(test_analysis.get("owners", []))
        common: set[str] = set(control.get("records", [])).intersection(test.get("records", []))

        if control_owners and test_owners and control_owners == test_owners:
            return InconsistencyDetail(
                server=server,
                server_name=SERVER_NAMES.get(server, "Unknown"),
                server_country=SERVER_COUNTRIES.get(server, "Unknown"),
                type="cdn_variation",
                severity="info",
                control_error=control.get("error"),
                test_error=test.get("error"),
                control_records=control.get("records", []),
                test_records=test.get("records", []),
                control_ttl=control.get("ttl"),
                test_ttl=test.get("ttl"),
                diff="cdn_nodes",
                common_records=list(common),
                control_analysis=control_analysis,
                test_analysis=test_analysis,
                owner=next(iter(control_owners), "Unknown"),
                control_owner=None,
                test_owner=None,
            )

        mismatch_severity: Literal["high", "medium"] = "medium" if common else "high"
        control_owners_list: list[str] = control_analysis.get("owners", [])
        test_owners_list: list[str] = test_analysis.get("owners", [])

        return InconsistencyDetail(
            server=server,
            server_name=SERVER_NAMES.get(server, "Unknown"),
            server_country=SERVER_COUNTRIES.get(server, "Unknown"),
            type="record_mismatch",
            severity=mismatch_severity,
            control_error=control.get("error"),
            test_error=test.get("error"),
            control_records=control.get("records", []),
            test_records=test.get("records", []),
            control_ttl=control.get("ttl"),
            test_ttl=test.get("ttl"),
            diff="records_differ",
            common_records=list(common),
            control_analysis=control_analysis,
            test_analysis=test_analysis,
            owner=None,
            control_owner=(control_owners_list[0] if control_owners_list else "Unknown"),
            test_owner=test_owners_list[0] if test_owners_list else "Unknown",
        )

    ttl_diff: int = abs((test.get("ttl") or 0) - (control.get("ttl") or 0))
    if ttl_diff > 3600:
        return InconsistencyDetail(
            server=server,
            server_name=SERVER_NAMES.get(server, "Unknown"),
            server_country=SERVER_COUNTRIES.get(server, "Unknown"),
            type="ttl_mismatch",
            severity="low",
            control_error=control.get("error"),
            test_error=test.get("error"),
            control_records=control.get("records", []),
            test_records=test.get("records", []),
            control_ttl=control.get("ttl"),
            test_ttl=test.get("ttl"),
            diff=ttl_diff,
            common_records=control.get("records", []),
            control_analysis=control_analysis,
            test_analysis=test_analysis,
            owner=None,
            control_owner=None,
            test_owner=None,
        )

    return None


def check_dns_poisoning(
    domain: str,
    control_server: str = "8.8.8.8",
    test_servers: list[str] | None = None,
    record_type: str = "A",
    additional_types: list[str] | None = None,
    timeout_config: TimeoutConfig | None = None,
) -> PoisoningCheckResult:
    """
    Check for DNS poisoning, censorship, or manipulation.

    Queries the trusted *control_server* and compares its response against
    multiple test servers. CDN and anycast patterns are classified separately
    from true poisoning.

    Args:
        domain: Domain to test (e.g. ``"example.com"``).
        control_server: Trusted DNS server IP used as the baseline.
            Defaults to ``"8.8.8.8"`` (Google DNS).
        test_servers: Test server IPs. ``None`` uses
            :func:`~nadzoring.dns_lookup.utils.get_public_dns_servers`.
        record_type: Record type to query. Defaults to ``"A"``.
        additional_types: Extra record types to query on the control server
            for additional context.
        timeout_config: Unified timeout configuration. If None, uses default.

    Returns:
        :class:`PoisoningCheckResult` with comprehensive analysis fields.

    Examples:
        >>> result = check_dns_poisoning("example.com")
        >>> if result["poisoned"]:
        ...     print(f"Confidence: {result['confidence']}%")

        >>> result = check_dns_poisoning("example.com", test_servers=["1.1.1.1", "9.9.9.9"])

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    if test_servers is None:
        test_servers = get_public_dns_servers()

    record_type_literal: RecordType = "A" if record_type == "A" else record_type  # type: ignore

    control_result: DNSResult = resolve_with_timer(
        domain,
        record_type_literal,
        control_server,
        include_ttl=True,
        timeout_config=timeout_config,
    )

    additional_results: dict[str, DNSResult] | None = _get_additional_records(
        domain,
        additional_types,
        control_server,
        timeout_config,
    )

    test_results, inconsistencies, mismatches, cdn_variations = _test_dns_servers(
        domain,
        record_type_literal,
        test_servers,
        control_result,
        control_server,
        timeout_config,
    )

    metrics: MetricsResult = _calculate_metrics(test_results, control_result, mismatches, cdn_variations)

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
    domain: str,
    additional_types: list[str] | None,
    control_server: str,
    timeout_config: TimeoutConfig,
) -> dict[str, DNSResult] | None:
    """
    Retrieve supplementary DNS record types from the control server.

    Args:
        domain: Domain name to query.
        additional_types: Record types to query, or ``None`` to skip.
        control_server: Control server IP address.
        timeout_config: Unified timeout configuration.

    Returns:
        Dict mapping record types to results, or ``None`` when
        *additional_types* is empty/``None``.

    """
    if not additional_types:
        return None
    result: dict[str, DNSResult] = {}
    for rtype in additional_types:
        rtype_literal: RecordType = rtype  # type: ignore
        result[rtype] = resolve_with_timer(
            domain,
            rtype_literal,
            control_server,
            include_ttl=True,
            timeout_config=timeout_config,
        )
    return result


def _test_dns_servers(
    domain: str,
    record_type: RecordType,
    test_servers: list[str],
    control_result: DNSResult,
    control_server: str,
    timeout_config: TimeoutConfig,
) -> tuple[dict[str, DNSResult], list[InconsistencyDetail], int, int]:
    """
    Query all test servers and collect comparison results.

    The control server itself is skipped if it appears in *test_servers*.

    Args:
        domain: Domain to query.
        record_type: DNS record type to query.
        test_servers: Test server IP addresses.
        control_result: Result from the control server for comparison.
        control_server: Control server IP (skipped when encountered in list).
        timeout_config: Unified timeout configuration.

    Returns:
        Four-tuple of ``(test_results, inconsistencies, mismatches,
        cdn_variations)``.

    """
    test_results: dict[str, DNSResult] = {}
    inconsistencies: list[InconsistencyDetail] = []
    mismatches = 0
    cdn_variations = 0

    for server in test_servers:
        if server == control_server:
            continue

        test_result: DNSResult = resolve_with_timer(
            domain,
            record_type,
            server,
            include_ttl=True,
            timeout_config=timeout_config,
        )
        test_results[server] = test_result

        inconsistency: InconsistencyDetail | None = _compare_results(control_result, test_result, server)
        if inconsistency is None:
            continue

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
    Compute poisoning-detection metrics from test results.

    Args:
        test_results: Dict mapping server IPs to DNS results.
        control_result: Control server DNS result.
        mismatches: Count of record mismatches.
        cdn_variations: Count of CDN-related variations.

    Returns:
        :class:`MetricsResult` with confidence, diversity, and detection flags.

    """
    total: int = len(test_results)

    all_ips: list[str] = [ip for res in test_results.values() for ip in res.get("records", [])]

    is_cdn, cdn_owner, cdn_percentage = is_likely_cdn(all_ips)

    if is_cdn:
        poisoned: bool = mismatches > 0 and cdn_percentage < 50
        confidence: float = mismatches / total * 100 * (1 - cdn_percentage / 100) if total > 0 else 0.0
    else:
        poisoned = mismatches > 0
        confidence = (mismatches / total * 100) if total > 0 else 0.0

    control_ips: set[str] = set(control_result.get("records", []))
    all_test_ips: set[str] = {ip for res in test_results.values() for ip in res.get("records", [])}

    ip_counter: Counter[str] = Counter(ip for res in test_results.values() for ip in res.get("records", []))
    top_consensus: list[tuple[str, int]] = ip_counter.most_common(3)
    consensus_rate: float = (top_consensus[0][1] / total * 100) if top_consensus and total > 0 else 0.0

    geo_diversity: int = len({SERVER_COUNTRIES.get(s, "Unknown") for s in test_results})

    return {
        "total_tested": total,
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
        "poisoning_likely": (mismatches == total and not is_cdn and len(control_ips) > 1 and len(all_test_ips) == 1),
    }


def _determine_poisoning_level(
    confidence: float,
    *,
    poisoned: bool,
    cdn_detected: bool,
) -> str:
    """
    Map confidence and detection flags to a poisoning severity label.

    Args:
        confidence: Confidence score (0-100).
        poisoned: Whether poisoning indicators exceed the threshold.
        cdn_detected: Whether CDN usage was identified.

    Returns:
        One of ``"NONE"``, ``"LOW"``, ``"MEDIUM"``, ``"HIGH"``,
        ``"CRITICAL"``, or ``"SUSPICIOUS"``.

    """
    if not poisoned:
        return "NONE"
    if cdn_detected:
        return "SUSPICIOUS" if confidence > 80 else "LOW"
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
    Assemble the final :class:`PoisoningCheckResult` from collected data.

    Args:
        domain: Tested domain name.
        record_type: DNS record type queried.
        control_server: Control server IP.
        control_result: DNS result from the control server.
        test_results: Dict of test server results.
        additional_results: Optional supplementary record results.
        inconsistencies: Detected inconsistencies.
        mismatches: Count of record mismatches.
        cdn_variations: Count of CDN variations.
        metrics: Aggregated metrics from :func:`_calculate_metrics`.
        poisoning_level: Poisoning severity label.

    Returns:
        Complete :class:`PoisoningCheckResult`.

    """
    control_analysis: IPAnalysisResult = _analyze_ip_patterns(control_result.get("records", []))
    control_owners: list[str] = control_analysis.get("owners", [])

    formatted_consensus: list[dict[str, float | int | str]] = [
        {
            "ip": ip,
            "count": count,
            "percentage": (round(count / metrics["total_tested"] * 100, 1) if metrics["total_tested"] > 0 else 0.0),
            "owner": get_ip_owner(ip),
        }
        for ip, count in metrics["consensus_top"]
    ]

    result: PoisoningCheckResult = {
        "domain": domain,
        "record_type": record_type,
        "control_server": control_server,
        "control_name": SERVER_NAMES.get(control_server, "Unknown"),
        "control_country": SERVER_COUNTRIES.get(control_server, "Unknown"),
        "control_result": control_result,
        "control_analysis": dict(control_analysis),
        "control_owner": control_owners[0] if control_owners else "Unknown",
        "additional_records": additional_results,
        "test_results": test_results,
        "test_servers_count": metrics["total_tested"],
        "inconsistencies": [dict(inc) for inc in inconsistencies],
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
    return result


def _count_severities(inconsistencies: list[InconsistencyDetail]) -> dict[str, int]:
    """
    Aggregate inconsistency counts by severity level.

    Args:
        inconsistencies: List of inconsistency detail dicts.

    Returns:
        Dict with ``"high"``, ``"medium"``, ``"low"``, and ``"info"`` keys.

    """
    counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for inc in inconsistencies:
        counts[inc.get("severity", "low")] += 1
    return counts
