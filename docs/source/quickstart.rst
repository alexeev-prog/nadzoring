Quick Start
===========

After installing Nadzoring (see :doc:`installation`), you can start using it immediately.
This page covers the most common workflows with practical examples.

----

Basic Structure
---------------

Nadzoring uses a three-level command hierarchy:

.. code-block:: text

   nadzoring <group> <command> [OPTIONS] [ARGUMENTS]

The four command groups are ``dns``, ``network-base``, ``security``, and ``arp``.

----

Global Options
--------------

Every command supports these flags:

.. list-table::
   :header-rows: 1
   :widths: 20 10 55 15

   * - Option
     - Short
     - Description
     - Default
   * - ``--verbose``
     -
     - Show debug logs and execution timing
     - ``False``
   * - ``--quiet``
     -
     - Suppress all output except results
     - ``False``
   * - ``--no-color``
     -
     - Disable colored output
     - ``False``
   * - ``--output``
     - ``-o``
     - Output format: ``table``, ``json``, ``csv``, ``html``, ``html_table``, ``yaml``
     - ``table``
   * - ``--save``
     -
     - Save results to a file
     - None
   * - ``--timeout``
     -
     - Lifetime timeout for the entire operation (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds). Falls back to ``--timeout``.
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds). Falls back to ``--timeout``.
     - ``10.0``

**Timeout resolution order:**
1. Explicit phase-specific flag (``--connect-timeout`` / ``--read-timeout``)
2. Generic ``--timeout`` flag
3. Module default shown above

----

1. Check Your Network Configuration
--------------------------------------

Get a full summary of your local network interface:

.. code-block:: bash

   nadzoring network-base params

Output includes interface name, IPv4/IPv6 addresses, gateway IP, MAC address,
and public IP address.

To export as JSON for scripting:

.. code-block:: bash

   nadzoring network-base params -o json --save net_params.json

**Python API:**

.. code-block:: python

   from nadzoring.network_base.network_params import network_param

   info = network_param()
   print(info["IPv4 address"])        # '192.168.1.42'
   print(info["Router ip-address"])   # '192.168.1.1'
   print(info["Public IP address"])   # your external IP

----

2. Resolve a Hostname to IP
-----------------------------

Translate a hostname to its IPv4 address:

.. code-block:: bash

   nadzoring network-base host-to-ip example.com

Look up specific DNS record types:

.. code-block:: bash

   # A record (IPv4)
   nadzoring dns resolve example.com

   # All record types at once
   nadzoring dns resolve -t ALL example.com

   # MX and TXT records
   nadzoring dns resolve -t MX -t TXT gmail.com

   # Show TTL values
   nadzoring dns resolve --show-ttl -t A github.com

   # Use a specific nameserver
   nadzoring dns resolve -n 8.8.8.8 example.com

   # Custom timeout for slow networks
   nadzoring dns resolve --connect-timeout 10 --read-timeout 20 example.com

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer
   from nadzoring.utils.timeout import TimeoutConfig

   # Default timeouts
   result = resolve_with_timer("example.com", "A")
   if not result["error"]:
       print(result["records"])       # ['93.184.216.34']
       print(result["response_time"]) # e.g. 42.5 ms

   # Custom timeouts
   config = TimeoutConfig(connect=3.0, read=8.0, lifetime=20.0)
   result = resolve_with_timer("example.com", "A", timeout_config=config)

----

3. Parse a URL
---------------

Break a URL into its components (scheme, hostname, port, path, query, fragment):

.. code-block:: bash

   nadzoring network-base parse-url https://example.com/path?q=1#section

**Python API:**

.. code-block:: python

   from nadzoring.network_base.parse_url import parse_url

   result = parse_url("https://user:pass@example.com:8080/path?key=value#frag")
   print(result["protocol"])   # 'https'
   print(result["hostname"])   # 'example.com'
   print(result["port"])       # 8080
   print(result["username"])   # 'user'
   print(result["query_params"])  # [('key', 'value')]

----

4. Comprehensive Domain Information
-------------------------------------

Retrieve WHOIS registration data, DNS records, IP geolocation, and reverse DNS
for a domain in a single command:

