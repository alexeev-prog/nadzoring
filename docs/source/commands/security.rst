Security Commands
=================

The ``security`` group provides SSL/TLS certificate inspection, HTTP security
header auditing, email security record validation (SPF/DKIM/DMARC), subdomain
discovery, and continuous certificate monitoring.

.. code-block:: bash

   nadzoring security --help

----

.. _security-check-ssl:

security check-ssl
------------------

Inspect the SSL/TLS certificate of one or more domains.  Checks expiry date,
issuer, subject, Subject Alternative Names (SAN), public key strength, domain
match, and which TLS protocol versions the server accepts (TLSv1.0 through
TLSv1.3).

By default a compact summary table is displayed.  Use ``--full`` to include
the complete SAN list, protocol support details, chain length, and raw serial
number.

.. code-block:: text

   nadzoring security check-ssl [OPTIONS] DOMAIN [DOMAIN ...]

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``--days-before / -d``
     - ``7``
     - Days before expiry at which to flag the certificate as ``warning``
   * - ``--no-verify``
     - off
     - Disable certificate chain verification (useful for self-signed or
       internal CA certificates)
   * - ``--full``
     - off
     - Show all fields — SAN list, protocol support, chain length, serial
       number — instead of the compact summary
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds). Falls back to ``--timeout``.
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds). Falls back to ``--timeout``.

Status values
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Status
     - Meaning
   * - ``valid``
     - Certificate is valid and not near expiry
   * - ``warning``
     - Fewer than ``--days-before`` days remaining before expiry
   * - ``expired``
     - Certificate has already passed its expiry date
   * - ``error``
     - Could not connect to the host or parse the certificate

Examples
~~~~~~~~

.. code-block:: bash

   # Compact summary (default)
   nadzoring security check-ssl example.com

   # 30-day warning window, multiple domains
   nadzoring security check-ssl --days-before 30 google.com github.com cloudflare.com

   # Skip chain verification — useful for self-signed certs
   nadzoring security check-ssl --no-verify internal.corp.example.com

   # Full details: SAN, protocol support, chain, serial number
   nadzoring security check-ssl --full ya.ru

   # Custom timeout for slow servers
   nadzoring security check-ssl --connect-timeout 10 example.com

   # Save full JSON report
   nadzoring security check-ssl --full -o json --save ssl_report.json example.com github.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.security.check_website_ssl_cert import (
       check_ssl_certificate,
       check_ssl_expiry,
       check_ssl_expiry_with_fallback,
   )
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=10.0)

   # Verified check (full certificate chain validation)
   result = check_ssl_certificate("example.com", days_before=14, timeout_config=config)

   print(result["status"])           # 'valid' | 'warning' | 'expired' | 'error'
   print(result["remaining_days"])   # e.g. 142
   print(result["expiry_date"])      # '2025-10-15T12:00:00+00:00'
   print(result["verification"])     # 'verified' | 'unverified' | 'failed'

   # Subject and issuer
   print(result["subject"]["CN"])    # 'example.com'
   print(result["issuer"]["CN"])     # 'DigiCert TLS RSA SHA256 2020 CA1'
   print(result["issuer"]["O"])      # 'DigiCert Inc'

   # Subject Alternative Names
   for san in result.get("san", []):
       print(san)                    # 'DNS:example.com', 'DNS:www.example.com', ...

   # Domain match
   print(result["domain_match"])     # True
   print(result["matched_names"])    # ['DNS:example.com']

   # Public key
   key = result["public_key"]
   print(key["algorithm"])           # 'RSA' | 'EC' | 'Ed25519' | ...
   print(key.get("key_size"))        # 2048  (RSA / DSA only)
   print(key.get("curve"))           # 'secp256r1'  (EC only)
   print(key["strength"])            # 'weak' | 'good' | 'strong'

   # TLS protocol support (TLSv1.0 – TLSv1.3)
   protos = result["protocols"]
   print(protos["supported"])        # ['TLSv1.2', 'TLSv1.3']
   print(protos["has_outdated"])     # False — True if TLSv1.0 or TLSv1.1 supported

   # Certificate chain (only when verify=True)
   print(result.get("chain_length")) # 3
   print(result.get("chain_valid"))  # True

   # Expiry-only check (lighter)
   result = check_ssl_expiry("example.com")

   # Automatic fallback to unverified if chain check fails
   result = check_ssl_expiry_with_fallback("self-signed.badssl.com")
   print(result["verification"])     # 'unverified' when fallback was used

----

