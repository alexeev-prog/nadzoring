===============
CLI Command Reference
===============

This page documents all CLI commands, their options, output formats, timeout configuration, and error handling patterns.

----

DNS Commands
------------

dns resolve
~~~~~~~~~~~

Resolve DNS records for one or more domains.

.. code-block:: bash

   nadzoring dns resolve [OPTIONS] DOMAINS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--type``
     - ``-t``
     - Record type: A, AAAA, CNAME, MX, NS, TXT, ALL
     - ``A``
   * - ``--nameserver``
     - ``-n``
     - Nameserver IP to use
     - System default
   * - ``--short``
     -
     - Compact output
     - ``False``
   * - ``--show-ttl``
     -
     - Show TTL value
     - ``False``
   * - ``--format-style``
     -
     - Output style: standard, bind, host, dig
     - ``standard``
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Examples:**

.. code-block:: bash

   # A record lookup
   nadzoring dns resolve google.com

   # Multiple record types
   nadzoring dns resolve -t MX -t TXT -t A example.com

   # All record types with a specific nameserver
   nadzoring dns resolve -t ALL -n 8.8.8.8 github.com

   # Show TTL values
   nadzoring dns resolve --show-ttl --type A cloudflare.com

   # Custom timeouts for slow networks
   nadzoring dns resolve --connect-timeout 10 --read-timeout 20 example.com

----

dns reverse
~~~~~~~~~~~

Perform reverse DNS lookups (PTR records) to find the hostname for an IP address.

.. code-block:: bash

   nadzoring dns reverse [OPTIONS] IP_ADDRESSES...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 70

   * - Option
     - Short
     - Description
   * - ``--nameserver``
     - ``-n``
     - Nameserver IP to use

**Examples:**

.. code-block:: bash

   # Single IP
   nadzoring dns reverse 8.8.8.8

   # Multiple IPs
   nadzoring dns reverse 1.1.1.1 8.8.8.8 9.9.9.9

   # Use a specific nameserver
   nadzoring dns reverse -n 208.67.222.222 8.8.4.4

   # Save as JSON
   nadzoring dns reverse -o json --save reverse_lookup.json 8.8.8.8 1.1.1.1

----

dns check
~~~~~~~~~

Perform a comprehensive DNS check including MX priority validation and SPF/DKIM analysis.

.. code-block:: bash

   nadzoring dns check [OPTIONS] DOMAINS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--nameserver``
     - ``-n``
     - Nameserver IP
     - System default
   * - ``--types``
     - ``-t``
     - Record types to check
     - ALL
   * - ``--validate-mx``
     -
     - Validate MX priority uniqueness
     - ``False``
   * - ``--validate-txt``
     -
     - Validate SPF and DKIM TXT records
     - ``False``
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Examples:**

.. code-block:: bash

   # Full DNS check
   nadzoring dns check example.com

   # Check MX and TXT only with validation
   nadzoring dns check -t MX -t TXT --validate-mx --validate-txt gmail.com

   # Multiple domains
   nadzoring dns check -n 9.9.9.9 google.com cloudflare.com

----

dns trace
~~~~~~~~~

Trace the complete DNS resolution delegation chain from root to authoritative nameserver.

.. code-block:: bash

   nadzoring dns trace [OPTIONS] DOMAIN

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--nameserver``
     - ``-n``
     - Starting nameserver
     - root ``198.41.0.4``
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Examples:**

.. code-block:: bash

   # Trace from root servers
   nadzoring dns trace example.com

   # Start trace from a specific nameserver
   nadzoring dns trace -n 8.8.8.8 google.com

   # Verbose with timing
   nadzoring dns trace -v github.com

----

dns compare
~~~~~~~~~~~

Compare DNS responses from multiple servers and detect discrepancies.

.. code-block:: bash

   nadzoring dns compare [OPTIONS] DOMAIN

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--servers``
     - ``-s``
     - DNS servers to compare
     - ``8.8.8.8``, ``1.1.1.1``, ``9.9.9.9``
   * - ``--type``
     - ``-t``
     - Record types to compare
     - ``A``

**Examples:**

