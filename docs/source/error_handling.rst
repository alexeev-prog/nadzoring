Error Handling
==============

Every public Python API in Nadzoring follows one of two contracts:

1. **Result-dict pattern** — functions return a typed dict that always
   contains an ``"error"`` field.  The function never raises on DNS or
   network failures; exceptions are caught internally and surfaced as
   human-readable strings.
2. **Return-None pattern** — functions return ``None`` (or an empty
   container) when an operation cannot be completed.

This page documents both patterns, their error values, and recommended
handling idioms.

----

DNS Result-Dict Pattern
-----------------------

All functions in :mod:`nadzoring.dns_lookup` that query nameservers return
a :class:`~nadzoring.dns_lookup.types.DNSResult` dict.  The contract is:

- ``result["error"] is None`` → success; ``result["records"]`` is populated
- ``result["error"] is not None`` → failure; ``result["records"]`` is ``[]``

Possible error strings:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Error value
     - Meaning
   * - ``"Domain does not exist"``
     - NXDOMAIN — the domain is not registered
   * - ``"No <TYPE> records"``
     - The domain exists but has no records of the queried type
   * - ``"Query timeout"``
     - The nameserver did not respond within the timeout
   * - arbitrary string
     - Unexpected ``dnspython`` or socket error

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer

   result = resolve_with_timer("example.com", "A")

   if result["error"]:
       print("DNS error:", result["error"])
       # "Domain does not exist"  — check spelling
       # "No A records"           — try a different record type
       # "Query timeout"          — try a different nameserver
   else:
       for record in result["records"]:
           print(record)
       print(f"RTT: {result['response_time']} ms")

----

Reverse DNS
-----------

:func:`~nadzoring.dns_lookup.reverse.reverse_dns` uses the same pattern:

.. code-block:: python

   from nadzoring.dns_lookup.reverse import reverse_dns

   result = reverse_dns("8.8.8.8")

   if result["error"]:
       # "No PTR record"          — IP has no reverse entry
       # "No reverse DNS"         — NXDOMAIN on reverse zone
       # "Query timeout"
       # "Invalid IP address: …"  — malformed input
       hostname = f"[{result['error']}]"
   else:
       hostname = result["hostname"]

   print(f"8.8.8.8 → {hostname}")

----

Health Check
------------

:func:`~nadzoring.dns_lookup.health.health_check_dns` always returns a
complete dict — it never fails outright.  Check ``"status"`` and
iterate ``"issues"`` / ``"warnings"``:

.. code-block:: python

   from nadzoring.dns_lookup.health import health_check_dns

   health = health_check_dns("example.com")

   print(f"Score: {health['score']}/100  Status: {health['status']}")
   # status: "healthy" (>=80) | "degraded" (50-79) | "unhealthy" (<50)

   for issue in health["issues"]:
       print("  CRITICAL:", issue)

   for warning in health["warnings"]:
       print("  WARN:", warning)

   for rtype, score in health["record_scores"].items():
       print(f"  {rtype}: {score}/100")

----

DNS Comparison
--------------

:func:`~nadzoring.dns_lookup.compare.compare_dns_servers` returns a
:class:`~nadzoring.dns_lookup.compare.ServerComparisonResult`.
Iterate ``"differences"`` to find discrepancies:

.. code-block:: python

   from nadzoring.dns_lookup.compare import compare_dns_servers

   result = compare_dns_servers(
       "example.com",
       servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
       record_types=["A", "MX"],
   )

   if not result["differences"]:
       print("All servers agree")
   else:
       for diff in result["differences"]:
           print(
               f"Server {diff['server']} returned different"
               f" {diff['type']} records:"
           )
           print(f"  Expected (baseline): {diff['expected']}")
           print(f"  Got:                 {diff['got']}")
           if diff["ttl_difference"] is not None:
               print(f"  TTL delta: {diff['ttl_difference']}s")

----

DNS Poisoning
-------------

:func:`~nadzoring.dns_lookup.poisoning.check_dns_poisoning` returns a
:class:`~nadzoring.dns_lookup.types.PoisoningCheckResult`.

Severity levels in ascending order: ``NONE`` → ``LOW`` → ``MEDIUM`` →
``HIGH`` → ``CRITICAL`` / ``SUSPICIOUS``.

.. code-block:: python

   from nadzoring.dns_lookup.poisoning import check_dns_poisoning

   result = check_dns_poisoning("example.com")

   level = result.get("poisoning_level", "NONE")
   confidence = result.get("confidence", 0.0)

   print(f"Level: {level}  Confidence: {confidence:.0f}%")

   if result.get("poisoned"):
       for inc in result.get("inconsistencies", []):
           print("Inconsistency:", inc)

   if result.get("cdn_detected"):
       print(f"CDN detected: {result['cdn_owner']}")

----

Geolocation
-----------

:func:`~nadzoring.network_base.geolocation_ip.geo_ip` returns an empty
dict ``{}`` on failure:

.. code-block:: python

   from nadzoring.network_base.geolocation_ip import geo_ip

   result = geo_ip("8.8.8.8")

   if not result:
       print("Geolocation unavailable (private IP, rate-limit, or error)")
   else:
       print(f"{result['city']}, {result['country']}")
       print(f"Coordinates: {result['lat']}, {result['lon']}")

----

Ping
----

:func:`~nadzoring.network_base.ping_address.ping_addr` returns a plain
``bool``.  Note that ICMP may be blocked by firewalls even for reachable
hosts:

.. code-block:: python

   from nadzoring.network_base.ping_address import ping_addr

   if ping_addr("8.8.8.8"):
       print("Host is reachable")
   else:
       print("No ICMP reply (host may still be up)")

----

ARP Cache
---------

:class:`~nadzoring.arp.cache.ARPCache` raises
:exc:`~nadzoring.arp.cache.ARPCacheRetrievalError` when the underlying
system command fails:

.. code-block:: python

   from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError

   try:
       cache = ARPCache()
       entries = cache.get_cache()
   except ARPCacheRetrievalError as exc:
       print("Cannot read ARP cache:", exc)
   else:
       for entry in entries:
           print(f"{entry.ip_address}  {entry.mac_address}  {entry.interface}")

----

HTTP Ping
---------

:func:`~nadzoring.network_base.http_ping.http_ping` never raises;
check the ``error`` attribute:

.. code-block:: python

   from nadzoring.network_base.http_ping import http_ping

   result = http_ping("https://example.com")

   if result.error:
       print("HTTP probe failed:", result.error)
   else:
       print(f"Status: {result.status_code}")
       print(f"DNS: {result.dns_ms} ms")
       print(f"TTFB: {result.ttfb_ms} ms")
       print(f"Total: {result.total_ms} ms")

----

Batch Processing
----------------

When processing many hosts, collect errors instead of stopping:

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer

   domains = ["example.com", "nonexistent.invalid", "google.com"]
   errors: list[dict] = []
   results: list[dict] = []

   for domain in domains:
       result = resolve_with_timer(domain, "A")
       if result["error"]:
           errors.append({"domain": domain, "error": result["error"]})
       else:
           results.append(result)

   print(f"Resolved: {len(results)}/{len(domains)}")
   for err in errors:
       print(f"  FAILED: {err['domain']} — {err['error']}")