.. _security-check-headers:

security check-headers
----------------------

Analyse the HTTP security headers returned by one or more URLs.  Reports
which recommended headers are present or missing, identifies deprecated
headers (e.g. ``X-XSS-Protection``), lists information-leaking headers
(e.g. ``Server``, ``X-Powered-By``), and produces a 0–100 coverage score.

.. code-block:: text

   nadzoring security check-headers [OPTIONS] URL [URL ...]

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``--timeout``
     - ``10.0``
     - HTTP request timeout in seconds — sets both connect and read
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds). Falls back to ``--timeout``.
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds). Falls back to ``--timeout``.
   * - ``--no-verify``
     - off
     - Disable SSL certificate verification for the request

Checked security headers
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Header
     - Purpose
   * - ``Strict-Transport-Security``
     - Enforce HTTPS connections (HSTS)
   * - ``Content-Security-Policy``
     - Mitigate XSS and injection attacks
   * - ``X-Content-Type-Options``
     - Prevent MIME-type sniffing
   * - ``X-Frame-Options``
     - Prevent clickjacking
   * - ``X-XSS-Protection``
     - Legacy XSS filter (deprecated — flagged if present)
   * - ``Referrer-Policy``
     - Control referrer information leakage
   * - ``Permissions-Policy``
     - Restrict browser feature access
   * - ``Cross-Origin-Embedder-Policy``
     - Isolate cross-origin resources (COEP)
   * - ``Cross-Origin-Opener-Policy``
     - Isolate browsing context groups (COOP)
   * - ``Cross-Origin-Resource-Policy``
     - Control cross-origin resource sharing (CORP)
   * - ``Cache-Control``
     - Prevent caching of sensitive responses

Examples
~~~~~~~~

.. code-block:: bash

   # Single URL
   nadzoring security check-headers https://example.com

   # Batch audit — multiple services at once
   nadzoring security check-headers \
       https://api.example.com \
       https://admin.example.com \
       https://static.example.com

   # Internal endpoint — skip SSL verification
   nadzoring security check-headers --no-verify https://internal.corp.example.com

   # Slow server — increase timeout
   nadzoring security check-headers --connect-timeout 20 https://slow-api.example.com

   # Export JSON for CI / dashboard
   nadzoring security check-headers -o json --save headers_audit.json https://example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.security.http_headers import check_http_security_headers
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=5.0, read=15.0)
   result = check_http_security_headers(
       "https://example.com",
       timeout_config=config,
       verify_ssl=True,
   )

   print(result["url"])          # final URL after any redirects
   print(result["status_code"])  # HTTP status code (e.g. 200)
   print(result["score"])        # 0–100 coverage score

   # Headers that are correctly set
   for header, value in result["present"].items():
       print(f"  ✓ {header}: {value}")

   # Recommended headers that are absent
   for header in result["missing"]:
       print(f"  ✗ {header}")

   # Deprecated headers found in the response
   for header in result["deprecated"]:
       print(f"  ⚠ deprecated: {header}")

   # Headers that leak server or technology information
   for header, value in result["leaking"].items():
       print(f"  ⚠ leaking: {header} = {value}")

   if result["error"]:
       print("Request failed:", result["error"])

----

.. _security-check-email:

security check-email
--------------------

Validate the email security configuration of one or more domains.  Checks:

- **SPF** (Sender Policy Framework) — mechanism syntax, ``+all`` misuse,
  multiple SPF records, DNS lookup count.
- **DKIM** (DomainKeys Identified Mail) — probes 13 common selector names.
- **DMARC** (Domain-based Message Authentication, Reporting and Conformance)
  — parses ``p``, ``sp``, ``pct``, ``rua``, ``ruf`` tags and flags weak
  policies.

.. note::

   Requires one of the following to be available:

   - ``dnspython`` Python package (``pip install dnspython``) — preferred;
     handles multi-chunk TXT records reliably.
   - ``dig`` system utility.
   - ``nslookup`` system utility (fallback).

.. code-block:: text

   nadzoring security check-email [OPTIONS] DOMAIN [DOMAIN ...]

Examples
~~~~~~~~

