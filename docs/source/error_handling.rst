Error Handling
==============

Nadzoring follows a consistent error-handling pattern across all Python APIs:
functions **never raise exceptions for expected failures** (DNS errors,
network timeouts, missing PTR records, SSL connection errors). All such
failures are returned as structured data with type-safe error fields,
making the library safe to use in automation scripts without wrapping every
call in try/except.

Only truly unexpected errors (programming mistakes, missing system commands,
unsupported operating systems) are allowed to propagate as exceptions.

----

Type-Safe Error Fields
----------------------

All result dictionaries use ``Literal`` types for their ``"error"`` field,
defined in module-specific ``errors.py`` files. This enables:

- **IDE autocompletion** for error strings
- **Static type checking** (mypy catches typos)
- **Single source of truth** for documentation

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer
   from nadzoring.dns_lookup.errors import DNSResolveError

   result = resolve_with_timer("example.com", "A")

   # Type-safe error checking
   if result["error"] == "Domain does not exist":
       handle_nxdomain()
   elif result["error"] == "Query timeout":
       retry_with_longer_timeout()

Error literal modules:

- ``nadzoring.dns_lookup.errors`` — DNS resolution, reverse DNS, trace
- ``nadzoring.security.errors`` — SSL certificates, HTTP headers, email security
- ``nadzoring.network_base.errors`` — ping, traceroute, WHOIS, port scanning
- ``nadzoring.arp.errors`` — ARP cache retrieval, spoofing detection

----

DNS Result Pattern
------------------

Functions that perform DNS lookups (``resolve_with_timer``, ``reverse_dns``)
return a dictionary with an ``"error"`` field typed as ``DNSResolveError | None``
or ``DNSReverseError | None``. Always check it before using other fields:

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer
   from nadzoring.dns_lookup.errors import DNSResolveError

   result = resolve_with_timer("example.com", "A")

   if result["error"]:
       # Handle the error — result["error"] is type DNSResolveError
       print("DNS error:", result["error"])
   else:
       # Safe to use records and response_time
       print(result["records"])
       print(f"RTT: {result['response_time']} ms")

Possible error values for ``resolve_with_timer`` (see ``DNSResolveError``):

- ``"Domain does not exist"`` — NXDOMAIN response
- ``"No records of requested type"`` — domain exists but has no records of the requested type
- ``"Query timeout"`` — nameserver did not respond within the timeout
- ``"Operation exceeded lifetime timeout"`` — overall timeout exceeded
- ``"Resolver error"`` — unexpected resolver error

**Reverse DNS:**

.. code-block:: python

   from nadzoring.dns_lookup.reverse import reverse_dns
   from nadzoring.dns_lookup.errors import DNSReverseError

   result = reverse_dns("8.8.8.8")

   if result["error"]:
       # result["error"] is type DNSReverseError | None
       print("Reverse lookup failed:", result["error"])
       # Possible values: "No PTR record", "No reverse DNS",
       # "Query timeout", "Invalid IP address", "Resolver error"
   else:
       print(result["hostname"])

----

Result Handling Utilities
-------------------------

The ``nadzoring.utils.result`` module provides helper functions for working
with error-bearing result dictionaries:

.. code-block:: python

   from nadzoring.utils.result import is_success, unwrap, unwrap_or
   from nadzoring.utils.errors import NadzoringError

   result = resolve_with_timer("example.com", "A")

   # Check success without accessing error field
   if is_success(result):
       print(result["records"])

   # Raise on error
   try:
       safe_result = unwrap(result)
       print(safe_result["records"])
   except NadzoringError as e:
       print(f"Operation failed: {e}")

   # Provide fallback on error
   records = unwrap_or(result, [])
   # records is either the original result dict or empty list

----

Timeout Errors
--------------

The ``OperationTimeoutError`` exception is raised when a lifetime timeout is
exceeded. This is an **expected failure** — it should be caught and handled
by converting to an error field in the result dict, not allowed to propagate
to the user.

.. code-block:: python

   from nadzoring.utils.timeout import TimeoutConfig, timeout_context, OperationTimeoutError

   config = TimeoutConfig(lifetime=5.0)

   try:
       with timeout_context(config):
           result = long_running_operation()
   except OperationTimeoutError:
       result = {"error": "Operation exceeded lifetime timeout"}

