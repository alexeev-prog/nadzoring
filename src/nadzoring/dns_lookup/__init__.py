"""DNS lookup module for domain name resolution and DNS record checking."""

from nadzoring.dns_lookup.benchmark import benchmark_dns_servers
from nadzoring.dns_lookup.compare import compare_dns_servers
from nadzoring.dns_lookup.health import check_dns, health_check_dns
from nadzoring.dns_lookup.poisoning import check_dns_poisoning
from nadzoring.dns_lookup.reverse import reverse_dns
from nadzoring.dns_lookup.trace import trace_dns
from nadzoring.dns_lookup.types import RECORD_TYPES
from nadzoring.dns_lookup.utils import resolve_with_timer as resolve_dns

__all__: list[str] = [
    "RECORD_TYPES",
    "benchmark_dns_servers",
    "check_dns",
    "check_dns_poisoning",
    "compare_dns_servers",
    "health_check_dns",
    "resolve_dns",
    "reverse_dns",
    "trace_dns",
]