.. code-block:: bash

   # Compare A records across default servers
   nadzoring dns compare example.com

   # Compare MX records with custom servers
   nadzoring dns compare -t MX -s 8.8.8.8 -s 208.67.222.222 -s 9.9.9.9 gmail.com

   # Multiple record types
   nadzoring dns compare -t A -t AAAA -t NS cloudflare.com

----

dns health
~~~~~~~~~~

Perform a scored DNS health check across all standard record types.

.. code-block:: bash

   nadzoring dns health [OPTIONS] DOMAIN

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--nameserver``
     - ``-n``
     - Nameserver IP
     - System default
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Health score:** **80–100** = Healthy · **50–79** = Degraded · **0–49** = Unhealthy

**Examples:**

.. code-block:: bash

   nadzoring dns health example.com
   nadzoring dns health -n 1.1.1.1 google.com
   nadzoring dns health -o json --save health.json example.com

----

dns benchmark
~~~~~~~~~~~~~

Benchmark DNS server response times across multiple servers.

.. code-block:: bash

   nadzoring dns benchmark [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--domain``
     - ``-d``
     - Domain to query
     - ``google.com``
   * - ``--servers``
     - ``-s``
     - Servers to benchmark
     - All public servers
   * - ``--type``
     - ``-t``
     - Record type
     - ``A``
   * - ``--queries``
     - ``-q``
     - Queries per server
     - ``10``
   * - ``--parallel/--sequential``
     -
     - Run concurrently or one by one
     - ``parallel``
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Examples:**

.. code-block:: bash

   nadzoring dns benchmark
   nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 9.9.9.9 --queries 20
   nadzoring dns benchmark -t MX -d gmail.com --sequential
   nadzoring dns benchmark -o json --save benchmark.json

----

dns poisoning
~~~~~~~~~~~~~

Detect DNS poisoning, censorship, or unusual CDN routing for a domain.

.. code-block:: bash

   nadzoring dns poisoning [OPTIONS] DOMAIN

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--control-server``
     - ``-c``
     - Trusted control resolver
     - ``8.8.8.8``
   * - ``--test-servers``
     - ``-t``
     - Servers to test against control
     - All public servers
   * - ``--type``
     - ``-T``
     - Record type
     - ``A``
   * - ``--additional-types``
     - ``-a``
     - Extra record types from control server
     - None
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Severity levels:** ``NONE`` → ``LOW`` → ``MEDIUM`` → ``HIGH`` → ``CRITICAL`` / ``SUSPICIOUS``

**Examples:**

.. code-block:: bash

   nadzoring dns poisoning example.com
   nadzoring dns poisoning -c 1.1.1.1 -a MX -a TXT google.com
   nadzoring dns poisoning -o html --save poisoning_report.html twitter.com

----

dns monitor
~~~~~~~~~~~

Continuously monitor DNS health and performance for a domain. Logs each cycle to a structured JSONL file and fires configurable alerts when response time or success rate thresholds are breached.

.. code-block:: bash

   nadzoring dns monitor [OPTIONS] DOMAIN

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--nameservers``
     - ``-n``
     - DNS server to monitor (repeatable)
     - ``8.8.8.8``, ``1.1.1.1``
   * - ``--interval``
     - ``-i``
     - Seconds between monitoring cycles
     - ``60``
   * - ``--type``
     - ``-t``
     - Record type: A, AAAA, MX, NS, TXT
     - ``A``
   * - ``--queries``
     - ``-q``
     - Queries per server per cycle
     - ``3``
   * - ``--max-rt``
     -
     - Alert threshold: max avg response time (ms)
     - ``500``
   * - ``--min-success``
     -
     - Alert threshold: minimum success rate (0–1)
     - ``0.95``
   * - ``--no-health``
     -
     - Skip DNS health check each cycle
     - ``False``
   * - ``--log-file``
     - ``-l``
     - JSONL file to append all cycle results to
     - None
   * - ``--cycles``
     - ``-c``
     - Stop after N cycles (0 = indefinite)
     - ``0``
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Examples:**

.. code-block:: bash

   # Monitor with default servers, save log
   nadzoring dns monitor example.com \
       --interval 60 \
       --log-file dns_monitor.jsonl

   # Strict thresholds — alert above 150 ms or below 99 % success
   nadzoring dns monitor example.com \
       -n 8.8.8.8 -n 1.1.1.1 -n 9.9.9.9 \
       --interval 30 \
       --max-rt 150 --min-success 0.99 \
       --log-file dns_monitor.jsonl

   # Run exactly 10 cycles and save a JSON report (great for CI)
   nadzoring dns monitor example.com --cycles 10 -o json --save report.json

   # Quiet mode for cron / systemd
   nadzoring dns monitor example.com \
       --quiet --log-file /var/log/nadzoring/dns_monitor.jsonl

----

dns monitor-report
~~~~~~~~~~~~~~~~~~

Analyse a JSONL log file produced by ``dns monitor``.

.. code-block:: bash

   nadzoring dns monitor-report [OPTIONS] LOG_FILE

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--server``
     - Filter statistics to a specific server IP

**Examples:**

.. code-block:: bash

   nadzoring dns monitor-report dns_monitor.jsonl
   nadzoring dns monitor-report dns_monitor.jsonl --server 8.8.8.8 -o json

----

Network Base Commands
---------------------

ping
~~~~

Check reachability using ICMP ping.

.. code-block:: bash

   nadzoring network-base ping ADDRESSES...

**Examples:**

.. code-block:: bash

   nadzoring network-base ping 8.8.8.8
   nadzoring network-base ping google.com cloudflare.com 1.1.1.1
   nadzoring network-base ping -o json github.com

----

http-ping
~~~~~~~~~

Measure HTTP/HTTPS response timing and inspect headers.

.. code-block:: bash

   nadzoring network-base http-ping [OPTIONS] URLS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 60 10

   * - Option
     - Description
     - Default
   * - ``--timeout``
     - Request timeout (seconds) — sets both connect and read
     - ``10.0``
   * - ``--connect-timeout``
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     - Read timeout (seconds)
     - ``10.0``
   * - ``--no-ssl-verify``
     - Disable SSL certificate check
     - ``False``
   * - ``--no-redirects``
     - Do not follow redirects
     - ``False``
   * - ``--show-headers``
     - Include response headers
     - ``False``

**Output includes:** DNS time, TTFB, total download time, status code, content size, redirects.

**Examples:**

.. code-block:: bash

   nadzoring network-base http-ping https://example.com
   nadzoring network-base http-ping --show-headers https://github.com https://google.com
   nadzoring network-base http-ping --timeout 5 --no-ssl-verify https://self-signed.badssl.com
   nadzoring network-base http-ping -o csv --save http_metrics.csv https://api.github.com

----

host-to-ip
~~~~~~~~~~

Resolve hostnames to IP addresses with IPv4/IPv6 availability checks.

.. code-block:: bash

   nadzoring network-base host-to-ip HOSTNAMES...

**Examples:**

.. code-block:: bash

   nadzoring network-base host-to-ip google.com github.com cloudflare.com
   nadzoring network-base host-to-ip -o csv --save resolutions.csv example.com

----

parse-url
~~~~~~~~~

Parse a URL into its components (scheme, hostname, port, path, query, fragment, etc.).

.. code-block:: bash

   nadzoring network-base parse-url URLS...

**Examples:**

.. code-block:: bash

   nadzoring network-base parse-url https://example.com/path?q=1#section
   nadzoring network-base parse-url "postgresql://user:pass@localhost:5432/db"

----

geolocation
~~~~~~~~~~~

Get geographic location for IP addresses.

.. code-block:: bash

   nadzoring network-base geolocation IPS...

**Output:** latitude, longitude, country, city.

**Examples:**

.. code-block:: bash

   nadzoring network-base geolocation 8.8.8.8 1.1.1.1
   nadzoring network-base geolocation --save locations.json 8.8.8.8

----

params
~~~~~~

Show local network interface configuration.

.. code-block:: bash

   nadzoring network-base params [OPTIONS]

**Output:** interface name, IPv4, IPv6, gateway IP, MAC address, public IP.

**Examples:**

.. code-block:: bash

   nadzoring network-base params
   nadzoring network-base params -o json --save net_params.json

----

port-scan
~~~~~~~~~

Scan for open TCP/UDP ports on one or more targets.

.. code-block:: bash

   nadzoring network-base port-scan [OPTIONS] TARGETS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 60 10

   * - Option
     - Description
     - Default
   * - ``--mode``
     - ``fast``, ``full``, or ``custom``
     - ``fast``
   * - ``--ports``
     - Port list or range, e.g. ``22,80,443`` or ``1-1024``
     - None
   * - ``--protocol``
     - ``tcp`` or ``udp``
     - ``tcp``
   * - ``--timeout``
     - Socket timeout (seconds) — sets connect timeout
     - ``2.0``
   * - ``--connect-timeout``
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     - Read timeout (seconds) for banner grabbing
     - ``10.0``
   * - ``--workers``
     - Concurrent workers
     - ``50``
   * - ``--no-banner``
     - Disable banner grabbing
     - ``False``
   * - ``--show-closed``
     - Show closed ports
     - ``False``

**Scan modes:** **fast** = common ports · **full** = all 1–65535 · **custom** = your list or range.

**Examples:**

.. code-block:: bash

   nadzoring network-base port-scan example.com
   nadzoring network-base port-scan --mode full 192.168.1.1
   nadzoring network-base port-scan --mode custom --ports 22,80,443,8080 example.com
   nadzoring network-base port-scan --protocol udp --mode fast example.com
   nadzoring network-base port-scan -o json --save scan.json example.com

----

detect-service
~~~~~~~~~~~~~~

Actively connect to ports and detect actual running services by banner analysis.

.. code-block:: bash

   nadzoring network-base detect-service [OPTIONS] TARGET PORTS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 60 10

   * - Option
     - Description
     - Default
   * - ``--timeout``
     - Connection timeout (seconds) — sets connect timeout
     - ``3.0``
   * - ``--connect-timeout``
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     - Read timeout (seconds) for banner
     - ``10.0``
   * - ``--no-probe``
     - Disable sending protocol-specific probes
     - ``False``

**Examples:**

.. code-block:: bash

   # Detect services on common ports
   nadzoring network-base detect-service example.com 80 443 22

   # Database ports with longer timeout
   nadzoring network-base detect-service --connect-timeout 5 192.168.1.100 3306 5432 6379

----

port-service
~~~~~~~~~~~~

Identify the service typically running on a port number.

.. code-block:: bash

   nadzoring network-base port-service PORTS...

**Examples:**

.. code-block:: bash

   nadzoring network-base port-service 80 443 22 53 3306
   nadzoring network-base port-service -o json 8080 5432 27017

----

whois
~~~~~

Look up WHOIS registration data for domains or IP addresses.

.. note::

   **Requires** the system ``whois`` utility:
   - Debian/Ubuntu: ``sudo apt install whois``
   - macOS: ``brew install whois``
   - RHEL/Fedora: ``sudo dnf install whois``

.. code-block:: bash

   nadzoring network-base whois [OPTIONS] TARGETS...

**Examples:**

.. code-block:: bash

   nadzoring network-base whois example.com
   nadzoring network-base whois google.com cloudflare.com 8.8.8.8
   nadzoring network-base whois -o json --save whois_data.json github.com

----

domain-info
~~~~~~~~~~~

Retrieve comprehensive information about a domain in a single call. Aggregates WHOIS registration data, DNS record lookups (A, AAAA, MX, NS, TXT), IP geolocation for the primary resolved address, and reverse DNS — all returned as a structured response.

.. code-block:: bash

   nadzoring network-base domain-info [OPTIONS] DOMAINS...

**Examples:**

.. code-block:: bash

   nadzoring network-base domain-info example.com
   nadzoring network-base domain-info google.com github.com cloudflare.com
   nadzoring network-base domain-info -o json --save domain_report.json example.com

----

connections
~~~~~~~~~~~

List active TCP/UDP network connections.

.. code-block:: bash

   nadzoring network-base connections [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--protocol``
     - ``-p``
     - Filter: ``tcp``, ``udp``, ``all``
     - ``all``
   * - ``--state``
     - ``-s``
     - State filter substring, e.g. ``LISTEN``
     - None
   * - ``--no-process``
     -
     - Skip PID/process info
     - ``False``

**Examples:**

.. code-block:: bash

   nadzoring network-base connections
   nadzoring network-base connections --protocol tcp --state LISTEN
   nadzoring network-base connections --protocol udp --no-process
   nadzoring network-base connections -o csv --save connections.csv

----

traceroute
~~~~~~~~~~

Trace the network path to a host.

.. code-block:: bash

   nadzoring network-base traceroute [OPTIONS] TARGETS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 60 10

   * - Option
     - Description
     - Default
   * - ``--max-hops``
     - Maximum hops
     - ``30``
   * - ``--timeout``
     - Per-hop timeout (seconds) — sets connect timeout
     - ``2.0``
   * - ``--connect-timeout``
     - Per-hop timeout (seconds)
     - ``5.0``
   * - ``--sudo``
     - Run with sudo (Linux)
     - ``False``

.. note::

   **Linux privilege note:** ``traceroute`` needs raw-socket access.
   Either use ``--sudo``, run as root, or: ``sudo setcap cap_net_raw+ep $(which traceroute)``
   Nadzoring automatically falls back to ``tracepath`` (no root required) if traceroute fails.

**Examples:**

.. code-block:: bash

   nadzoring network-base traceroute google.com
   nadzoring network-base traceroute --max-hops 20 github.com cloudflare.com
   nadzoring network-base traceroute --sudo example.com
   nadzoring network-base traceroute -o html --save trace.html 8.8.8.8

----

route
~~~~~

Display the system IP routing table.

.. code-block:: bash

   nadzoring network-base route [OPTIONS]

**Examples:**

.. code-block:: bash

   nadzoring network-base route
   nadzoring network-base route -o json
   nadzoring network-base route --save routing_table.json

----

Security Commands
-----------------

The ``security`` group provides SSL/TLS certificate inspection, HTTP security header auditing, email security record validation, subdomain discovery, and continuous certificate monitoring.

.. code-block:: bash

   nadzoring security --help

----

security check-ssl
~~~~~~~~~~~~~~~~~~

Inspect the SSL/TLS certificate for one or more domains. Checks expiry, issuer, subject, Subject Alternative Names, key strength, domain match, and which TLS protocol versions the server accepts (TLSv1.0 through TLSv1.3).

By default only a compact summary is shown. Use ``--full`` to see all fields including the complete SAN list, protocol details, chain length, and raw serial number.

.. code-block:: bash

   nadzoring security check-ssl [OPTIONS] DOMAINS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--days-before``
     - ``-d``
     - Days before expiry to flag as ``warning`` status
     - ``7``
   * - ``--no-verify``
     -
     - Disable certificate chain verification (falls back automatically)
     - ``False``
   * - ``--full``
     -
     - Show all certificate fields instead of compact summary
     - ``False``
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Status values:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Status
     - Meaning
   * - ``valid``
     - Certificate is valid and not near expiry
   * - ``warning``
     - Fewer than ``--days-before`` days remaining
   * - ``expired``
     - Certificate has already expired
   * - ``error``
     - Could not connect or parse the certificate

**Examples:**

.. code-block:: bash

   # Basic check — compact summary table
   nadzoring security check-ssl example.com

   # Check multiple domains with a 30-day warning window
   nadzoring security check-ssl --days-before 30 google.com github.com cloudflare.com

   # Check without verifying the certificate chain (useful for self-signed certs)
   nadzoring security check-ssl --no-verify internal.corp.example.com

   # Full details including SAN list, protocol support, chain info
   nadzoring security check-ssl --full ya.ru

   # Save results as JSON for further processing
   nadzoring security check-ssl -o json --save ssl_report.json example.com github.com

----

security check-headers
~~~~~~~~~~~~~~~~~~~~~~

Analyse the HTTP security headers returned by one or more URLs. Checks for the presence of eleven recommended headers, flags deprecated headers (e.g. ``X-XSS-Protection``), identifies information-leaking headers (e.g. ``Server``, ``X-Powered-By``), and produces a 0–100 coverage score.

.. code-block:: bash

   nadzoring security check-headers [OPTIONS] URLS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 60 10

   * - Option
     - Description
     - Default
   * - ``--timeout``
     - Request timeout in seconds — sets both connect and read
     - ``10.0``
   * - ``--connect-timeout``
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     - Read timeout (seconds)
     - ``10.0``
   * - ``--no-verify``
     - Disable SSL certificate verification
     - ``False``

**Checked security headers:**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Header
     - Purpose
   * - ``Strict-Transport-Security``
     - Enforce HTTPS (HSTS)
   * - ``Content-Security-Policy``
     - Mitigate XSS and injection attacks
   * - ``X-Content-Type-Options``
     - Prevent MIME-type sniffing
   * - ``X-Frame-Options``
     - Prevent clickjacking
   * - ``X-XSS-Protection``
     - Legacy XSS filter (deprecated)
   * - ``Referrer-Policy``
     - Control referrer information leakage
   * - ``Permissions-Policy``
     - Restrict browser feature access
   * - ``Cross-Origin-Embedder-Policy``
     - Isolate cross-origin resources
   * - ``Cross-Origin-Opener-Policy``
     - Isolate browsing context
   * - ``Cross-Origin-Resource-Policy``
     - Control cross-origin resource sharing
   * - ``Cache-Control``
     - Prevent caching of sensitive responses

**Examples:**

.. code-block:: bash

   # Check a single URL
   nadzoring security check-headers https://example.com

   # Check multiple URLs and save results
   nadzoring security check-headers https://google.com https://github.com https://cloudflare.com

   # Skip SSL verification for internal/self-signed endpoints
   nadzoring security check-headers --no-verify https://internal.corp.example.com

   # Export as JSON for CI integration or dashboards
   nadzoring security check-headers -o json --save headers_audit.json https://example.com

   # Adjust timeout for slow servers
   nadzoring security check-headers --connect-timeout 20 https://slow-api.example.com

----

security check-email
~~~~~~~~~~~~~~~~~~~~

Validate the email security configuration for one or more domains. Checks SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail) by probing common selectors, and DMARC (Domain-based Message Authentication, Reporting and Conformance). Returns structured findings including detected issues and an overall score.

.. note::

   **Requires:** ``dig`` or ``nslookup`` to be available on the system, or ``dnspython`` installed in the Python environment (``pip install dnspython``). ``dnspython`` is preferred as it handles multi-chunk TXT records reliably.

.. code-block:: bash

   nadzoring security check-email [OPTIONS] DOMAINS...

**Examples:**

.. code-block:: bash

   # Check a single domain
   nadzoring security check-email gmail.com

   # Check multiple domains at once
   nadzoring security check-email google.com github.com cloudflare.com

   # Export full JSON report
   nadzoring security check-email -o json --save email_security.json example.com

   # Quiet mode for scripting — results only, no progress bars
   nadzoring security check-email --quiet example.com

----

security subdomains
~~~~~~~~~~~~~~~~~~~

Discover subdomains for a target domain using two complementary methods: certificate transparency (CT) log queries via `crt.sh <https://crt.sh>`_ and concurrent DNS brute-force using a built-in wordlist of 80+ common prefixes (or a custom wordlist file). Each result is tagged with its discovery source.

.. code-block:: bash

   nadzoring security subdomains [OPTIONS] DOMAIN

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 60 10

   * - Option
     - Description
     - Default
   * - ``--wordlist``
     - Path to a custom wordlist file (one prefix per line)
     - Built-in 80+ prefix list
   * - ``--threads``
     - Number of concurrent DNS resolution threads
     - ``20``
   * - ``--timeout``
     - Per-host DNS resolution timeout in seconds
     - ``3.0``
   * - ``--connect-timeout``
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     - Read timeout (seconds)
     - ``10.0``
   * - ``--no-bruteforce``
     - Skip DNS brute-force entirely, use CT logs only
     - ``False``

**Examples:**

.. code-block:: bash

   # Discover subdomains using CT logs + built-in wordlist
   nadzoring security subdomains example.com

   # CT logs only — no brute-force DNS
   nadzoring security subdomains --no-bruteforce example.com

   # Use a custom wordlist file
   nadzoring security subdomains --wordlist /path/to/subdomains.txt example.com

   # Increase concurrency and timeout for faster / more thorough scanning
   nadzoring security subdomains --threads 50 --connect-timeout 5 example.com

   # Export results as JSON
   nadzoring security subdomains -o json --save subdomains.json example.com

   # Quiet mode for scripting
   nadzoring security subdomains --quiet example.com

----

security watch-ssl
~~~~~~~~~~~~~~~~~~

Continuously monitor SSL/TLS certificates for one or more domains. On each check cycle the certificate is re-fetched and alerts are fired for: near-expiry (``status == warning``), expired certificates, certificate changes (expiry date difference between consecutive checks), and check failures. Runs indefinitely until Ctrl-C or for a fixed number of cycles.

.. code-block:: bash

   nadzoring security watch-ssl [OPTIONS] DOMAINS...

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--interval``
     - ``-i``
     - Seconds between full check cycles
     - ``3600``
   * - ``--cycles``
     - ``-c``
     - Number of cycles to run (``0`` = run indefinitely)
     - ``0``
   * - ``--days-before``
     - ``-d``
     - Days before expiry to trigger a warning alert
     - ``7``
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Alert events fired:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

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

**Examples:**

.. code-block:: bash

   # Monitor ya.ru indefinitely, check every hour
   nadzoring security watch-ssl ya.ru

   # Monitor multiple domains with a 14-day warning threshold
   nadzoring security watch-ssl --days-before 14 example.com github.com cloudflare.com

   # Run exactly 5 check cycles with a 60-second interval (useful for CI/testing)
   nadzoring security watch-ssl --cycles 5 --interval 60 example.com

   # Frequent checks — every 5 minutes — for a critical service
   nadzoring security watch-ssl --interval 300 api.example.com

   # Save all check results as JSON after monitoring ends
   nadzoring security watch-ssl --cycles 3 -o json --save ssl_history.json example.com

   # Quiet mode — suppress progress output, emit only alert lines
   nadzoring security watch-ssl --quiet --cycles 10 --interval 30 example.com

----

ARP Commands
------------

arp cache
~~~~~~~~~

Show the current ARP cache table (IP-to-MAC mappings).

.. code-block:: bash

   nadzoring arp cache [OPTIONS]

**Examples:**

.. code-block:: bash

   nadzoring arp cache
   nadzoring arp cache -o csv --save arp_cache.csv
   nadzoring arp cache -o json

----

arp detect-spoofing
~~~~~~~~~~~~~~~~~~~

Statically detect ARP spoofing by analyzing the current ARP cache.

.. code-block:: bash

   nadzoring arp detect-spoofing [OPTIONS] [INTERFACES]...

**Detects:** duplicate MAC across IPs (``duplicate_mac``) and duplicate IP with multiple MACs (``duplicate_ip``).

**Examples:**

.. code-block:: bash

   nadzoring arp detect-spoofing
   nadzoring arp detect-spoofing eth0 wlan0
   nadzoring arp detect-spoofing -o json --save spoofing_alerts.json

----

arp monitor-spoofing
~~~~~~~~~~~~~~~~~~~~

Monitor live network traffic for ARP spoofing in real time (requires root/admin).

.. code-block:: bash

   nadzoring arp monitor-spoofing [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 20 10 60 10

   * - Option
     - Short
     - Description
     - Default
   * - ``--interface``
     - ``-i``
     - Interface to monitor
     - All
   * - ``--count``
     - ``-c``
     - Packets to capture
     - ``10``
   * - ``--timeout``
     - ``-t``
     - Capture timeout (seconds) — sets lifetime timeout
     - ``30``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds)
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds)
     - ``10.0``