**When to use:** Lifetime timeouts are useful for operations that may hang
indefinitely (e.g., DNS queries to unresponsive servers, socket connections
to firewalled hosts). Phase-specific timeouts (connect/read) are handled by
socket timeouts and do not raise ``OperationTimeoutError``.

**Platform differences:** On Unix systems, ``timeout_context`` uses SIGALRM
which can interrupt blocking system calls. On Windows, the timeout is checked
only after the operation completes (best-effort).

----

Empty-Result Pattern
--------------------

Some functions return an empty dict (or empty list) when the result cannot be
partially valid. This is common for geolocation, WHOIS, or system information
commands.

.. code-block:: python

   from nadzoring.network_base.geolocation_ip import geo_ip

   result = geo_ip("8.8.8.8")
   if not result:
       print("Geolocation unavailable (private IP, rate-limit, or network error)")
   else:
       print(result["city"], result["country"])

   from nadzoring.network_base.whois_lookup import whois_lookup
   from nadzoring.network_base.errors import WHOISError

   result = whois_lookup("example.com")
   if result.get("error"):
       # result["error"] is type WHOISError | None
       print("WHOIS lookup failed:", result["error"])
       # Possible values: "Command not found", "Query timeout",
       # "No information found", "Invalid target"

----

Security Module Error Types
---------------------------

**SSL/TLS Certificate Checks** (``nadzoring.security.errors.SSLCertError``):

.. code-block:: python

   from nadzoring.security.check_website_ssl_cert import check_ssl_certificate
   from nadzoring.security.errors import SSLCertError

   result = check_ssl_certificate("example.com")
   if result.get("error"):
       # Possible values: "Certificate expired", "Certificate not yet valid",
       # "Hostname mismatch", "Self-signed certificate", "Connection timeout",
       # "SSL handshake failed", "Certificate verification failed",
       # "No certificate returned"
       print("SSL error:", result["error"])

**HTTP Security Headers** (``nadzoring.security.errors.HTTPHeaderError``):

.. code-block:: python

   from nadzoring.security.http_headers import check_http_security_headers
   from nadzoring.security.errors import HTTPHeaderError

   result = check_http_security_headers("https://example.com")
   if result.get("error"):
       # Possible values: "Request timeout", "Connection refused",
       # "SSL verification failed", "Too many redirects", "Invalid URL"
       print("HTTP check failed:", result["error"])

**Email Security** (``nadzoring.security.errors.EmailSecurityError``):

.. code-block:: python

   from nadzoring.security.email_security import check_email_security
   from nadzoring.security.errors import EmailSecurityError

   result = check_email_security("example.com")
   # Errors are collected in result["all_issues"] list
   # Each issue is one of: "No SPF record", "No DKIM record",
   # "No DMARC record", "SPF lookup timeout", etc.

----

Network Base Module Error Types
-------------------------------

**WHOIS Lookups** (``nadzoring.network_base.errors.WHOISError``):

.. code-block:: python

   from nadzoring.network_base.whois_lookup import whois_lookup
   from nadzoring.network_base.errors import WHOISError

   result = whois_lookup("example.com")
   if result.get("error"):
       # Possible values: "Command not found", "Query timeout",
       # "No information found", "Invalid target"
       print("WHOIS error:", result["error"])

**Traceroute** (``nadzoring.network_base.errors.TracerouteError``):

.. code-block:: python

   from nadzoring.network_base.traceroute import traceroute
   from nadzoring.network_base.errors import TracerouteError

   # traceroute returns list of TraceHop objects, errors are logged
   # but the function may raise on system-level failures with messages:
   # "Permission denied (needs root)", "Command not found",
   # "Network unreachable", "DNS resolution failed", "Timeout"

**Port Scanning** (``nadzoring.network_base.errors.PortScanError``):

.. code-block:: python

   from nadzoring.network_base.port_scanner import scan_ports, ScanConfig
   from nadzoring.network_base.errors import PortScanError

   # scan_ports returns list of ScanResult, errors are logged internally
   # Resolution failures return None for target_ip and are skipped

**Geolocation** (``nadzoring.network_base.errors.GeolocationError``):

.. code-block:: python

   from nadzoring.network_base.geolocation_ip import geo_ip

   result = geo_ip("8.8.8.8")
   if not result:
       # Empty dict indicates: "API request failed", "Rate limit exceeded",
       # "Invalid IP address", or "Private IP address"
       print("Geolocation unavailable")

