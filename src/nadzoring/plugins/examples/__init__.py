"""Example connectors for popular Python web frameworks.

These connectors demonstrate how to extend :class:`~nadzoring.plugins.base.ConnectorBase`
for framework-specific health checks.  They are intentionally minimal — copy and
adapt them for your own application.

Available examples
------------------
- :class:`~nadzoring.plugins.examples.frameworks.FlaskConnector`
- :class:`~nadzoring.plugins.examples.frameworks.DjangoConnector`
- :class:`~nadzoring.plugins.examples.frameworks.FastAPIConnector`
"""

from nadzoring.plugins.examples.frameworks import (
    DjangoConnector,
    FastAPIConnector,
    FlaskConnector,
)

__all__ = [
    "DjangoConnector",
    "FastAPIConnector",
    "FlaskConnector",
]