**Examples:**

.. code-block:: bash

   nadzoring arp monitor-spoofing
   nadzoring arp monitor-spoofing --interface eth0 --count 200 --timeout 60
   nadzoring arp monitor-spoofing -o json --save arp_alerts.json

----

Output Formats
--------------

Use ``-o`` / ``--output`` to change the output format:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Format
     - Description
   * - ``table``
     - Rich terminal table (default)
   * - ``json``
     - JSON array, suitable for scripting
   * - ``csv``
     - Comma-separated values
   * - ``html``
     - Complete HTML page with CSS
   * - ``html_table``
     - HTML table fragment only
   * - ``yaml``
     - YAML format

**Examples:**

.. code-block:: bash

   nadzoring dns resolve -o json example.com
   nadzoring dns health -o html --save health.html example.com
   nadzoring network-base connections -o csv --save conns.csv
   nadzoring security check-ssl -o json example.com
   nadzoring security check-headers -o json --save headers.json https://example.com
   nadzoring security check-email -o json --save email_audit.json example.com
   nadzoring security subdomains -o json --save subdomains.json example.com

----

Saving Results
--------------

Use ``--save`` to write output to a file:

.. code-block:: bash

   nadzoring dns check -o html --save dns_report.html example.com
   nadzoring dns compare -o csv --save comparison.csv google.com
   nadzoring dns poisoning -o json --save poisoning.json example.com
   nadzoring network-base port-scan -o json --save scan.json example.com
   nadzoring network-base domain-info -o json --save domain_info.json example.com
   nadzoring security check-ssl -o json --save ssl_report.json example.com
   nadzoring security check-headers -o json --save headers_report.json https://example.com
   nadzoring security check-email -o json --save email_security.json example.com
   nadzoring security subdomains -o json --save subdomains.json example.com
   nadzoring arp cache -o csv --save arp.csv

