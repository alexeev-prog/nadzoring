# nadzoring/dns_lookup/compare.py
"""DNS server comparison functionality."""

from collections.abc import Callable
from typing import Any

from nadzoring.dns_lookup.types import DNSResult
from nadzoring.dns_lookup.utils import resolve_with_timer


def compare_dns_servers(
    domain: str,
    servers: list[str],
    record_types: list[str],
    progress_callback: Callable | None = None,
) -> dict[str, Any]:
    """Compare DNS responses from different servers."""
    result: dict[str, Any] = {
        "domain": domain,
        "servers": {},
        "differences": [],
    }

    for i, server in enumerate(servers):
        server_results: dict[str, dict] = {}

        for rtype in record_types:
            query_result: DNSResult = resolve_with_timer(
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
