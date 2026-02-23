# src/nadzoring/dns_lookup/dns_resolver.py
"""DNS resolution module."""

import socket
from logging import Logger
from time import time
from typing import Literal

import dns.message
import dns.name
import dns.query
import dns.rdatatype
import dns.resolver
import dns.reversename
from dns.message import Message, QueryMessage
from dns.name import Name
from dns.resolver import Answer, Resolver

from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

RecordType: type["RecordType"] = Literal["A", "AAAA", "CNAME", "MX", "NS", "TXT", "PTR"]
RECORD_TYPES: list[str] = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "PTR"]


def resolve_dns(
    domain: str,
    record_type: RecordType = "A",
    nameserver: str | None = None,
    *,
    include_ttl: bool = False,
) -> dict[str, any]:
    """Resolve DNS records for a given domain."""
    result: dict[str, list[str] | str | None] = {
        "domain": domain,
        "record_type": record_type,
        "records": [],
        "ttl": None,
        "error": None,
        "response_time": None,
    }

    try:
        resolver = dns.resolver.Resolver()
        if nameserver:
            resolver.nameservers = [nameserver]

        start_time: float = time()
        answers: Answer = resolver.resolve(domain, record_type)
        result["response_time"] = round((time() - start_time) * 1000, 2)

        if answers.rrset and include_ttl:
            result["ttl"] = answers.rrset.ttl

        for answer in answers:
            if record_type == "MX":
                result["records"].append(
                    f"{answer.preference} {answer.exchange}".rstrip(".")
                )
            elif record_type == "TXT":
                txt_parts: list[str] = [
                    part.decode("utf-8") if isinstance(part, bytes) else str(part)
                    for part in answer.strings
                ]
                result["records"].append("".join(txt_parts))
            else:
                result["records"].append(str(answer).rstrip("."))

    except dns.resolver.NoAnswer:
        result["error"] = f"No {record_type} records"
    except dns.resolver.NXDOMAIN:
        result["error"] = "Domain does not exist"
    except dns.exception.Timeout:
        result["error"] = "Query timeout"
        logger.debug("DNS query timeout for %s", domain)
    except Exception as e:
        result["error"] = str(e)
        logger.debug("DNS resolution failed for %s: %s", domain, e)

    return result


def query_nameserver(
    domain: str, nameserver: str
) -> tuple[Answer | None, float | None, str | None]:
    """Query a nameserver for A records."""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [nameserver]
    resolver.timeout = 3
    resolver.lifetime = 5

    start_time: float = time()

    try:
        answers: Answer = resolver.resolve(domain, "A")
        response_time: float = round((time() - start_time) * 1000, 2)
    except dns.resolver.NXDOMAIN:
        response_time: float = round((time() - start_time) * 1000, 2)
        return None, response_time, "Domain does not exist"
    except dns.resolver.NoAnswer:
        response_time: float = round((time() - start_time) * 1000, 2)
        return None, response_time, "No answer"
    except dns.exception.Timeout:
        return None, None, "Timeout"
    except Exception as e:
        response_time: float = round((time() - start_time) * 1000, 2)
        return None, response_time, str(e)
    else:
        return answers, response_time, None


def get_delegation_info(current_domain: Name, current_ns: str, hop: dict) -> str | None:
    """Get delegation information from nameserver."""
    try:
        ns_query: QueryMessage = dns.message.make_query(
            current_domain, dns.rdatatype.NS
        )
        response: Message = dns.query.udp(ns_query, current_ns, timeout=5)

        for rrset in response.authority:
            if rrset.rdtype == dns.rdatatype.NS:
                for rr in rrset:
                    ns_name = str(rr.target)
                    try:
                        ns_ip_answer: Answer = dns.resolver.resolve(
                            ns_name, "A", lifetime=3
                        )
                        if ns_ip_answer:
                            ns_ip = str(ns_ip_answer[0])
                            hop["records"].append(f"Delegation to {ns_name} ({ns_ip})")
                            return ns_ip
                    except Exception:
                        hop["records"].append(f"Delegation to {ns_name}")
                        try:
                            return socket.gethostbyname(ns_name)
                        except Exception:
                            logger.exception(
                                "Raised exception when getted delegation info"
                            )
    except Exception as e:
        hop["error"] = f"Delegation error: {e!s}"

    return None


def create_hop(nameserver: str) -> dict:
    """Create a new hop dictionary."""
    return {
        "nameserver": nameserver,
        "records": [],
        "response_time": None,
        "next": None,
        "error": None,
    }


