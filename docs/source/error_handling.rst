Error Handling
==============

Nadzoring follows a consistent error-handling pattern across all Python APIs:
functions **never raise exceptions for expected failures** (DNS errors,
network timeouts, missing PTR records, SSL connection errors). All such
failures are returned as structured data, making the library safe to use in
automation scripts without wrapping every call in try/except.

Only truly unexpected errors (programming mistakes, missing system commands,
unsupported operating systems) are allowed to propagate as exceptions.

----

DNS Result Pattern
------------------

Functions that perform DNS lookups (``resolve_with_timer``, ``reverse_dns``)
return a dictionary with an ``"error"`` key. Always check it before using
other fields:

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer

   result = resolve_with_timer("example.com", "A")

   if result["error"]:
       # Handle the error
       print("DNS error:", result["error"])
   else:
       # Safe to use records and response_time
       print(result["records"])
       print(f"RTT: {result['response_time']} ms")

Possible error values for ``resolve_with_timer``:

- ``"Domain does not exist"`` — NXDOMAIN response
- ``"No A records"`` (or any record type) — domain exists but has no records of the requested type
- ``"Query timeout"`` — nameserver did not respond within the timeout
- Any other string — unexpected resolver error (e.g. malformed response)

**Reverse DNS:**

.. code-block:: python

   from nadzoring.dns_lookup.reverse import reverse_dns

   result = reverse_dns("8.8.8.8")

   if result["error"]:
       print("Reverse lookup failed:", result["error"])
       # "No PTR record", "No reverse DNS", "Query timeout",
       # "Invalid IP address: …"
   else:
       print(result["hostname"])

----

Timeout Errors
--------------

The `OperationTimeoutError` exception is raised when a lifetime timeout is
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
socket timeouts and do not raise `OperationTimeoutError`.

**Platform differences:** On Unix systems, `timeout_context` uses SIGALRM
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

   result = whois_lookup("example.com")
   if result.get("error"):
       print("WHOIS lookup failed:", result["error"])
       # "WHOIS lookup failed. Ensure 'whois' is installed."

----

Exception Pattern
------------------

Exceptions are reserved for system-level failures that the caller cannot
reasonably handle inline. All custom exceptions inherit from
``nadzoring.utils.errors.NadzoringError``.

.. code-block:: python

   from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError
   from nadzoring.utils.errors import ARPError, DNSError, NetworkError

   try:
       cache = ARPCache()
       entries = cache.get_cache()
   except ARPCacheRetrievalError as exc:
       # System command missing, permission denied, etc.
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
3. **Catch specific exceptions** only for system-level failures.
4. **Use timeout contexts** for operations that may hang.
5. **Use the structured error values** for logging and alerting.

Example robust monitoring script with timeout support:

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer
   from nadzoring.dns_lookup.health import health_check_dns
   from nadzoring.utils.errors import NadzoringError
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
       if a_result["error"]:
           result["error"] = f"A record failed: {a_result['error']}"
           return result
       result["a_record"] = a_result["records"][0]

       # Health check
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