----

Logging Levels
--------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Mode
     - Flag
     - Behaviour
   * - Normal
     - (none)
     - Warnings + progress bars
   * - Verbose
     - ``--verbose``
     - Debug logs + execution timing
   * - Quiet
     - ``--quiet``
     - Results only — ideal for scripting

----

Timeout Configuration
---------------------

Nadzoring provides three timeout options that work together:

.. list-table::
   :header-rows: 1
   :widths: 30 60 10 10

   * - Option
     - Description
     - Default
     - Fallback
   * - ``--timeout``
     - Lifetime timeout for the entire operation
     - ``30.0``
     - —
   * - ``--connect-timeout``
     - Timeout for establishing connections
     - ``5.0``
     - Falls back to ``--timeout``
   * - ``--read-timeout``
     - Timeout for read operations after connection
     - ``10.0``
     - Falls back to ``--timeout``

**Resolution order per phase:**
1. Phase-specific option (``--connect-timeout`` / ``--read-timeout``)
2. Generic ``--timeout``
3. Module default (shown above)

**Example:**

.. code-block:: bash

   # All three phases have explicit timeouts
   nadzoring dns resolve --timeout 60 --connect-timeout 5 --read-timeout 30 example.com

   # Connect timeout inherits from generic timeout (30s), read uses default (10s)
   nadzoring dns resolve --timeout 30 example.com

   # Connect timeout = 3s, read timeout = 3s (both inherit from --timeout)
   nadzoring dns resolve --timeout 3 example.com