def trace_dns(domain: str, nameserver: str | None = None) -> dict[str, any]:
    """Trace the DNS resolution path."""
    result: dict[str, list[str] | str | None] = {
        "domain": domain,
        "hops": [],
        "final_answer": None,
    }

    current_ns: str = nameserver or "198.41.0.4"  # a.root-servers.net
    current_domain: Name = dns.name.from_text(domain)
    max_hops = 30
    hop_count = 0
    visited_ns: set[str] = set()

    while hop_count < max_hops:
        hop_count += 1

        if current_ns in visited_ns:
            hop = create_hop(current_ns)
            hop["error"] = "Loop detected"
            hop["next"] = "Loop detected"
            result["hops"].append(hop)
            break

        visited_ns.add(current_ns)
        hop: dict[str, str | list[str] | int] = create_hop(current_ns)

        answers, response_time, error = query_nameserver(domain, current_ns)
        hop["response_time"] = response_time

        if answers:
            for answer in answers:
                hop["records"].append(str(answer))
            hop["next"] = "Complete"
            result["final_answer"] = hop
            result["hops"].append(hop)
            break

        next_ns: str | None = get_delegation_info(current_domain, current_ns, hop)

        if error:
            hop["error"] = error

        if next_ns and next_ns != current_ns:
            hop["next"] = next_ns
            result["hops"].append(hop)
            current_ns = next_ns
        else:
            hop["next"] = "No further delegation"
            result["hops"].append(hop)
            break

    return result


def compare_dns_servers(
    domain: str,
    servers: list[str],
    record_types: list[str],
    progress_callback=None,
) -> dict[str, any]:
    """Compare DNS responses from different servers."""
    result: dict[str, dict[str, str] | list[int] | str] = {
        "domain": domain,
        "servers": {},
        "differences": [],
    }

    for i, server in enumerate(servers):
        server_results: dict[str, dict[str, bool]] = {}

        for rtype in record_types:
            query_result: dict[str, bool] = resolve_dns(
                domain, rtype, server, include_ttl=True
            )
            server_results[rtype] = query_result

            if i == 0:
                query_result["differs"] = False
            else:
                base = result["servers"][servers[0]].get(rtype, {})
                differs: bool = query_result.get("records") != base.get("records")
                query_result["differs"] = differs
                if differs:
                    result["differences"].append(
                        {
                            "server": server,
                            "type": rtype,
                            "expected": base.get("records"),
                            "got": query_result.get("records"),
                        }
                    )

            if progress_callback:
                progress_callback()

        result["servers"][server] = server_results

    return result


def _calculate_record_score(rtype: str, record_result: dict, result: dict) -> int:
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

    return _apply_rtype_specific_checks(rtype, record_result, record_score, result)


def _apply_rtype_specific_checks(
    rtype: str, record_result: dict, record_score: int, result: dict
) -> int:
    """Apply record-type specific validation rules."""
    if rtype == "MX" and record_result.get("records"):
        record_score = _check_mx_priorities(
            record_result["records"], record_score, result
        )

    elif rtype == "TXT" and record_result.get("records"):
        record_score = _check_txt_records(
            record_result["records"], record_score, result
        )

    return record_score


def _check_mx_priorities(records: list, record_score: int, result: dict) -> int:
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


def _check_txt_records(records: list, record_score: int, result: dict) -> int:
    """Check TXT records for SPF and DKIM compliance."""
    for txt in records:
        if txt.startswith("v=spf1"):
            record_score = _check_spf_record(txt, record_score, result)
        elif txt.startswith("v=DKIM1"):
            record_score = _check_dkim_record(txt, record_score, result)
    return record_score


def _check_spf_record(txt: str, record_score: int, result: dict) -> int:
    """Validate SPF record."""
    if "~all" not in txt and "-all" not in txt:
        record_score -= 10
        result["warnings"].append("SPF record missing softfail/hardfail")
    return record_score


def _check_dkim_record(txt: str, record_score: int, result: dict) -> int:
    """Validate DKIM record."""
    if "p=" not in txt:
        record_score -= 20
        result["issues"].append("DKIM record missing public key")
    return record_score


def _determine_status(score: int) -> str:
    """Determine health status based on score."""
    if score >= 80:
        return "healthy"
    if score >= 50:
        return "degraded"
    return "unhealthy"


