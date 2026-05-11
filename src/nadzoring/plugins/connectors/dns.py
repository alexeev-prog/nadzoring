"""DNS category connectors — wraps every command from ``nadzoring dns``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from nadzoring.dns_lookup.types import RecordType
from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.result import ProbeResult
from nadzoring.utils.timeout import TimeoutConfig

# Re-used tag tuple
_TAGS = ("dns", "network")


def _ok(data: Any, latency_ms: float | None = None) -> ProbeResult:
    return ProbeResult(status="ok", latency_ms=latency_ms, details={"data": data})


def _err(msg: str) -> ProbeResult:
    return ProbeResult(status="error", error=msg)


# ---------------------------------------------------------------------------
# dns resolve
# ---------------------------------------------------------------------------


@dataclass
class DnsResolveConnector(ConnectorBase):
    """Resolve DNS records for one or more domains.

    Wraps :func:`nadzoring.dns_lookup.resolve_dns`.

    Attributes:
        domains: List of domains to query.
        record_types: DNS record types to look up (e.g. ``["A", "MX"]``).
            Defaults to ``["A"]``.
        nameserver: Custom resolver IP. ``None`` uses the system default.
        include_ttl: Include TTL values in results.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="dns-resolve",
        category=ConnectorCategory.NETWORK,
        description="Resolves DNS records for given domains.",
        tags=_TAGS,
    )

    domains: list[str]
    record_types: list[str] = field(default_factory=lambda: ["A"])
    nameserver: str | None = None
    include_ttl: bool = False
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.dns_lookup import resolve_dns

        results = []
        errors = []
        for domain in self.domains:
            for rtype in self.record_types:
                res = resolve_dns(
                    domain,
                    cast(RecordType, rtype),
                    self.nameserver,
                    self.timeout_config,
                    include_ttl=self.include_ttl,
                )
                if res.get("error"):
                    errors.append(f"{domain}/{rtype}: {res['error']}")
                else:
                    results.append(res)

        if errors and not results:
            return _err("; ".join(errors))
        return ProbeResult(
            status="ok" if not errors else "degraded",
            error="; ".join(errors) if errors else None,
            details={"data": results},
        )


# ---------------------------------------------------------------------------
# dns reverse
# ---------------------------------------------------------------------------


@dataclass
class DnsReverseConnector(ConnectorBase):
    """Perform reverse DNS (PTR) lookups on IP addresses.

    Wraps :func:`nadzoring.dns_lookup.reverse_dns`.

    Attributes:
        ip_addresses: IPs to look up.
        nameserver: Custom resolver IP.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="dns-reverse",
        category=ConnectorCategory.NETWORK,
        description="Performs reverse DNS (PTR) lookups.",
        tags=_TAGS,
    )

    ip_addresses: list[str]
    nameserver: str | None = None
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.dns_lookup import reverse_dns

        results = []
        errors = []
        for ip in self.ip_addresses:
            res = reverse_dns(ip, self.nameserver)
            if res.get("error"):
                errors.append(f"{ip}: {res['error']}")
            else:
                results.append(res)

        if errors and not results:
            return _err("; ".join(errors))
        return ProbeResult(
            status="ok" if not errors else "degraded",
            error="; ".join(errors) if errors else None,
            details={"data": results},
        )


# ---------------------------------------------------------------------------
# dns health
# ---------------------------------------------------------------------------


@dataclass
class DnsHealthConnector(ConnectorBase):
    """Run a DNS health check on a domain.

    Wraps :func:`nadzoring.dns_lookup.health_check_dns`.

    Attributes:
        domain: Domain to check.
        nameserver: Custom resolver IP.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="dns-health",
        category=ConnectorCategory.NETWORK,
        description="Runs DNS health check (SOA, NS, MX reachability).",
        tags=_TAGS,
    )

    domain: str
    nameserver: str | None = None
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.dns_lookup import health_check_dns

        res = health_check_dns(self.domain, self.nameserver, self.timeout_config)
        if res.get("error"):
            return _err(str(res["error"]))
        status = str(res.get("status", "healthy"))
        healthy = status == "healthy"
        return ProbeResult(
            status="ok" if healthy else "degraded",
            error=None if healthy else f"DNS health status: {status}",
            details={"data": dict(res)},
        )


# ---------------------------------------------------------------------------
# dns benchmark
# ---------------------------------------------------------------------------


