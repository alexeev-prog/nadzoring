"""Network category connectors — wraps every command from ``nadzoring network-base``."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal, cast

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.result import ProbeResult
from nadzoring.utils.timeout import TimeoutConfig

_TAGS = ("network",)


def _ok(data: Any, latency_ms: float | None = None) -> ProbeResult:
    return ProbeResult(status="ok", latency_ms=latency_ms, details={"data": data})


def _err(msg: str) -> ProbeResult:
    return ProbeResult(status="error", error=msg)


# ---------------------------------------------------------------------------
# network ping
# ---------------------------------------------------------------------------


@dataclass
class PingConnector(ConnectorBase):
    """ICMP ping one or more hosts.

    Wraps :func:`nadzoring.network_base.ping_address.ping_addr`.

    Attributes:
        addresses: Hostnames or IPs to ping.
    """

    meta = ConnectorMeta(
        name="ping",
        category=ConnectorCategory.NETWORK,
        description="ICMP ping — checks host reachability.",
        tags=_TAGS,
    )

    addresses: list[str]

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.ping_address import ping_addr

        results = [{"address": addr, "is_pinged": ping_addr(addr)} for addr in self.addresses]
        failed = [r["address"] for r in results if not r["is_pinged"]]
        if failed:
            return ProbeResult(
                status="degraded" if len(failed) < len(results) else "unreachable",
                error=f"Unreachable: {', '.join(str(a) for a in failed)}",
                details={"data": results},
            )
        return _ok(results)


# ---------------------------------------------------------------------------
# network traceroute
# ---------------------------------------------------------------------------


@dataclass
class TracerouteConnector(ConnectorBase):
    """Run traceroute to one or more targets.

    Wraps :func:`nadzoring.network_base.traceroute.traceroute`.

    Attributes:
        targets: Hostnames or IPs to trace.
        max_hops: Maximum number of hops. Defaults to 30.
        use_sudo: Run traceroute with sudo (Linux ICMP mode).
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="traceroute",
        category=ConnectorCategory.NETWORK,
        description="Traces network path hop-by-hop to targets.",
        tags=_TAGS,
    )

    targets: list[str]
    max_hops: int = 30
    use_sudo: bool = field(default=False, kw_only=True)
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.traceroute import traceroute

        results = []
        for target in self.targets:
            hops = traceroute(
                target,
                max_hops=self.max_hops,
                per_hop_timeout=self.timeout_config.read,
                use_sudo=self.use_sudo,
            )
            results.append(
                {
                    "target": target,
                    "hops": [asdict(h) for h in hops],
                }
            )

        return ProbeResult(status="ok", details={"data": results})


# ---------------------------------------------------------------------------
# network port-scan
# ---------------------------------------------------------------------------


@dataclass
class PortScanConnector(ConnectorBase):
    """Scan TCP/UDP ports on one or more targets.

    Wraps :func:`nadzoring.network_base.port_scanner.scan_ports`.

    Attributes:
        targets: Hostnames or IPs to scan.
        mode: Scan profile — ``"fast"`` (top 100), ``"full"`` (1-65535),
            or ``"custom"`` (use ``ports``).
        ports: Port specification for custom mode (e.g. ``"22,80,443"`` or
            ``"1-1024"``). Ignored when ``mode != "custom"``.
        protocol: ``"tcp"`` or ``"udp"``. Defaults to ``"tcp"``.
        workers: Thread count. Defaults to 50.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="port-scan",
        category=ConnectorCategory.NETWORK,
        description="TCP/UDP port scanner.",
        tags=(*_TAGS, "scan", "security"),
    )

    targets: list[str]
    mode: str = "fast"
    ports: str = ""
    protocol: str = "tcp"
    workers: int = 50
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.port_scanner import ScanConfig, scan_ports

        mode = cast(Literal["fast", "full", "custom"], self.mode)
        custom_ports: list[int] | None = None
        port_range: tuple[int, int] | None = None
        effective_mode = mode
        spec = self.ports.strip()
        if spec:
            effective_mode = "custom"
            if "-" in spec and "," not in spec:
                start_s, end_s = spec.split("-", 1)
                if start_s.isdigit() and end_s.isdigit():
                    port_range = (int(start_s), int(end_s))
                else:
                    custom_ports = [
                        int(p) for p in spec.replace(" ", "").split(",") if p.isdigit()
                    ]
            else:
                custom_ports = [int(p) for p in spec.replace(" ", "").split(",") if p.isdigit()]

        config = ScanConfig(
            targets=self.targets,
            mode=effective_mode,
            protocol=cast(Literal["tcp", "udp"], self.protocol),
            custom_ports=custom_ports,
            port_range=port_range,
            timeout_config=self.timeout_config,
            max_workers=self.workers,
        )
        results = scan_ports(config)
        return _ok([asdict(r) for r in results])


# ---------------------------------------------------------------------------
# network http-ping
# ---------------------------------------------------------------------------


@dataclass
class HttpPingConnector(ConnectorBase):
    """Measure HTTP-level latency for one or more URLs.

    Wraps :func:`nadzoring.network_base.http_ping.http_ping`.

    Attributes:
        urls: URLs to probe.
        verify_ssl: Verify TLS certificates. Defaults to ``True``.
        follow_redirects: Follow HTTP redirects. Defaults to ``True``.
        include_headers: Include response headers in results.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="http-ping",
        category=ConnectorCategory.NETWORK,
        description="Measures DNS, TTFB, and total HTTP latency.",
        tags=(*_TAGS, "http", "web"),
    )

    urls: list[str]
    verify_ssl: bool = field(default=True, kw_only=True)
    follow_redirects: bool = field(default=True, kw_only=True)
    include_headers: bool = field(default=False, kw_only=True)
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.http_ping import http_ping

        results = []
        errors = []
        for url in self.urls:
            res = http_ping(
                url,
                self.timeout_config,
                verify_ssl=self.verify_ssl,
                follow_redirects=self.follow_redirects,
                include_headers=self.include_headers,
            )
            row = asdict(res)
            if res.error:
                errors.append(f"{url}: {res.error}")
            else:
                results.append(row)

        if errors and not results:
            return _err("; ".join(errors))

        avg_ms: float | None = None
        total_values: list[float] = [
            float(r["total_ms"]) for r in results if r.get("total_ms") is not None
        ]
        if total_values:
            avg_ms = sum(total_values) / len(total_values)

        return ProbeResult(
            status="ok" if not errors else "degraded",
            latency_ms=avg_ms,
            error="; ".join(errors) if errors else None,
            details={"data": results},
        )


