"""Central registry for discovering and instantiating connectors."""

from __future__ import annotations

from typing import Any

from nadzoring.plugins.base import ConnectorBase, ConnectorCategory, ConnectorMeta
from nadzoring.plugins.errors import (
    ConnectorNotFoundError,
    ConnectorRegistrationError,
)


class PluginRegistry:
    """Central store for connector classes.

    Connectors are registered by their :attr:`ConnectorMeta.name`.  The
    registry is intentionally *not* a singleton — callers that need a shared
    instance must manage it themselves.

    Example::

        registry = PluginRegistry()
        registry.register(HttpEndpointConnector)
        registry.register(KubernetesConnector)

        connector = registry.build("http-endpoint", target="https://example.com")
        result = connector.probe()
    """

    def __init__(self) -> None:
        """Create an empty registry."""
        self._connectors: dict[str, type[ConnectorBase]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, connector_cls: type[ConnectorBase]) -> None:
        """Register a connector class.

        Args:
            connector_cls: A concrete subclass of :class:`ConnectorBase`
                with a valid :attr:`~ConnectorBase.meta` attribute.

        Raises:
            ConnectorRegistrationError: If ``meta`` is missing, malformed,
                or if a connector with the same name is already registered.
        """
        if not hasattr(connector_cls, "meta") or not isinstance(
            connector_cls.meta, ConnectorMeta
        ):
            raise ConnectorRegistrationError(
                f"{connector_cls.__name__} must define a class-level "
                "'meta: ConnectorMeta' attribute."
            )

        name = connector_cls.meta.name
        if name in self._connectors:
            raise ConnectorRegistrationError(
                f"A connector named '{name}' is already registered "
                f"({self._connectors[name].__name__}). "
                "Use a unique name or unregister the existing one first."
            )

        self._connectors[name] = connector_cls

    def unregister(self, name: str) -> None:
        """Remove a connector from the registry.

        Args:
            name: The :attr:`ConnectorMeta.name` to remove.

        Raises:
            ConnectorNotFoundError: If no connector with that name exists.
        """
        if name not in self._connectors:
            raise ConnectorNotFoundError(f"No connector named '{name}' is registered.")
        del self._connectors[name]

    # ------------------------------------------------------------------
    # Instantiation
    # ------------------------------------------------------------------

    def build(self, name: str, **kwargs: Any) -> ConnectorBase:
        """Instantiate a registered connector by name.

        All extra keyword arguments are forwarded to the connector's
        ``__init__``.

        Args:
            name: The :attr:`ConnectorMeta.name` of the desired connector.
            **kwargs: Constructor arguments for the connector.

        Returns:
            A ready-to-use :class:`ConnectorBase` instance.

        Raises:
            ConnectorNotFoundError: If the name is not registered.
        """
        connector_cls = self._get(name)
        return connector_cls(**kwargs)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_all(self) -> list[ConnectorMeta]:
        """Return metadata for every registered connector, sorted by name."""
        return sorted(
            (cls.meta for cls in self._connectors.values()),
            key=lambda m: m.name,
        )

    def list_by_category(self, category: ConnectorCategory) -> list[ConnectorMeta]:
        """Return metadata for connectors in the given category.

        Args:
            category: The :class:`ConnectorCategory` to filter by.

        Returns:
            Alphabetically sorted list of matching :class:`ConnectorMeta`.
        """
        return sorted(
            (
                cls.meta
                for cls in self._connectors.values()
                if cls.meta.category == category
            ),
            key=lambda m: m.name,
        )

    def list_by_tag(self, tag: str) -> list[ConnectorMeta]:
        """Return metadata for connectors that carry the given tag.

        Args:
            tag: Tag string to match (case-sensitive).

        Returns:
            Alphabetically sorted list of matching :class:`ConnectorMeta`.
        """
        return sorted(
            (
                cls.meta
                for cls in self._connectors.values()
                if tag in cls.meta.tags
            ),
            key=lambda m: m.name,
        )

    def __contains__(self, name: str) -> bool:
        """Return ``True`` if *name* is a registered connector id."""
        return name in self._connectors

    def __len__(self) -> int:
        """Return the number of registered connector classes."""
        return len(self._connectors)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(self, name: str) -> type[ConnectorBase]:
        try:
            return self._connectors[name]
        except KeyError:
            raise ConnectorNotFoundError(
                f"No connector named '{name}' is registered. "
                f"Available: {sorted(self._connectors)}"
            ) from None
