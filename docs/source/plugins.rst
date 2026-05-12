Plugins
=======

The :mod:`nadzoring.plugins` package provides a small **connector** framework for
probing hosts, services, and CI/CD systems from Python. It is separate from the
Click CLI: connectors call the same domain functions the CLI uses and return a
uniform :class:`~nadzoring.plugins.result.ProbeResult`.

This is intended for integrators who want to embed Nadzoring checks in
monitoring pipelines, test harnesses, or orchestration without shelling out to
``nadzoring`` commands.

----

Concepts
--------

**Connector** — A class inheriting :class:`~nadzoring.plugins.base.ConnectorBase`
with a class-level :attr:`~nadzoring.plugins.base.ConnectorBase.meta` and an
implemented :meth:`~nadzoring.plugins.base.ConnectorBase.probe` method that returns
:class:`~nadzoring.plugins.result.ProbeResult`.

**Registry** — :class:`~nadzoring.plugins.registry.PluginRegistry` maps
``ConnectorMeta.name`` strings to connector classes, builds instances, and lists
connectors by category or tag.

**Categories** — :class:`~nadzoring.plugins.base.ConnectorCategory` groups
connectors as ``web``, ``network``, or ``cicd``.

Built-in implementations live under :mod:`nadzoring.plugins.connectors` (DNS,
network, security, ARP, HTTP, CI/CD). Optional Flask/Django/FastAPI examples live
in :mod:`nadzoring.plugins.examples`.

----

Minimal example
---------------

.. code-block:: python

   from nadzoring.plugins import PluginRegistry
   from nadzoring.plugins.connectors import DnsResolveConnector, PingConnector

   registry = PluginRegistry()
   registry.register(DnsResolveConnector)
   registry.register(PingConnector)

   dns_result = registry.build(
       "dns-resolve",
       domains=["example.com"],
       record_types=["A"],
   ).probe()

   ping_result = registry.build("ping", addresses=["127.0.0.1"]).probe()

   print(dns_result.status, dns_result.details)
   print(ping_result.status, ping_result.error)

Several network and security connectors mark **boolean and timeout fields as
keyword-only** in their dataclass constructors. This avoids passing a bare
``True``/``False`` positionally where it could be mistaken for a numeric
parameter. Always pass those arguments by name (and the same applies to
``PluginRegistry.build``, which forwards keyword arguments to the connector).

.. code-block:: python

   from nadzoring.plugins import PluginRegistry
   from nadzoring.plugins.connectors import (
       ConnectionsConnector,
       HttpPingConnector,
       SslCertConnector,
       TracerouteConnector,
   )

   registry = PluginRegistry()
   for cls in (
       HttpPingConnector,
       SslCertConnector,
       ConnectionsConnector,
       TracerouteConnector,
   ):
       registry.register(cls)

   http = registry.build(
       "http-ping",
       urls=["https://example.com"],
       verify_ssl=True,
       follow_redirects=True,
       include_headers=False,
   ).probe()

   tls = registry.build(
       "ssl-cert",
       domains=["example.com"],
       days_before=14,
       verify=True,
       full=False,
   ).probe()

   connections = registry.build(
       "connections",
       protocol="tcp",
       state_filter="LISTEN",
       include_process=False,
   ).probe()

   trace = registry.build(
       "traceroute",
       targets=["198.51.100.1"],
       max_hops=30,
       use_sudo=False,
   ).probe()

----

Result contract
---------------

:class:`~nadzoring.plugins.result.ProbeResult` fields:

* ``status`` — ``"ok"``, ``"degraded"``, ``"unreachable"``, or ``"error"``.
* ``error`` — Human-readable message when the probe did not fully succeed.
* ``latency_ms`` — Optional round-trip timing where applicable.
* ``details`` — Structured payload (often includes a ``"data"`` key with raw
  domain-layer results).

Connectors should follow the same rule as domain code: **do not raise for
expected failures** (timeouts, HTTP 4xx/5xx, DNS errors). Surface them via
``status`` and ``error``.

----

Timeouts
--------

Network-oriented connectors accept :class:`~nadzoring.utils.timeout.TimeoutConfig`
(see :doc:`error_handling` and domain documentation). Pass ``None`` only where the
connector constructs defaults internally.

----

Linting note for contributors
-------------------------------

``ruff`` applies a few **per-file ignores** under ``src/nadzoring/plugins/`` for
lazy imports inside ``probe()`` and connector ``meta`` layout. See ``ruff.toml``
``[lint.per-file-ignores]`` for the exact codes.
