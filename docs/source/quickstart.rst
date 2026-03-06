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

The three command groups are ``dns``, ``network-base``, and ``arp``.

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
     - Output format: ``table``, ``json``, ``csv``, ``html``, ``html_table``
     - ``table``
   * - ``--save``
     -
     - Save results to a file
     - None

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

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer

   result = resolve_with_timer("example.com", "A")
   if not result["error"]:
       print(result["records"])       # ['93.184.216.34']
       print(result["response_time"]) # e.g. 42.5 ms

----

3. Reverse DNS Lookup
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
   print(result["hostname"])       # 'dns.google'
   print(result["response_time"])  # e.g. 18.34 ms

   # IPv6 also supported
   result = reverse_dns("2001:4860:4860::8888")
   print(result["hostname"])       # 'dns.google'

   # Handle errors
   result = reverse_dns("192.168.1.1")
   if result["error"]:
       print(result["error"])  # 'No PTR record'

----

4. Ping a Host
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

5. HTTP Probe a URL
---------------------

Measure DNS resolution time, time-to-first-byte, and total download time:

.. code-block:: bash

   nadzoring network-base http-ping https://example.com

   # With response headers
   nadzoring network-base http-ping --show-headers https://github.com

   # Custom timeout, disable SSL verification
   nadzoring network-base http-ping --timeout 5 --no-ssl-verify https://self-signed.badssl.com

**Python API:**

.. code-block:: python

   from nadzoring.network_base.http_ping import http_ping

   result = http_ping("https://example.com")
   print(result.status_code)   # 200
   print(result.dns_ms)        # e.g. 12.5
   print(result.ttfb_ms)       # e.g. 87.3
   print(result.total_ms)      # e.g. 134.6
   print(result.content_length) # bytes

----

6. DNS Health Check
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
   for warn in result["warnings"]:
       print("WARN:", warn)

----

7. Validate DNS Records
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
   print(result["validations"])  # {'mx': {'valid': True, 'issues': [], ...}}

----

8. Trace the DNS Resolution Path
----------------------------------

Follow the delegation chain from root servers to the authoritative answer,
similar to ``dig +trace``:

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
   print("Final answer:", result["final_answer"])

----

9. Compare DNS Servers
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
           print(f"Server {diff['server']} returned different {diff['type']} records")
           print(f"  Expected: {diff['expected']}")
           print(f"  Got:      {diff['got']}")

----

10. Detect DNS Poisoning
--------------------------

Check whether a domain's DNS responses show signs of poisoning, censorship,
or unusual CDN routing:

.. code-block:: bash

   nadzoring dns poisoning example.com

   # Custom control server with additional record types checked
   nadzoring dns poisoning -c 1.1.1.1 -a MX -a TXT google.com

   # Save as HTML report
   nadzoring dns poisoning -o html --save poisoning_report.html twitter.com

Severity levels: ``NONE`` → ``LOW`` → ``MEDIUM`` → ``HIGH`` → ``CRITICAL`` / ``SUSPICIOUS``

----

11. Benchmark DNS Servers
---------------------------

Find the fastest DNS resolver for your location:

.. code-block:: bash

   # Benchmark all well-known public servers
   nadzoring dns benchmark

   # Custom servers, 20 queries each
   nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 9.9.9.9 --queries 20

   # Sequential mode (one server at a time)
   nadzoring dns benchmark -t MX -d gmail.com --sequential

**Python API:**

.. code-block:: python

   from nadzoring.dns_lookup.benchmark import benchmark_dns_servers

   results = benchmark_dns_servers(
       servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
       queries=10,
   )
   for r in results:
       print(f"{r['server']}: avg={r['avg_response_time']:.1f}ms  ok={r['success_rate']}%")

----

12. Scan Ports
---------------

Discover open ports and running services on a target:

.. code-block:: bash

   # Fast scan (common ports)
   nadzoring network-base port-scan example.com

   # Full scan (all 65535 ports)
   nadzoring network-base port-scan --mode full 192.168.1.1

   # Custom range
   nadzoring network-base port-scan --mode custom --ports 1-1024 example.com

   # UDP scan
   nadzoring network-base port-scan --protocol udp --mode fast example.com

