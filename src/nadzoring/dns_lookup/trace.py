# nadzoring/dns_lookup/trace.py
"""DNS trace routing functionality."""

import socket
from logging import Logger
from time import time
from typing import Any

import dns.message
import dns.name
import dns.query
import dns.rdatatype
import dns.resolver
from dns.message import Message, QueryMessage
from dns.name import Name
from dns.resolver import Answer, Resolver

from nadzoring.dns_lookup.utils import create_resolver
from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)


def query_nameserver(
    domain: str,
    nameserver: str,
) -> tuple[Answer | None, float | None, str | None]:
    """Query a nameserver for A records."""
    resolver: Resolver = create_resolver(nameserver, timeout=3, lifetime=5)
    start_time: float = time()

    try:
        answers: Answer = resolver.resolve(domain, "A")
        response_time: float = round((time() - start_time) * 1000, 2)
    except dns.resolver.NXDOMAIN:
        response_time = round((time() - start_time) * 1000, 2)
        return None, response_time, "Domain does not exist"
    except dns.resolver.NoAnswer:
        response_time = round((time() - start_time) * 1000, 2)
        return None, response_time, "No answer"
    except dns.exception.Timeout:
        return None, None, "Timeout"
    except Exception as e:
        response_time = round((time() - start_time) * 1000, 2)
        return None, response_time, str(e)
    else:
        return answers, response_time, None


def get_delegation_info(
    current_domain: Name,
    current_ns: str,
    hop: dict,
) -> str | None:
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
                            logger.exception("Failed to resolve nameserver IP")
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


def trace_dns(domain: str, nameserver: str | None = None) -> dict[str, Any]:
    """Trace the DNS resolution path."""
    result: dict[str, Any] = {
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
        hop: dict = create_hop(current_ns)

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
