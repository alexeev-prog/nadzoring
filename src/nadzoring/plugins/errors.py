"""Exceptions raised by the plugin registry and connector lifecycle."""

from nadzoring.utils.errors import NadzoringError


class PluginError(NadzoringError):
    """Base exception for plugin system failures."""


class ConnectorRegistrationError(PluginError):
    """Raised when a connector class cannot be registered.

    Common causes:
    - Missing or invalid :attr:`ConnectorBase.meta` attribute.
    - Duplicate connector name registration.
    """


class ConnectorNotFoundError(PluginError):
    """Raised when the registry has no connector with the requested name."""


class ConnectorProbeError(PluginError):
    """Raised when a connector's :meth:`probe` method raises unexpectedly.

    This wraps the original exception so callers can distinguish
    programming errors in a connector from expected probe failures
    (which are returned as error fields in :class:`ProbeResult`).
    """