----

13. ARP Cache and Spoofing Detection
--------------------------------------

Inspect the local ARP cache:

.. code-block:: bash

   nadzoring arp cache

Statically detect potential spoofing from current cache:

.. code-block:: bash

   nadzoring arp detect-spoofing

   # Check only specific interfaces
   nadzoring arp detect-spoofing eth0 wlan0

Monitor ARP traffic in real time (requires root/admin):

.. code-block:: bash

   nadzoring arp monitor-spoofing --interface eth0 --count 200 --timeout 60

   # Save alerts for forensic analysis
   nadzoring arp monitor-spoofing -o json --save arp_alerts.json

----

Output Formats
--------------

Use ``-o`` to change how results are displayed or saved:

.. code-block:: bash

   nadzoring dns resolve -o json example.com
   nadzoring dns health -o html --save health_report.html example.com
   nadzoring network-base connections -o csv --save conns.csv

Available formats: ``table`` (default), ``json``, ``csv``, ``html``, ``html_table``

----

Getting Help
------------

.. code-block:: bash

   # List all command groups
   nadzoring --help

   # List commands in a group
   nadzoring dns --help
   nadzoring network-base --help
   nadzoring arp --help

   # Help for a specific command
   nadzoring dns reverse --help
   nadzoring network-base port-scan --help
   nadzoring arp monitor-spoofing --help

----

14. Continuous DNS Monitoring
-------------------------------

The ``dns monitor`` command runs a persistent loop that tracks health and
performance over time, fires alerts when thresholds are breached, and logs
everything to a structured JSONL file.

.. code-block:: bash

   # Monitor with default servers (Google + Cloudflare), save log
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

After Ctrl-C (or after ``--cycles`` completes), a statistical summary is
printed automatically.

**Analyse the log later:**

.. code-block:: bash

   nadzoring dns monitor-report dns_monitor.jsonl
   nadzoring dns monitor-report dns_monitor.jsonl --server 8.8.8.8 -o json

**Python API — embed in your own script:**

.. code-block:: python

   from nadzoring.dns_lookup.monitor import AlertEvent, DNSMonitor, MonitorConfig


   def my_alert_handler(alert: AlertEvent) -> None:
       print(f"ALERT [{alert.alert_type}]: {alert.message}")


   config = MonitorConfig(
       domain="example.com",
       nameservers=["8.8.8.8", "1.1.1.1"],
       interval=60.0,
       queries_per_sample=3,
       max_response_time_ms=300.0,
       min_success_rate=0.95,
       log_file="dns_monitor.jsonl",
       alert_callback=my_alert_handler,
   )

   monitor = DNSMonitor(config)
   monitor.run()
   print(monitor.report())

**Scheduling with systemd (recommended for production):**

.. code-block:: bash

   # Create /etc/systemd/system/nadzoring-dns-monitor.service
   # then:
   sudo systemctl enable --now nadzoring-dns-monitor
   sudo journalctl -u nadzoring-dns-monitor -f

See :doc:`monitoring` for the full systemd unit file, cron setup, trend
analysis examples, and alert integration patterns.

----

15. Error Handling Patterns
-----------------------------

Every public Python API function returns structured errors rather than
raising exceptions, making it safe to use in automation scripts:

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer
   from nadzoring.dns_lookup.reverse import reverse_dns
   from nadzoring.dns_lookup.health import health_check_dns

   # resolve_with_timer never raises — check the "error" field
   result = resolve_with_timer("example.com", "A", timeout=3.0)
   if result["error"]:
       # possible: 'Domain does not exist', 'Query timeout', 'No A records'
       print("DNS error:", result["error"])
   else:
       print("Records:", result["records"])
       print("Response time:", result["response_time"], "ms")

   # reverse_dns — same pattern
   r = reverse_dns("8.8.8.8")
   hostname = r["hostname"] or f"[{r['error']}]"

   # health_check_dns always returns a complete dict
   health = health_check_dns("example.com")
   if health["status"] == "unhealthy":
       for issue in health["issues"]:
           print("CRITICAL:", issue)
   for warning in health["warnings"]:
       print("WARN:", warning)