def health_check_dns(domain: str, nameserver: str | None = None) -> dict[str, any]:
    """Perform comprehensive DNS health check."""
    result: dict[str, dict[str, str] | int | list[str] | list[int] | str] = {
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
        record_result: dict[str, int] = resolve_dns(domain, rtype, nameserver)

        if rtype == "CNAME" and not is_subdomain:
            if record_result.get("records"):
                record_score = 100
            else:
                record_score = 100
                continue
        else:
            record_score: int = _calculate_record_score(rtype, record_result, result)
            total_score += record_score
            record_count += 1

        result["record_scores"][rtype] = max(0, record_score)

    result["score"] = total_score // record_count if record_count > 0 else 0
    result["status"] = _determine_status(result["score"])

    return result


def reverse_dns(ip_address: str, nameserver: str | None = None) -> dict[str, any]:
    """Perform reverse DNS lookup."""
    result: dict[str, str | None] = {
        "ip_address": ip_address,
        "hostname": None,
        "error": None,
        "response_time": None,
    }

    try:
        resolver = dns.resolver.Resolver()
        if nameserver:
            resolver.nameservers = [nameserver]

        reverse_name: Name = dns.reversename.from_address(ip_address)
        start_time: float = time()
        answers: Answer = resolver.resolve(reverse_name, "PTR")
        result["response_time"] = round((time() - start_time) * 1000, 2)

        if answers:
            result["hostname"] = str(answers[0]).rstrip(".")

    except dns.resolver.NoAnswer:
        result["error"] = "No PTR record"
    except dns.resolver.NXDOMAIN:
        result["error"] = "No reverse DNS"
    except Exception as e:
        result["error"] = str(e)
        logger.debug("Reverse DNS failed for %s: %s", ip_address, e)

    return result


def _create_resolver(nameserver: str | None) -> dns.resolver.Resolver:
    """Create and configure DNS resolver."""
    resolver = dns.resolver.Resolver()
    if nameserver:
        resolver.nameservers = [nameserver]
    return resolver


def _process_record_type(
    resolver: dns.resolver.Resolver,
    domain: str,
    record_type: str,
    results: dict,
    *,
    validate_mx: bool,
    validate_txt: bool,
) -> None:
    """Process a single DNS record type."""
    try:
        start_time: float = time()
        answers: Answer = resolver.resolve(domain, record_type)
        response_time: float = round((time() - start_time) * 1000, 2)

        records: list[str] = _extract_records(answers, record_type)

        if records:
            results["records"][record_type] = records
            results["response_times"][record_type] = response_time
            _handle_validations(
                records, record_type, results, validate_mx, validate_txt
            )

    except dns.resolver.NoAnswer:
        results["errors"][record_type] = f"No {record_type} records"
    except Exception as e:
        results["errors"][record_type] = str(e)


def _extract_records(answers: Answer, record_type: str) -> list[str]:
    """Extract records from DNS answer."""
    records: list[str] = []
    for answer in answers:
        if record_type == "MX":
            records.append(f"{answer.preference} {answer.exchange}".rstrip("."))
        elif record_type == "TXT":
            txt_parts: list[str] = [
                part.decode("utf-8") if isinstance(part, bytes) else str(part)
                for part in answer.strings
            ]
            records.append("".join(txt_parts))
        else:
            records.append(str(answer).rstrip("."))
    return records


def _handle_validations(
    records: list[str],
    record_type: str,
    results: dict,
    *,
    validate_mx: bool,
    validate_txt: bool,
) -> None:
    """Handle validations for MX and TXT records."""
    if validate_mx and record_type == "MX":
        results["validations"]["mx"] = validate_mx_records(records)
    elif validate_txt and record_type == "TXT":
        results["validations"]["txt"] = validate_txt_records(records)


def check_dns(
    domain: str,
    nameserver: str | None = None,
    record_types: list[str] | None = None,
    *,
    validate_mx: bool = False,
    validate_txt: bool = False,
) -> dict[str, any]:
    """Comprehensive DNS check."""
    if record_types is None:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]

    results: dict[str, dict[str, list[str]] | dict[str, str | int] | str] = {
        "domain": domain,
        "records": {},
        "errors": {},
        "response_times": {},
        "validations": {},
    }

    resolver: Resolver = _create_resolver(nameserver)

    for record_type in record_types:
        _process_record_type(
            resolver,
            domain,
            record_type,
            results,
            validate_mx=validate_mx,
            validate_txt=validate_txt,
        )

    return results


def validate_mx_records(mx_records: list[str]) -> dict[str, any]:
    """Validate MX records."""
    validation: dict[str, bool | list[int]] = {
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


def validate_txt_records(txt_records: list[str]) -> dict[str, any]:
    """Validate TXT records (SPF, DKIM)."""
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

    return validation
