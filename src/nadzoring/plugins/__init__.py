"""Plugin system for Nadzoring connectors.

Connectors are grouped into categories:

- ``web``      — HTTP/HTTPS endpoints, webhooks
- ``network``  — TCP/TLS ports, ping, traceroute, port-scan, whois, geo, …
- ``cicd``     — Docker, Kubernetes, GitHub Actions, GitLab CI, Jenkins

All built-in connectors live in :mod:`nadzoring.plugins.connectors`.
Framework-specific examples (Flask, Django, FastAPI) live in
:mod:`nadzoring.plugins.examples`.

Quick start::

    from nadzoring.plugins import PluginRegistry
    from nadzoring.plugins.connectors import (
        DnsResolveConnector,
        SslCertConnector,
        FlaskConnector,       # from examples
    )

    registry = PluginRegistry()
    registry.register(DnsResolveConnector)
    registry.register(SslCertConnector)

    result = registry.build(
        "ssl-cert",
        domains=["example.com"],
        days_before=14,
        verify=True,
        full=False,
    ).probe()

    print(result.status, result.details)
"""

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.errors import (
    ConnectorNotFoundError,
    ConnectorProbeError,
    ConnectorRegistrationError,
)
from nadzoring.plugins.registry import PluginRegistry
from nadzoring.plugins.result import ProbeResult

__all__ = [
    "ConnectorBase",
    "ConnectorCategory",
    "ConnectorMeta",
    "ConnectorNotFoundError",
    "ConnectorProbeError",
    "ConnectorRegistrationError",
    "PluginRegistry",
    "ProbeResult",
]