.. code-block:: bash

   nadzoring network-base domain-info example.com

   # Multiple domains, save as JSON
   nadzoring network-base domain-info -o json --save domain_info.json \
       google.com github.com cloudflare.com

**Python API:**

.. code-block:: python

   from nadzoring.network_base.domain_info import get_domain_info

   info = get_domain_info("example.com")

   print(info["whois"]["registrar"])
   print(info["dns"]["ipv4"])          # '93.184.216.34'
   print(info["dns"]["records"]["MX"]) # list of MX records
   print(info["geolocation"]["country"])
   print(info["reverse_dns"])          # hostname or None

----

5. Reverse DNS Lookup
-----------------------

Find the hostname associated with an IP address (PTR record):

.. code-block:: bash

   # Single IP
   nadzoring dns reverse 8.8.8.8

   # Multiple IPs at once
   nadzoring dns reverse 1.1.1.1 8.8.8.8 9.9.9.9

   # Use a custom nameserver
   nadzoring dns reverse -n 208.67.222.222 8.8.4.4

   # Save results as JSON
   nadzoring dns reverse -o json --save reverse.json 8.8.8.8

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.reverse import reverse_dns

   result = reverse_dns("8.8.8.8")
   if result["error"]:
       print(result["error"])  # 'No PTR record'
   else:
       print(result["hostname"])       # 'dns.google'
       print(result["response_time"])  # e.g. 18.34 ms

----

6. Ping a Host
---------------

Check basic network reachability:

.. code-block:: bash

   # Single host
   nadzoring network-base ping google.com

   # Multiple hosts at once
   nadzoring network-base ping 8.8.8.8 1.1.1.1 cloudflare.com

**Python API:**

.. code-block:: python

   from nadzoring.network_base.ping_address import ping_addr

   # Works with IPs, hostnames, and full URLs
   reachable = ping_addr("8.8.8.8")
   reachable = ping_addr("https://google.com")

----

7. HTTP Probe a URL
---------------------

Measure DNS resolution time, time-to-first-byte, and total download time:

.. code-block:: bash

   nadzoring network-base http-ping https://example.com

   # With response headers
   nadzoring network-base http-ping --show-headers https://github.com

   # Custom timeout, disable SSL verification
   nadzoring network-base http-ping --timeout 5 --no-ssl-verify https://self-signed.badssl.com

   # Phase-specific timeouts
   nadzoring network-base http-ping --connect-timeout 3 --read-timeout 15 https://slow.example.com

**Python API:**

.. code-block:: python

   from nadzoring.network_base.http_ping import http_ping
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=10.0)
   result = http_ping("https://example.com", timeout_config=config)
   if not result.error:
       print(result.status_code)    # 200
       print(result.dns_ms)         # e.g. 12.5
       print(result.ttfb_ms)        # e.g. 87.3
       print(result.total_ms)       # e.g. 134.6

----

8. DNS Health Check
---------------------

Score a domain's DNS configuration from 0 to 100:

.. code-block:: bash

   nadzoring dns health example.com

Scoring thresholds:

- **80–100** → Healthy
- **50–79** → Degraded
- **0–49** → Unhealthy

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.health import health_check_dns

   result = health_check_dns("example.com")
   print(result["score"])   # e.g. 85
   print(result["status"])  # 'healthy' | 'degraded' | 'unhealthy'
   for issue in result["issues"]:
       print("ISSUE:", issue)

----

9. Validate DNS Records
------------------------

Run a detailed DNS check including MX priority and SPF/DKIM validation:

.. code-block:: bash

   nadzoring dns check example.com

   # Check specific record types only
   nadzoring dns check -t MX -t TXT gmail.com

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.health import check_dns

   result = check_dns(
       "example.com",
       record_types=["MX", "TXT"],
       validate_mx=True,
       validate_txt=True,
   )
   print(result["records"])      # {'MX': ['10 mail.example.com'], ...}
   print(result["validations"])  # {'mx': {'valid': True, 'issues': []}}

----

10. Trace the DNS Resolution Path
----------------------------------

Follow the delegation chain from root servers to the authoritative answer:

