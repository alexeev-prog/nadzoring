"""DNS trace routing functionality for tracking resolution paths."""

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
    """
    Query a specific nameserver for A records of a domain.

    Performs a DNS A record lookup against a specified nameserver, measuring
    response time and handling various error conditions gracefully.

    Args:
        domain: Domain name to query (e.g., "example.com").
        nameserver: IP address of the nameserver to query.

    Returns:
        Tuple[Optional[Answer], Optional[float], Optional[str]]: A tuple containing:
            - answers: DNS Answer object if successful, None otherwise.
            - response_time: Response time in milliseconds rounded to 2 decimals,
                           None if timeout occurred.
            - error: Error message string if resolution failed, None if successful.

    Examples:
        >>> answers, rt, error = query_nameserver("example.com", "8.8.8.8")
        >>> if answers:
        ...     print(f"Resolved in {rt}ms: {answers[0]}")
        >>> elif error:
        ...     print(f"Failed: {error}")

    Notes:
        - Timeout is set to 3 seconds per query with 5 seconds total lifetime
        - Response time is None only for timeout errors
        - For other errors, response time is still recorded
    """
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
    hop: dict[str, Any],
) -> str | None:
    """
    Get delegation information from a nameserver for the next hop.

    Queries a nameserver for NS records of the current domain to find
    delegation information, then resolves the nameserver IP for the next hop.

    Args:
        current_domain: Domain name as dns.name.Name object to query for NS records.
        current_ns: IP address of the current nameserver to query.
        hop: Hop dictionary to update with delegation records and errors.
            Modified in-place to add delegation information.

    Returns:
        Optional[str]: IP address of the next nameserver to query, or None if
                      delegation information cannot be obtained or resolved.

    Notes:
        - Uses UDP query for NS records with 5 second timeout
        - Attempts to resolve nameserver hostnames to IP addresses
        - Falls back to socket.gethostbyname() if dns.resolver fails
        - Logs exceptions but continues execution
    """
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


def create_hop(nameserver: str) -> dict[str, Any]:
    """
    Create a new hop dictionary for DNS trace tracking.

    Initializes a hop structure to store information about a single step
    in the DNS resolution path.

    Args:
        nameserver: IP address of the nameserver for this hop.

    Returns:
        Dict[str, Any]: Hop dictionary with the following structure:
            - nameserver: IP address of the queried nameserver
            - records: List of record strings obtained from this hop
            - response_time: Response time in milliseconds (None if not yet measured)
            - next: Next nameserver IP or status string (None if unknown)
            - error: Error message if this hop failed (None otherwise)

    Example:
        >>> hop = create_hop("198.41.0.4")
        >>> hop["records"].append("A record response")
        >>> hop["response_time"] = 45.67
    """
    return {
        "nameserver": nameserver,
        "records": [],
        "response_time": None,
        "next": None,
        "error": None,
    }


def trace_dns(domain: str, nameserver: str | None = None) -> dict[str, Any]:
    """
    Trace the complete DNS resolution path for a domain.

    Performs a DNS trace following the delegation chain from root servers
    to authoritative nameservers, similar to dig +trace functionality.

    Args:
        domain: Domain name to trace (e.g., "example.com").
        nameserver: Optional starting nameserver IP. If None, starts from
                   root server (198.41.0.4 - a.root-servers.net).

    Returns:
        Dict[str, Any]: Trace result containing:
            - domain: The domain that was traced
            - hops: List of hop dictionaries, each representing a nameserver
                   queried along the path
            - final_answer: The hop dictionary containing the final answer
                           (None if resolution failed)

    Example:
        >>> result = trace_dns("example.com")
        >>> for i, hop in enumerate(result["hops"]):
        ...     print(f"Hop {i + 1}: {hop['nameserver']} ({hop['response_time']}ms)")
        >>> if result["final_answer"]:
        ...     print(f"Final answer: {result['final_answer']['records']}")

    Notes:
        - Maximum hops limited to 30 to prevent infinite loops
        - Detects and reports loops in delegation chain
        - Tracks visited nameservers to avoid repetition
        - Gracefully handles delegation failures and errors
    """
    result: dict[str, Any] = {
        "domain": domain,
        "hops": [],
        "final_answer": None,
    }

    # Start from root server (a.root-servers.net) if no nameserver specified
    current_ns: str = nameserver or "198.41.0.4"
    current_domain: Name = dns.name.from_text(domain)
    max_hops = 30
    hop_count = 0
    visited_ns: set[str] = set()

    while hop_count < max_hops:
        hop_count += 1

        # Detect loops in delegation chain
        if current_ns in visited_ns:
            hop = create_hop(current_ns)
            hop["error"] = "Loop detected"
            hop["next"] = "Loop detected"
            result["hops"].append(hop)
            break

        visited_ns.add(current_ns)
        hop: dict[str, Any] = create_hop(current_ns)

        answers, response_time, error = query_nameserver(domain, current_ns)
        hop["response_time"] = response_time

        # If we got answers, we've reached an authoritative server
        if answers:
            for answer in answers:
                hop["records"].append(str(answer))
            hop["next"] = "Complete"
            result["final_answer"] = hop
            result["hops"].append(hop)
            break

        # Try to get delegation to next nameserver
        next_ns: str | None = get_delegation_info(current_domain, current_ns, hop)

        if error:
            hop["error"] = error

        # Move to next nameserver if delegation succeeded
        if next_ns and next_ns != current_ns:
            hop["next"] = next_ns
            result["hops"].append(hop)
            current_ns = next_ns
        else:
            hop["next"] = "No further delegation"
            result["hops"].append(hop)
            break

    return result