----

Error Handling
--------------

Every public Python API function follows a consistent error contract — functions never raise on expected DNS or network failures. All errors are returned as structured data so that scripts can handle them uniformly.

**DNS result-dict pattern** — check ``result["error"]`` before using ``result["records"]``:

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer

   result = resolve_with_timer("example.com", "A")
   if result["error"]:
       # "Domain does not exist"  — NXDOMAIN
       # "No A records"           — record type not present
       # "Query timeout"          — nameserver did not respond
       print("DNS error:", result["error"])
   else:
       print(result["records"])
       print(f"RTT: {result['response_time']} ms")

**Return-None / empty-dict pattern** — used where a result cannot be partially valid:

.. code-block:: python

   from nadzoring.network_base.geolocation_ip import geo_ip

   result = geo_ip("8.8.8.8")
   if not result:
       print("Geolocation unavailable")
   else:
       print(f"{result['city']}, {result['country']}")

**Timeout exceptions** — raised only when lifetime timeout is exceeded:

.. code-block:: python

   from nadzoring.utils.timeout import OperationTimeoutError, timeout_context, TimeoutConfig

   config = TimeoutConfig(lifetime=5.0)
   try:
       with timeout_context(config):
           result = resolve_with_timer("example.com", "A")
   except OperationTimeoutError:
       print("Operation exceeded 5 second lifetime limit")

**Exception pattern** — used only for system-level failures (missing commands, unsupported OS):

.. code-block:: python

   from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError

   try:
       cache = ARPCache()
       entries = cache.get_cache()
   except ARPCacheRetrievalError as exc:
       print("Cannot read ARP cache:", exc)

All library exceptions inherit from ``nadzoring.utils.errors.NadzoringError`` and can be caught at any granularity:

.. code-block:: python

   from nadzoring.utils.errors import NadzoringError, DNSError, NetworkError, ARPError