.. code-block:: bash

   nadzoring dns trace example.com

   # Start from a specific nameserver instead of root
   nadzoring dns trace -n 8.8.8.8 google.com

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.trace import trace_dns

   result = trace_dns("example.com")
   for hop in result["hops"]:
       print(hop["nameserver"], hop["response_time"], hop.get("records"))

----

11. Compare DNS Servers
-----------------------

Detect discrepancies between multiple resolvers for the same domain:

.. code-block:: bash

   nadzoring dns compare example.com

   # Custom servers and record types
   nadzoring dns compare -t A -t MX -s 8.8.8.8 -s 1.1.1.1 -s 9.9.9.9 example.com

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.compare import compare_dns_servers

   result = compare_dns_servers(
       "example.com",
       servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
       record_types=["A", "MX"],
   )
   if result["differences"]:
       for diff in result["differences"]:
           print(f"Server {diff['server']} returned different records")

----

12. Detect DNS Poisoning
--------------------------

Check whether a domain's DNS responses show signs of poisoning, censorship,
or unusual CDN routing:

.. code-block:: bash

   nadzoring dns poisoning example.com

   # Custom control server with additional record types checked
   nadzoring dns poisoning -c 1.1.1.1 -a MX -a TXT google.com

   # Save as HTML report
   nadzoring dns poisoning -o html --save poisoning_report.html twitter.com

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.poisoning import check_dns_poisoning

   result = check_dns_poisoning("example.com")
   print(f"Level: {result.get('poisoning_level', 'NONE')}")
   print(f"Confidence: {result.get('confidence', 0):.0f}%")

----

13. Benchmark DNS Servers
---------------------------

Find the fastest DNS resolver for your location:

.. code-block:: bash

   # Benchmark all well-known public servers
   nadzoring dns benchmark

   # Custom servers, 20 queries each
   nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 9.9.9.9 --queries 20

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.benchmark import benchmark_dns_servers

   results = benchmark_dns_servers(
       servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
       queries=10,
   )
   for r in results:
       print(f"{r['server']}: avg={r['avg_response_time']:.1f}ms")

----

14. Continuous DNS Monitoring
-------------------------------

Monitor DNS health and performance over time, with alerts and logging:

.. code-block:: bash

   nadzoring dns monitor example.com \
       --interval 60 \
       --log-file dns_monitor.jsonl

   # Analyse the log later
   nadzoring dns monitor-report dns_monitor.jsonl

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.monitor import DNSMonitor, MonitorConfig, load_log
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=8.0)

   # Monitor for 10 cycles
   monitor_config = MonitorConfig(
       domain="example.com",
       interval=10.0,
       timeout_config=config,
   )
   monitor = DNSMonitor(monitor_config)
   history = monitor.run_cycles(10)

   # Analyse existing log
   cycles = load_log("dns_monitor.jsonl")
   print(f"Cycles: {len(cycles)}")

----

15. Scan Ports
---------------

Discover open ports and running services on a target:

.. code-block:: bash

   # Fast scan (common ports)
   nadzoring network-base port-scan example.com

   # Full scan (all 65535 ports)
   nadzoring network-base port-scan --mode full 192.168.1.1

   # Custom range
   nadzoring network-base port-scan --mode custom --ports 1-1024 example.com

   # With custom timeouts
   nadzoring network-base port-scan --connect-timeout 1 --read-timeout 3 example.com

**Python API:**

.. code-block:: python

   from nadzoring.network_base.port_scanner import ScanConfig, scan_ports
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=1.5, read=5.0)
   scan_config = ScanConfig(targets=["example.com"], mode="fast", timeout_config=config)
   for result in scan_ports(scan_config):
       print("Open ports:", result.open_ports)

----

16. Detect Service on Port
---------------------------

Actively connect to a port and identify the running service by banner:

.. code-block:: bash

   nadzoring network-base detect-service example.com 80 443 22

**Python API:**

.. code-block:: python

   from nadzoring.network_base.service_detector import detect_service_on_host
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=8.0)
   result = detect_service_on_host("example.com", 80, timeout_config=config)
   print(result.detected_service or result.guessed_service)