# ---------------------------------------------------------------------------
# network whois
# ---------------------------------------------------------------------------


@dataclass
class WhoisConnector(ConnectorBase):
    """Run WHOIS lookup on domains or IPs.

    Wraps :func:`nadzoring.network_base.whois_lookup.whois_lookup`.

    Attributes:
        targets: Domains or IPs to query.
    """

    meta = ConnectorMeta(
        name="whois",
        category=ConnectorCategory.NETWORK,
        description="Retrieves raw WHOIS data for domains or IPs.",
        tags=(*_TAGS, "whois"),
    )

    targets: list[str]

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.whois_lookup import whois_lookup

        results = []
        errors = []
        for target in self.targets:
            data = whois_lookup(target)
            if data.get("error"):
                errors.append(f"{target}: {data['error']}")
            else:
                results.append({"target": target, "data": data})

        if errors and not results:
            return _err("; ".join(errors))
        return ProbeResult(
            status="ok" if not errors else "degraded",
            error="; ".join(errors) if errors else None,
            details={"data": results},
        )


# ---------------------------------------------------------------------------
# network geolocation
# ---------------------------------------------------------------------------


@dataclass
class GeolocationConnector(ConnectorBase):
    """Geolocate IP addresses.

    Wraps :func:`nadzoring.network_base.geolocation_ip.geo_ip`.

    Attributes:
        ip_addresses: IPs to geolocate.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="geolocation",
        category=ConnectorCategory.NETWORK,
        description="Geolocates IP addresses (country, city, coordinates).",
        tags=(*_TAGS, "geo"),
    )

    ip_addresses: list[str]
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.geolocation_ip import geo_ip

        results = []
        errors = []
        for ip in self.ip_addresses:
            res = geo_ip(ip)
            if not res:
                errors.append(f"{ip}: geolocation lookup failed or empty result")
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
# network connections
# ---------------------------------------------------------------------------


@dataclass
class ConnectionsConnector(ConnectorBase):
    """List active network connections on the local machine.

    Wraps :func:`nadzoring.network_base.connections.get_connections`.

    Attributes:
        protocol: ``"tcp"``, ``"udp"``, or ``"all"``. Defaults to ``"all"``.
        state_filter: Only return connections whose state contains this
            substring (e.g. ``"ESTABLISHED"``). ``None`` returns all.
        include_process: Include PID and process name when available.
    """

    meta = ConnectorMeta(
        name="connections",
        category=ConnectorCategory.NETWORK,
        description="Lists active TCP/UDP connections on the local host.",
        tags=(*_TAGS, "local"),
    )

    protocol: str = "all"
    state_filter: str | None = None
    include_process: bool = field(default=True, kw_only=True)

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.connections import get_connections

        data = get_connections(
            protocol=self.protocol,
            state_filter=self.state_filter,
            include_process=self.include_process,
        )
        return _ok([asdict(row) if hasattr(row, "__dataclass_fields__") else row for row in data])


# ---------------------------------------------------------------------------
# network tcp-port  (raw, no scanner — single port reachability)
# ---------------------------------------------------------------------------


@dataclass
class TcpPortConnector(ConnectorBase):
    """Check whether a single TCP port is open and accepting connections.

    Attributes:
        host: Hostname or IP address.
        port: TCP port number (1-65535).
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="tcp-port",
        category=ConnectorCategory.NETWORK,
        description="Checks whether a TCP port is open.",
        tags=(*_TAGS, "port", "tcp"),
    )

    host: str
    port: int
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        import socket
        import time

        start = time.perf_counter()
        try:
            with socket.create_connection(
                (self.host, self.port),
                timeout=self.timeout_config.connect,
            ):
                latency_ms = (time.perf_counter() - start) * 1000
                return ProbeResult(
                    status="ok",
                    latency_ms=latency_ms,
                    details={"host": self.host, "port": self.port},
                )
        except TimeoutError:
            return ProbeResult(
                status="unreachable",
                error=f"Connection to {self.host}:{self.port} timed out",
            )
        except ConnectionRefusedError:
            return ProbeResult(
                status="unreachable",
                error=f"Port {self.port} on {self.host} is closed",
            )
        except OSError as exc:
            return _err(str(exc))


