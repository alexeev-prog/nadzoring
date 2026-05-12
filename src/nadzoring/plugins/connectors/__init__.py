"""Built-in connector implementations.

Categories
----------
- :mod:`.web`      — HTTP/HTTPS endpoint connectors
- :mod:`.network`  — Network connectors (TCP, TLS, ping, scan, traceroute, …)
- :mod:`.dns`      — DNS connectors (resolve, reverse, health, benchmark, …)
- :mod:`.security` — Security connectors (SSL cert, HTTP headers, email, subdomains)
- :mod:`.arp`      — ARP connectors (cache, spoofing detection)
- :mod:`.cicd`     — CI/CD connectors (Docker, Kubernetes, GitHub Actions, GitLab CI, Jenkins)

Constructor note
------------------
Some connectors use ``dataclasses.field(..., kw_only=True)`` for booleans and
timeouts. Pass those arguments by keyword (including via
:class:`~nadzoring.plugins.registry.PluginRegistry.build`).
"""

from nadzoring.plugins.connectors.arp import ArpCacheConnector, ArpSpoofingConnector
from nadzoring.plugins.connectors.cicd import (
    DockerRegistryConnector,
    GithubActionsConnector,
    GitlabCIConnector,
    JenkinsConnector,
    KubernetesConnector,
)
from nadzoring.plugins.connectors.dns import (
    DnsBenchmarkConnector,
    DnsCompareConnector,
    DnsHealthConnector,
    DnsPoisoningConnector,
    DnsResolveConnector,
    DnsReverseConnector,
    DnsTraceConnector,
    DnsWhoisConnector,
)
from nadzoring.plugins.connectors.network import (
    ConnectionsConnector,
    GeolocationConnector,
    HttpPingConnector,
    NetworkParamsConnector,
    PingConnector,
    PortScanConnector,
    RouteTableConnector,
    TcpPortConnector,
    TlsCertConnector,
    TracerouteConnector,
    WhoisConnector,
)
from nadzoring.plugins.connectors.security import (
    EmailSecurityConnector,
    HttpHeadersConnector,
    SslCertConnector,
    SubdomainScanConnector,
)
from nadzoring.plugins.connectors.web import HttpEndpointConnector, WebhookConnector

__all__ = [
    "ArpCacheConnector",
    "ArpSpoofingConnector",
    "ConnectionsConnector",
    "DnsBenchmarkConnector",
    "DnsCompareConnector",
    "DnsHealthConnector",
    "DnsPoisoningConnector",
    "DnsResolveConnector",
    "DnsReverseConnector",
    "DnsTraceConnector",
    "DnsWhoisConnector",
    "DockerRegistryConnector",
    "EmailSecurityConnector",
    "GeolocationConnector",
    "GithubActionsConnector",
    "GitlabCIConnector",
    "HttpEndpointConnector",
    "HttpHeadersConnector",
    "HttpPingConnector",
    "JenkinsConnector",
    "KubernetesConnector",
    "NetworkParamsConnector",
    "PingConnector",
    "PortScanConnector",
    "RouteTableConnector",
    "SslCertConnector",
    "SubdomainScanConnector",
    "TcpPortConnector",
    "TlsCertConnector",
    "TracerouteConnector",
    "WebhookConnector",
    "WhoisConnector",
]