@dataclass
class DnsBenchmarkConnector(ConnectorBase):
    """Benchmark multiple DNS servers for a given domain.

    Wraps :func:`nadzoring.dns_lookup.benchmark_dns_servers`.

    Attributes:
        domain: Domain used for benchmark queries.
        servers: DNS server IPs to benchmark.
        record_type: DNS record type to query. Defaults to ``"A"``.
        queries: Number of queries per server.
        parallel: Run queries in parallel when ``True``.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="dns-benchmark",
        category=ConnectorCategory.NETWORK,
        description="Benchmarks response times across DNS servers.",
        tags=_TAGS,
    )

    domain: str
    servers: list[str] = field(default_factory=lambda: ["8.8.8.8", "1.1.1.1", "9.9.9.9"])
    record_type: str = "A"
    queries: int = 10
    parallel: bool = True
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.dns_lookup import benchmark_dns_servers

        results = benchmark_dns_servers(
            self.domain,
            self.servers,
            cast(RecordType, self.record_type),
            self.queries,
            20,
            None,
            parallel=self.parallel,
            timeout_config=self.timeout_config,
        )
        degraded = any(r["failed_queries"] > 0 for r in results)
        return ProbeResult(
            status="ok" if not degraded else "degraded",
            error="One or more benchmark servers reported failed queries" if degraded else None,
            details={"data": results},
        )


# ---------------------------------------------------------------------------
# dns compare
# ---------------------------------------------------------------------------


@dataclass
class DnsCompareConnector(ConnectorBase):
    """Compare DNS responses across multiple servers.

    Wraps :func:`nadzoring.dns_lookup.compare_dns_servers`.

    Attributes:
        domain: Domain to compare.
        servers: DNS servers to compare.
        record_types: Record types to include in comparison.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="dns-compare",
        category=ConnectorCategory.NETWORK,
        description="Compares DNS responses across multiple resolvers.",
        tags=_TAGS,
    )

    domain: str
    servers: list[str] = field(default_factory=lambda: ["8.8.8.8", "1.1.1.1", "9.9.9.9"])
    record_types: list[str] = field(default_factory=lambda: ["A"])
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.dns_lookup import compare_dns_servers

        result = compare_dns_servers(
            self.domain,
            self.servers,
            self.record_types,
            None,
            self.timeout_config,
        )
        differences = result.get("differences", [])
        consistent = len(differences) == 0
        return ProbeResult(
            status="ok" if consistent else "degraded",
            error=None if consistent else "DNS responses are inconsistent across servers",
            details={"data": result},
        )


# ---------------------------------------------------------------------------
# dns poisoning
# ---------------------------------------------------------------------------


@dataclass
class DnsPoisoningConnector(ConnectorBase):
    """Check for DNS cache poisoning on a domain.

    Wraps :func:`nadzoring.dns_lookup.check_dns_poisoning`.

    Attributes:
        domain: Domain to check.
        control_server: Trusted reference DNS server.
        test_servers: Servers to test against the control.
        record_type: Primary record type to check.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="dns-poisoning",
        category=ConnectorCategory.NETWORK,
        description="Detects potential DNS cache poisoning.",
        tags=(*_TAGS, "security"),
    )

    domain: str
    control_server: str = "8.8.8.8"
    test_servers: list[str] = field(default_factory=lambda: ["1.1.1.1", "9.9.9.9"])
    record_type: str = "A"
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.dns_lookup import check_dns_poisoning

        result = check_dns_poisoning(
            self.domain,
            self.control_server,
            self.test_servers,
            self.record_type,
            [],
            self.timeout_config,
        )
        poisoned = bool(result.get("poisoned") or result.get("poisoning_likely"))
        return ProbeResult(
            status="error" if poisoned else "ok",
            error="DNS poisoning indicators detected" if poisoned else None,
            details={"data": result},
        )


# ---------------------------------------------------------------------------
# dns trace
# ---------------------------------------------------------------------------


@dataclass
class DnsTraceConnector(ConnectorBase):
    """Trace the DNS delegation chain for a domain.

    Wraps :func:`nadzoring.dns_lookup.trace_dns`.

    Attributes:
        domain: Domain to trace.
        nameserver: Starting resolver IP.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="dns-trace",
        category=ConnectorCategory.NETWORK,
        description="Traces DNS delegation chain from root to authoritative.",
        tags=_TAGS,
    )

    domain: str
    nameserver: str | None = None
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.dns_lookup import trace_dns

        result = trace_dns(self.domain, self.nameserver, self.timeout_config)
        if result.get("error"):
            return _err(str(result["error"]))
        return _ok(result)


# ---------------------------------------------------------------------------
# dns whois
# ---------------------------------------------------------------------------


@dataclass
class DnsWhoisConnector(ConnectorBase):
    """Query WHOIS information for a domain.

    Wraps :func:`nadzoring.network_base.whois_lookup.whois_domain_lookup`.

    Attributes:
        domain: Domain to look up.
    """

    meta = ConnectorMeta(
        name="dns-whois",
        category=ConnectorCategory.NETWORK,
        description="Retrieves WHOIS registration data for a domain.",
        tags=(*_TAGS, "whois"),
    )

    domain: str

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.whois_lookup import whois_domain_lookup

        data = whois_domain_lookup(self.domain)
        if data and isinstance(data[0], dict) and data[0].get("error"):
            return _err(str(data[0]["error"]))
        return _ok(data)