.. code-block:: bash

   # Single domain
   nadzoring security check-email gmail.com

   # Multiple domains
   nadzoring security check-email google.com github.com cloudflare.com

   # All owned domains at once
   nadzoring security check-email corp.example.com mail.example.com newsletter.example.com

   # Full JSON report
   nadzoring security check-email -o json --save email_security.json example.com

   # Quiet mode — results only, no progress output
   nadzoring security check-email --quiet example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.security.email_security import check_email_security

   result = check_email_security("example.com")

   print(result["domain"])
   print(result["overall_score"])  # 0 = none found, 3 = SPF + DKIM + DMARC all present

   # SPF
   spf = result["spf"]
   print(spf["found"])             # True
   print(spf["record"])            # 'v=spf1 include:_spf.example.com ~all'
   print(spf["mechanisms"])        # ['include:_spf.example.com']
   print(spf["all_qualifier"])     # '~' (softfail — recommended minimum)
   for issue in spf["issues"]:
       print("  SPF issue:", issue)

   # DKIM
   dkim = result["dkim"]
   print(dkim["found"])
   print(dkim["selectors_checked"])  # list of 13 common selectors probed
   for selector, record in dkim["records"].items():
       print(f"  DKIM selector '{selector}': {record[:60]}...")
   for issue in dkim["issues"]:
       print("  DKIM issue:", issue)

   # DMARC
   dmarc = result["dmarc"]
   print(dmarc["found"])
   print(dmarc["record"])           # 'v=DMARC1; p=reject; rua=mailto:...'
   print(dmarc["policy"])           # 'none' | 'quarantine' | 'reject'
   print(dmarc["subdomain_policy"]) # value of sp= tag, or None
   print(dmarc["pct"])              # percentage the policy applies to
   print(dmarc["rua"])              # aggregate report destinations
   print(dmarc["ruf"])              # forensic report destinations
   for issue in dmarc["issues"]:
       print("  DMARC issue:", issue)

   # All issues aggregated across SPF + DKIM + DMARC
   for issue in result["all_issues"]:
       print("Issue:", issue)

Common issues reported
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Category
     - Issue
   * - SPF
     - No SPF record found
   * - SPF
     - Multiple SPF records (RFC violation)
   * - SPF
     - ``+all`` mechanism allows any sender (insecure)
   * - SPF
     - Missing ``all`` mechanism
   * - SPF
     - Exceeds 10 DNS lookup limit (RFC 7208)
   * - DKIM
     - No DKIM records found for any common selector
   * - DMARC
     - No DMARC record found
   * - DMARC
     - Policy ``p=none`` does not protect against spoofing
   * - DMARC
     - No aggregate report address (``rua=``) configured
   * - DMARC
     - Policy applies to less than 100 % of messages (``pct<100``)

----

.. _security-subdomains:

security subdomains
-------------------

Discover subdomains for a target domain using two complementary methods:

1. **Certificate Transparency logs** — queries the public `crt.sh
   <https://crt.sh>`_ API for all certificates ever issued for the domain.
2. **DNS brute-force** — resolves prefixes from a built-in wordlist of 80+
   common names (or a custom file) concurrently using a thread pool.

Each discovered subdomain is tagged with its discovery source.

.. code-block:: text

   nadzoring security subdomains [OPTIONS] DOMAIN

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``--wordlist``
     - built-in
     - Path to a custom wordlist file (one prefix per line).  Pass an
       empty string to skip brute-force entirely.
   * - ``--threads``
     - ``20``
     - Number of concurrent DNS resolution threads
   * - ``--timeout``
     - ``3.0``
     - Per-host DNS resolution timeout (seconds) — sets connect timeout
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds). Falls back to ``--timeout``.
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds). Falls back to ``--timeout``.
   * - ``--no-bruteforce``
     - off
     - Skip DNS brute-force; use CT logs only

Examples
~~~~~~~~

.. code-block:: bash

   # CT logs + built-in wordlist (default)
   nadzoring security subdomains example.com

   # CT logs only — faster, no DNS queries
   nadzoring security subdomains --no-bruteforce example.com

   # Custom wordlist, more threads, longer timeout
   nadzoring security subdomains \
       --wordlist /path/to/big-wordlist.txt \
       --threads 100 \
       --connect-timeout 5 \
       example.com

   # Save results as JSON
   nadzoring security subdomains -o json --save subdomains.json example.com

   # Quiet mode for scripting
   nadzoring security subdomains --quiet example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.security.subdomain_scan import scan_subdomains
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=8.0)

   # CT logs + built-in wordlist
   results = scan_subdomains("example.com", max_threads=20, timeout_config=config)

   for r in results:
       print(f"{r['subdomain']:40}  {r['ip']:16}  [{r['source']}]")
   # source: 'ct_log' | 'brute_force'

   # CT logs only
   results = scan_subdomains("example.com", wordlist_path="")

   # Custom wordlist
   results = scan_subdomains(
       "example.com",
       wordlist_path="/path/to/custom_wordlist.txt",
       max_threads=50,
       timeout_config=config,
   )

   # Filter by source
   ct_found    = [r for r in results if r["source"] == "ct_log"]
   brute_found = [r for r in results if r["source"] == "brute_force"]
   print(f"CT log: {len(ct_found)}  Brute-force: {len(brute_found)}")

