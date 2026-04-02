"""DNS trace routing for tracking the full resolution delegation chain."""

import socket
from logging import Logger
from time import time
from typing import Any

import dns.exception
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
from nadzoring.utils.timeout import TimeoutConfig

logger: Logger = get_logger(__name__)

_ROOT_NAMESERVER = "198.41.0.4"
_MAX_HOPS = 30
_DELEGATION_TIMEOUT = 5

_TRACE_CONNECT_TIMEOUT = 5.0
_TRACE_READ_TIMEOUT = 3.0
_TRACE_LIFETIME_TIMEOUT = 5.0


def _create_hop(nameserver: str) -> dict[str, Any]:
    """
    Initialise a new hop entry for DNS trace tracking.

    Args:
        nameserver: IP address of the nameserver for this hop.

    Returns:
        Dict with ``nameserver``, ``records``, ``response_time``, ``next``,
        and ``error`` keys set to their zero/null defaults.

    """
    return {
        "nameserver": nameserver,
        "records": [],
        "response_time": None,
        "next": None,
        "error": None,
    }


def _query_nameserver(
    domain: str,
    nameserver: str,
    timeout_config: TimeoutConfig,
) -> tuple[Answer | None, float | None, str | None]:
    """
    Query a specific nameserver for A records of *domain*.

    Args:
        domain: Domain name to query.
        nameserver: IP address of the nameserver to query.
        timeout_config: Unified timeout configuration.

    Returns:
        Three-tuple of ``(answers, response_time_ms, error_message)``.
        *response_time_ms* is ``None`` only on timeout; *error_message*
        is ``None`` on success.

    """
    resolver: Resolver = create_resolver(nameserver, timeout_config)
    start_time: float = time()

    try:
        answers: Answer = resolver.resolve(domain, "A")
        return answers, round((time() - start_time) * 1000, 2), None
    except dns.resolver.NXDOMAIN:
        return None, round((time() - start_time) * 1000, 2), "Domain does not exist"
    except dns.resolver.NoAnswer:
        return None, round((time() - start_time) * 1000, 2), "No answer"
    except dns.exception.Timeout:
        return None, None, "Timeout"
    except Exception as exc:
        return None, round((time() - start_time) * 1000, 2), str(exc)


def _get_delegation_info(
    current_domain: Name,
    current_ns: str,
    hop: dict[str, Any],
    timeout_config: TimeoutConfig,
) -> str | None:
    """
    Resolve the next-hop nameserver IP via NS delegation records.

    Args:
        current_domain: Domain to query for NS records.
        current_ns: IP address of the nameserver to ask.
        hop: Hop dict updated in-place with delegation record strings or
            an ``"error"`` key on failure.
        timeout_config: Unified timeout configuration.

    Returns:
        IP address of the next nameserver, or ``None`` when delegation
        cannot be determined.

    """
    try:
        ns_query: QueryMessage = dns.message.make_query(current_domain, dns.rdatatype.NS)
        response: Message = dns.query.udp(ns_query, current_ns, timeout=timeout_config.connect)

        for rrset in response.authority:
            if rrset.rdtype != dns.rdatatype.NS:
                continue

            for rr in rrset:
                ns_name = str(rr.target)
                try:
                    ns_ip_answer: Answer = dns.resolver.resolve(ns_name, "A", lifetime=timeout_config.read)
                    ns_ip = str(ns_ip_answer[0])
                    hop["records"].append(f"Delegation to {ns_name} ({ns_ip})")
                except Exception:
                    hop["records"].append(f"Delegation to {ns_name}")
                    try:
                        return socket.gethostbyname(ns_name)
                    except OSError:
                        logger.debug("Failed to resolve delegation NS %s", ns_name)
                else:
                    return ns_ip

    except Exception as exc:
        hop["error"] = f"Delegation error: {exc}"

    return None


def trace_dns(
    domain: str,
    nameserver: str | None = None,
    timeout_config: TimeoutConfig | None = None,
) -> dict[str, Any]:
    """
    Trace the complete DNS resolution path for *domain*.

    Follows the delegation chain from the specified (or root) nameserver to
    the authoritative answer, similar to ``dig +trace``. Loop detection and a
    maximum-hop limit prevent infinite recursion.

    Args:
        domain: Domain name to trace (e.g. ``"example.com"``).
        nameserver: Starting nameserver IP. Defaults to ``a.root-servers.net``
            (``198.41.0.4``) when ``None``.
        timeout_config: Unified timeout configuration. If None, uses trace-specific
            defaults (connect=5.0, read=3.0, lifetime=5.0).

    Returns:
        Dict with ``domain``, ``hops`` (list of hop dicts), and
        ``final_answer`` (the authoritative hop, or ``None``).

    Examples:
        >>> result = trace_dns("example.com")
        >>> for hop in result["hops"]:
        ...     print(hop["nameserver"], hop["response_time"])

    """
    if timeout_config is None:
        timeout_config = TimeoutConfig(
            connect=_TRACE_CONNECT_TIMEOUT,
            read=_TRACE_READ_TIMEOUT,
            lifetime=_TRACE_LIFETIME_TIMEOUT,
        )

    result: dict[str, Any] = {
        "domain": domain,
        "hops": [],
        "final_answer": None,
    }

    current_ns: str = nameserver or _ROOT_NAMESERVER
    current_domain: Name = dns.name.from_text(domain)
    visited: set[str] = set()

    for _ in range(_MAX_HOPS):
        if current_ns in visited:
            loop_hop: dict[str, Any] = _create_hop(current_ns)
            loop_hop["error"] = "Loop detected"
            loop_hop["next"] = "Loop detected"
            result["hops"].append(loop_hop)
            break

        visited.add(current_ns)
        hop: dict[str, Any] = _create_hop(current_ns)

        answers, response_time, error = _query_nameserver(domain, current_ns, timeout_config)
        hop["response_time"] = response_time

        if answers:
            hop["records"] = [str(a) for a in answers]
            hop["next"] = "Complete"
            result["final_answer"] = hop
            result["hops"].append(hop)
            break

        next_ns: str | None = _get_delegation_info(current_domain, current_ns, hop, timeout_config)

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