----

ARP Module Error Types
----------------------

**ARP Cache Retrieval** (``nadzoring.arp.errors.ARPCacheError``):

.. code-block:: python

   from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError
   from nadzoring.arp.errors import ARPCacheError

   try:
       cache = ARPCache()
       entries = cache.get_cache()
   except ARPCacheRetrievalError as e:
       # Exception message is one of: "Command not found",
       # "Permission denied (needs root)", "Unsupported platform",
       # "Failed to parse ARP cache output"
       print("ARP cache error:", e)

**ARP Spoofing Detection** (``nadzoring.arp.errors.ARPSpoofingError``):

.. code-block:: python

   from nadzoring.arp.realtime import ARPRealtimeDetector
   from nadzoring.arp.errors import ARPSpoofingError

   detector = ARPRealtimeDetector()
   try:
       alerts = detector.monitor(interface="eth0", count=100)
   except RuntimeError as e:
       # RuntimeError wraps ARPSpoofingError messages:
       # "No network interface specified", "Packet capture failed",
       # "No ARP packets captured"
       print("Monitoring failed:", e)

----

Exception Pattern
-----------------

Exceptions are reserved for system-level failures that the caller cannot
reasonably handle inline. All custom exceptions inherit from
``nadzoring.utils.errors.NadzoringError``.

.. code-block:: python

   from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError
   from nadzoring.utils.errors import ARPError, DNSError, NetworkError, NadzoringError

   try:
       cache = ARPCache()
       entries = cache.get_cache()
   except ARPCacheRetrievalError as exc:
       # System command missing, permission denied, etc.
       # Exception message matches ARPCacheError literal
       print("Cannot read ARP cache:", exc)

   # Catch any Nadzoring error at any granularity
   try:
       # some operation
       pass
   except NadzoringError as exc:
       print("A Nadzoring operation failed:", exc)
   except DNSError as exc:
       # Handle only DNS-related errors
       print("DNS operation failed:", exc)

Common exception types:

- ``DNSError`` — base for all DNS errors
  - ``DNSResolutionError`` — resolution failed
  - ``DNSTimeoutError`` — query timed out
  - ``DNSDomainNotFoundError`` — NXDOMAIN
  - ``DNSNoRecordsError`` — record type not present
- ``NetworkError`` — base for network errors
  - ``HostResolutionError`` — hostname resolution failed
  - ``ConnectionTimeoutError`` — connection timed out
  - ``UnsupportedPlatformError`` — OS not supported
- ``ARPError`` — base for ARP errors
  - ``ARPCacheRetrievalError`` — failed to read ARP cache
- ``ValidationError`` — input validation failed
  - ``InvalidIPAddressError`` — not a valid IP
  - ``InvalidDomainError`` — not a valid domain name
  - ``InvalidPortError`` — port out of range

----

Command-Line Error Handling
---------------------------

When using the CLI, errors are displayed in red and the command exits with a
non-zero status code. Use ``--quiet`` to suppress all output except the error
message.

.. code-block:: bash

   $ nadzoring dns resolve non-existent-domain.example
   DNS error: Domain does not exist
   $ echo $?
   1

   $ nadzoring dns resolve -o json non-existent-domain.example
   {"error": "Domain does not exist", ...}
   $ echo $?
   1

Timeout errors in CLI:

   When a lifetime timeout is exceeded, the command exits with an error
   message and a non-zero status code. Phase-specific timeouts (connect/read)
   are handled within the operation and returned as error fields where
   applicable.

.. code-block:: bash

   $ nadzoring dns resolve --timeout 1 slow-domain.example
   DNS error: Operation exceeded lifetime timeout
   $ echo $?
   1

----

Best Practices for Scripts
--------------------------

1. **Always check the error field** for DNS/network operations.
2. **Use truthiness checks** for functions that return empty dicts/lists.
3. **Use ``is_success()`` helper** for cleaner error checking.
4. **Use ``unwrap_or()``** for graceful degradation with defaults.
5. **Catch specific exceptions** only for system-level failures.
6. **Use timeout contexts** for operations that may hang.
7. **Use the Literal error types** for type-safe pattern matching.

