"""Base classes and metadata for the plugin connector system."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import StrEnum
from typing import ClassVar

from nadzoring.plugins.result import ProbeResult


class ConnectorCategory(StrEnum):
    """Top-level grouping for connector types.

    Attributes:
        WEB: HTTP/HTTPS endpoints, REST APIs, webhooks.
        NETWORK: Raw network targets — ICMP, TCP, TLS, DNS.
        CICD: CI/CD and deployment platforms — Docker, Kubernetes,
            GitHub Actions, GitLab CI, Jenkins.
    """

    WEB = "web"
    NETWORK = "network"
    CICD = "cicd"


@dataclass(frozen=True)
class ConnectorMeta:
    """Static metadata describing a connector.

    Attributes:
        name: Unique, machine-readable identifier (e.g. ``"http-endpoint"``).
        category: Which top-level group the connector belongs to.
        description: One-sentence human-readable summary.
        version: Semantic version of this connector implementation.
        tags: Optional free-form labels for filtering (e.g. ``["k8s", "tls"]``).
    """

    name: str
    category: ConnectorCategory
    description: str
    version: str = "1.0.0"
    tags: tuple[str, ...] = field(default_factory=tuple)


class ConnectorBase(abc.ABC):
    """Abstract base class for all Nadzoring connectors.

    Every connector must:

    1. Define a class-level :attr:`meta` attribute.
    2. Implement :meth:`probe` — the single entry point for connectivity checks.
    3. Never raise for expected failures; return an error via :class:`ProbeResult`.

    Network-bound connectors should accept ``timeout_config`` and forward it
    to every I/O call. Connectors that do not perform I/O may ignore it.

    Example subclass::

        class HttpEndpointConnector(ConnectorBase):
            meta = ConnectorMeta(
                name="http-endpoint",
                category=ConnectorCategory.WEB,
                description="Checks reachability of an HTTP/HTTPS URL.",
            )

            def __init__(
                self,
                target: str,
                *,
                timeout_config: TimeoutConfig | None = None,
            ) -> None:
                self.target = target
                self.timeout_config = timeout_config or TimeoutConfig()

            def probe(self) -> ProbeResult:
                ...
    """

    meta: ClassVar[ConnectorMeta]

    @abc.abstractmethod
    def probe(self) -> ProbeResult:
        """Run a single connectivity / health check against the target.

        Returns:
            A :class:`~nadzoring.plugins.result.ProbeResult` instance.
            On expected failures (timeout, auth error, unreachable host) the
            result must carry a non-``None`` ``error`` field rather than raising.
        """