Built-in wordlist categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The built-in wordlist of 80+ prefixes covers:

- Common web services: ``www``, ``mail``, ``ftp``, ``smtp``
- Admin panels: ``admin``, ``portal``, ``cpanel``, ``whm``, ``plesk``
- APIs and apps: ``api``, ``app``, ``dev``, ``staging``, ``test``, ``beta``
- Infrastructure: ``vpn``, ``proxy``, ``lb``, ``waf``, ``gateway``, ``ns1``, ``ns2``
- CDN and static assets: ``cdn``, ``static``, ``assets``, ``media``, ``images``
- DevOps tooling: ``git``, ``gitlab``, ``jenkins``, ``ci``, ``grafana``, ``kibana``
- Databases: ``db``, ``mysql``, ``postgres``, ``mongo``, ``redis``, ``elastic``

----

.. _security-watch-ssl:

security watch-ssl
------------------

Continuously monitor SSL/TLS certificates for one or more domains.  On each
check cycle the certificate is re-fetched and alerts are fired for:

- Near expiry (``status == warning``, fewer than ``--days-before`` days remain)
- Expired certificates (``status == expired``)
- Certificate changes (expiry date differs from the previous cycle)
- Check failures (connection error, parse error)

The command runs indefinitely until Ctrl-C, or for a fixed number of cycles
when ``--cycles`` is specified.

.. code-block:: text

   nadzoring security watch-ssl [OPTIONS] DOMAIN [DOMAIN ...]

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``--interval / -i``
     - ``3600``
     - Seconds between full check cycles
   * - ``--cycles / -c``
     - ``0``
     - Number of cycles to run (``0`` = run indefinitely)
   * - ``--days-before / -d``
     - ``7``
     - Days before expiry to trigger a warning alert
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds). Falls back to ``--timeout``.
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds). Falls back to ``--timeout``.

Alert events
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Trigger
     - Message example
   * - Check failure
     - ``Check failed: [Errno 111] Connection refused``
   * - Expired certificate
     - ``Certificate has EXPIRED``
   * - Near expiry
     - ``Certificate expires in 5 day(s)``
   * - Certificate changed
     - ``Certificate changed: expiry 2025-06-01 → 2025-12-01``

Examples
~~~~~~~~

.. code-block:: bash

   # Monitor one domain indefinitely (Ctrl-C to stop)
   nadzoring security watch-ssl example.com

   # Monitor multiple domains with a 14-day warning threshold
   nadzoring security watch-ssl --days-before 14 \
       example.com github.com cloudflare.com api.example.com

   # Check every 5 minutes for a critical service
   nadzoring security watch-ssl --interval 300 api.example.com

   # Run 10 cycles with a 60-second interval, save all results
   nadzoring security watch-ssl \
       --cycles 10 --interval 60 \
       -o json --save ssl_monitor_history.json \
       example.com

   # Custom timeout for slow servers
   nadzoring security watch-ssl --connect-timeout 10 --interval 300 api.example.com

   # Quiet mode — suppress progress, emit only alert lines
   nadzoring security watch-ssl --quiet --cycles 10 --interval 30 example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.security.ssl_monitor import SSLMonitor
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=10.0)

   monitor = SSLMonitor(
       domains=["example.com", "github.com", "cloudflare.com"],
       interval=3600,   # seconds between cycles
       days_before=14,  # alert when fewer than 14 days remain
       timeout_config=config,
   )

   # Custom alert handler — integrate with Slack, PagerDuty, email, etc.
   def on_alert(domain: str, message: str) -> None:
       print(f"ALERT  {domain}: {message}")

   monitor.set_alert_callback(on_alert)

   # Run a fixed number of cycles (blocking call)
   results = monitor.run_cycles(cycles=5)

   # Or run indefinitely until KeyboardInterrupt
   try:
       monitor.run()
   except KeyboardInterrupt:
       pass

   # Inspect the full check history
   for entry in monitor.history():
       print(
           entry["domain"],
           entry["status"],
           entry["remaining_days"],
           entry["checked_at"],
       )