# ---------------------------------------------------------------------------
# network tls-cert
# ---------------------------------------------------------------------------


@dataclass
class TlsCertConnector(ConnectorBase):
    """Verify a TLS certificate and report its expiry.

    Attributes:
        host: Hostname (also used for SNI).
        port: Port. Defaults to 443.
        warn_days: Days remaining before expiry to report ``"degraded"``.
        timeout_config: Timeout settings.
    """

    meta = ConnectorMeta(
        name="tls-cert",
        category=ConnectorCategory.NETWORK,
        description="Checks TLS certificate validity and expiry.",
        tags=(*_TAGS, "tls", "ssl", "security"),
    )

    host: str
    port: int = 443
    warn_days: int = 30
    timeout_config: TimeoutConfig = field(default_factory=TimeoutConfig)

    def probe(self) -> ProbeResult:
        import socket
        import ssl
        import time
        from datetime import UTC, datetime

        context = ssl.create_default_context()
        start = time.perf_counter()
        try:
            with socket.create_connection(
                (self.host, self.port),
                timeout=self.timeout_config.connect,
            ) as raw_sock, context.wrap_socket(raw_sock, server_hostname=self.host) as tls_sock:
                latency_ms = (time.perf_counter() - start) * 1000
                cert_raw = tls_sock.getpeercert()
                if not cert_raw:
                    return _err("No TLS peer certificate received")
                cert: dict[str, Any] = dict(cert_raw)

            not_after = str(cert.get("notAfter", ""))
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)
            days_left = (expiry - datetime.now(UTC)).days
            subject_pairs: list[tuple[str, str]] = [
                (str(attr[0]), str(attr[1]))
                for rdn in (cert.get("subject") or ())
                for attr in rdn
            ]
            subject = dict(subject_pairs)

            details: dict[str, Any] = {"expiry_days": days_left, "subject": subject}

            if days_left <= 0:
                return ProbeResult(
                    status="error",
                    latency_ms=latency_ms,
                    error="TLS certificate has expired",
                    details=details,
                )
            if days_left <= self.warn_days:
                return ProbeResult(
                    status="degraded",
                    latency_ms=latency_ms,
                    error=f"Certificate expires in {days_left} days",
                    details=details,
                )
            return ProbeResult(status="ok", latency_ms=latency_ms, details=details)

        except ssl.SSLCertVerificationError as exc:
            return _err(f"Certificate verification failed: {exc}")
        except TimeoutError:
            return ProbeResult(status="unreachable", error="TLS handshake timed out")
        except OSError as exc:
            return _err(str(exc))


# ---------------------------------------------------------------------------
# network route-table
# ---------------------------------------------------------------------------


@dataclass
class RouteTableConnector(ConnectorBase):
    """Read the local OS routing table.

    Wraps :func:`nadzoring.network_base.route_table.get_route_table`.
    """

    meta = ConnectorMeta(
        name="route-table",
        category=ConnectorCategory.NETWORK,
        description="Reads the OS routing table.",
        tags=(*_TAGS, "local", "routing"),
    )

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.route_table import get_route_table

        return _ok(get_route_table())


# ---------------------------------------------------------------------------
# network params
# ---------------------------------------------------------------------------


@dataclass
class NetworkParamsConnector(ConnectorBase):
    """Collect local network interface parameters.

    Wraps :func:`nadzoring.network_base.network_params.network_param` and
    :func:`nadzoring.network_base.ipv4_local_cli.get_local_ipv4`.
    """

    meta = ConnectorMeta(
        name="network-params",
        category=ConnectorCategory.NETWORK,
        description="Collects local network interface parameters.",
        tags=(*_TAGS, "local"),
    )

    def probe(self) -> ProbeResult:
        from nadzoring.network_base.ipv4_local_cli import get_local_ipv4
        from nadzoring.network_base.network_params import network_param

        params = network_param()
        if params is None:
            return _err("Network parameters are unavailable on this platform")
        out: dict[str, Any] = dict(params)
        out["local_ipv4"] = get_local_ipv4()
        return _ok(out)