Example robust monitoring script with timeout support:

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer
   from nadzoring.dns_lookup.health import health_check_dns
   from nadzoring.dns_lookup.errors import DNSResolveError
   from nadzoring.utils.errors import NadzoringError
   from nadzoring.utils.result import is_success, unwrap_or
   from nadzoring.utils.timeout import TimeoutConfig

   def check_domain(domain: str, timeout_sec: float = 30.0) -> dict:
       """Safe domain checker — never raises."""
       timeout_config = TimeoutConfig(lifetime=timeout_sec)

       result = {
           "domain": domain,
           "a_record": None,
           "health_score": None,
           "error": None,
       }

       # DNS resolution with timeout
       a_result = resolve_with_timer(
           domain, "A",
           timeout_config=timeout_config,
       )

       if not is_success(a_result):
           # Type-safe error handling
           error: DNSResolveError | None = a_result.get("error")
           result["error"] = f"A record failed: {error}"
           return result

       result["a_record"] = a_result["records"][0]

       # Health check with fallback
       try:
           health = health_check_dns(domain, timeout_config=timeout_config)
           result["health_score"] = health["score"]
       except NadzoringError as exc:
           # System-level failure (unlikely, but possible)
           result["error"] = f"Health check system error: {exc}"

       return result

   # Use it
   data = check_domain("example.com", timeout_sec=10.0)
   if data["error"]:
       print(f"Check failed: {data['error']}")
   else:
       print(f"OK: {data['a_record']}  score={data['health_score']}")

   # Using unwrap_or for graceful degradation
   from nadzoring.utils.result import unwrap_or

   result = resolve_with_timer("example.com", "A")
   records = unwrap_or(result, ["0.0.0.0"])  # Fallback on error
   print(f"Resolved to: {records[0]}")

----

Error Literal Reference
-----------------------

**DNS Module** (``nadzoring.dns_lookup.errors``):

- ``DNSResolveError``: ``"Domain does not exist"``, ``"No records of requested type"``,
  ``"Query timeout"``, ``"Operation exceeded lifetime timeout"``, ``"Resolver error"``
- ``DNSReverseError``: ``"No PTR record"``, ``"No reverse DNS"``, ``"Query timeout"``,
  ``"Invalid IP address"``, ``"Resolver error"``
- ``DNSTraceError``: ``"Loop detected"``, ``"Delegation error"``, ``"No further delegation"``,
  ``"Timeout"``, ``"Domain does not exist"``, ``"No answer"``

**Security Module** (``nadzoring.security.errors``):

- ``SSLCertError``: ``"Certificate expired"``, ``"Certificate not yet valid"``,
  ``"Hostname mismatch"``, ``"Self-signed certificate"``, ``"Connection timeout"``,
  ``"SSL handshake failed"``, ``"Certificate verification failed"``, ``"No certificate returned"``
- ``HTTPHeaderError``: ``"Request timeout"``, ``"Connection refused"``,
  ``"SSL verification failed"``, ``"Too many redirects"``, ``"Invalid URL"``
- ``EmailSecurityError``: ``"No SPF record"``, ``"No DKIM record"``, ``"No DMARC record"``,
  ``"SPF lookup timeout"``, ``"DKIM lookup timeout"``, ``"DMARC lookup timeout"``

**Network Base Module** (``nadzoring.network_base.errors``):

- ``PingError``: ``"Host unreachable"``, ``"Timeout"``, ``"Permission denied (needs root)"``,
  ``"Invalid address"``
- ``TracerouteError``: ``"Permission denied (needs root)"``, ``"Command not found"``,
  ``"Network unreachable"``, ``"DNS resolution failed"``, ``"Timeout"``
- ``WHOISError``: ``"Command not found"``, ``"Query timeout"``, ``"No information found"``,
  ``"Invalid target"``
- ``PortScanError``: ``"Connection refused"``, ``"Timeout"``, ``"Host unreachable"``,
  ``"Invalid port range"``, ``"Resolution failed"``
- ``GeolocationError``: ``"API request failed"``, ``"Rate limit exceeded"``,
  ``"Invalid IP address"``, ``"Private IP address"``

**ARP Module** (``nadzoring.arp.errors``):

- ``ARPCacheError``: ``"Command not found"``, ``"Permission denied (needs root)"``,
  ``"Unsupported platform"``, ``"Failed to parse ARP cache output"``
- ``ARPSpoofingError``: ``"No network interface specified"``, ``"Packet capture failed"``,
  ``"No ARP packets captured"``