----

17. SSL/TLS Certificate Check
-------------------------------

Inspect SSL/TLS certificates for expiry and security:

.. code-block:: bash

   # Compact summary
   nadzoring security check-ssl example.com

   # 30-day warning window, full details
   nadzoring security check-ssl --days-before 30 --full example.com

   # Custom timeout for slow servers
   nadzoring security check-ssl --connect-timeout 10 example.com

**Python API:**

.. code-block:: python

   from nadzoring.security.check_website_ssl_cert import check_ssl_certificate
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=10.0)
   result = check_ssl_certificate("example.com", days_before=14, timeout_config=config)
   print(result["status"], result["remaining_days"])
   print(result["protocols"]["supported"])

----

18. HTTP Security Headers
--------------------------

Audit HTTP security headers for a URL:

.. code-block:: bash

   nadzoring security check-headers https://example.com

**Python API:**

.. code-block:: python

   from nadzoring.security.http_headers import check_http_security_headers
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=5.0, read=15.0)
   result = check_http_security_headers("https://example.com", timeout_config=config)
   print(result["score"])    # 0–100 coverage score
   print(result["missing"])  # list of absent headers

----

19. Email Security
-------------------

Validate SPF, DKIM, and DMARC records:

.. code-block:: bash

   nadzoring security check-email example.com

**Python API:**

.. code-block:: python

   from nadzoring.security.email_security import check_email_security

   result = check_email_security("example.com")
   print(result["overall_score"])         # 0–3
   print(result["spf"]["all_qualifier"])  # '~'
   print(result["dmarc"]["policy"])       # 'reject'

----

20. Subdomain Discovery
------------------------

Find subdomains using CT logs and DNS brute-force:

.. code-block:: bash

   nadzoring security subdomains example.com

**Python API:**

.. code-block:: python

   from nadzoring.security.subdomain_scan import scan_subdomains
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=8.0)
   results = scan_subdomains("example.com", timeout_config=config)
   for r in results:
       print(r["subdomain"], r["ip"], r["source"])

----

21. Continuous SSL Monitoring
-------------------------------

Monitor SSL certificates for changes and expiry:

.. code-block:: bash

   nadzoring security watch-ssl example.com

**Python API:**

.. code-block:: python

   from nadzoring.security.ssl_monitor import SSLMonitor
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=10.0)
   monitor = SSLMonitor(["example.com"], interval=3600, timeout_config=config)
   monitor.set_alert_callback(lambda d, m: print(f"ALERT {d}: {m}"))
   monitor.run_cycles(5)

----

22. ARP Cache and Spoofing Detection
--------------------------------------

Inspect the local ARP cache:

.. code-block:: bash

   nadzoring arp cache

Detect spoofing statically or in real-time:

.. code-block:: bash

   nadzoring arp detect-spoofing
   nadzoring arp monitor-spoofing --interface eth0 --timeout 60

**Python API:**

.. code-block:: python

   from nadzoring.arp.cache import ARPCache
   from nadzoring.arp.realtime import ARPRealtimeDetector
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(lifetime=45.0)
   cache = ARPCache()
   for entry in cache.get_cache():
       print(entry.ip_address, entry.mac_address)

   detector = ARPRealtimeDetector()
   alerts = detector.monitor(interface="eth0", count=50, timeout_config=config)

----

Output Formats
--------------

Use ``-o`` to change how results are displayed or saved:

.. code-block:: bash

   nadzoring dns resolve -o json example.com
   nadzoring dns health -o html --save health_report.html example.com
   nadzoring network-base connections -o csv --save conns.csv
   nadzoring security check-ssl -o json example.com

Available formats: ``table`` (default), ``json``, ``csv``, ``html``, ``html_table``, ``yaml``

----

Getting Help
------------

.. code-block:: bash

   # List all command groups
   nadzoring --help

   # List commands in a group
   nadzoring dns --help
   nadzoring network-base --help
   nadzoring security --help
   nadzoring arp --help

   # Help for a specific command
   nadzoring dns reverse --help
   nadzoring network-base port-scan --help
   nadzoring security check-ssl --help
