# nadzoring/dns_lookup/reverse.py
"""Reverse DNS lookup functionality."""

from time import time

import dns.exception
import dns.resolver
import dns.reversename
from dns.name import Name
from dns.resolver import Answer

from nadzoring.dns_lookup.utils import create_resolver
from nadzoring.logger import get_logger

logger = get_logger(__name__)


def reverse_dns(
    ip_address: str,
    nameserver: str | None = None,
) -> dict[str, str | float | None]:
    """Perform reverse DNS lookup."""
    result: dict[str, str | float | None] = {
        "ip_address": ip_address,
        "hostname": None,
        "error": None,
        "response_time": None,
    }

    try:
        resolver = create_resolver(nameserver)
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
