"""Tests for plugin registry, metadata, and :class:`~nadzoring.plugins.result.ProbeResult`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pytest

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.connectors.security import SslCertConnector
from nadzoring.plugins.connectors.web import HttpEndpointConnector
from nadzoring.plugins.errors import (
    ConnectorNotFoundError,
    ConnectorRegistrationError,
)
from nadzoring.plugins.registry import PluginRegistry
from nadzoring.plugins.result import ProbeResult


def test_probe_result_ok_property() -> None:
    """``ProbeResult.ok`` is true only when status is ok and error is absent."""
    assert ProbeResult(status="ok", error=None).ok is True
    assert ProbeResult(status="ok", error="x").ok is False
    assert ProbeResult(status="degraded", error=None).ok is False


def test_registry_build_ssl_cert_keyword_only_fields() -> None:
    """``PluginRegistry.build`` forwards keyword-only flags to the connector."""
    registry = PluginRegistry()
    registry.register(SslCertConnector)
    conn = registry.build(
        "ssl-cert",
        domains=["example.test"],
        days_before=1,
        verify=False,
        full=True,
    )
    assert isinstance(conn, SslCertConnector)
    assert conn.verify is False
    assert conn.full is True


def test_registry_register_build_list() -> None:
    """Register, build, and list connectors."""
    registry = PluginRegistry()
    registry.register(HttpEndpointConnector)
    assert "http-endpoint" in registry
    assert len(registry) == 1

    conn = registry.build("http-endpoint", target="https://example.com")
    assert isinstance(conn, HttpEndpointConnector)

    meta_list = registry.list_all()
    assert len(meta_list) == 1
    assert meta_list[0].name == "http-endpoint"
    assert meta_list[0].category is ConnectorCategory.WEB


def test_registry_duplicate_name_raises() -> None:
    """Duplicate ``meta.name`` registration raises."""
    registry = PluginRegistry()
    registry.register(HttpEndpointConnector)

    @dataclass
    class DuplicateHttp(ConnectorBase):
        meta: ClassVar[ConnectorMeta] = ConnectorMeta(
            name="http-endpoint",
            category=ConnectorCategory.WEB,
            description="duplicate",
        )
        target: str = "https://x"

        def probe(self) -> ProbeResult:
            return ProbeResult(status="ok")

    with pytest.raises(ConnectorRegistrationError, match="already registered"):
        registry.register(DuplicateHttp)


def test_registry_missing_meta_raises() -> None:
    """Classes without ``ConnectorMeta`` cannot be registered."""

    class BadConnector(ConnectorBase):
        def probe(self) -> ProbeResult:
            return ProbeResult(status="ok")

    registry = PluginRegistry()
    with pytest.raises(ConnectorRegistrationError, match="meta"):
        registry.register(BadConnector)  # type: ignore[arg-type]


def test_registry_build_unknown_raises() -> None:
    """``build`` raises when the name is unknown."""
    registry = PluginRegistry()
    with pytest.raises(ConnectorNotFoundError, match="http-endpoint"):
        registry.build("http-endpoint", target="https://x")


def test_registry_unregister() -> None:
    """Unregister removes a connector by name."""
    registry = PluginRegistry()
    registry.register(HttpEndpointConnector)
    registry.unregister("http-endpoint")
    assert len(registry) == 0
    with pytest.raises(ConnectorNotFoundError):
        registry.unregister("http-endpoint")


def test_registry_list_by_category_and_tag() -> None:
    """``list_by_category`` and ``list_by_tag`` filter metadata."""
    registry = PluginRegistry()
    registry.register(HttpEndpointConnector)
    web = registry.list_by_category(ConnectorCategory.WEB)
    assert len(web) == 1
    assert registry.list_by_category(ConnectorCategory.CICD) == []

    tagged = registry.list_by_tag("https")
    assert len(tagged) == 1
    assert registry.list_by_tag("nonexistent-tag") == []
