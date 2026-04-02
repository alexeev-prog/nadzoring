DNS Commands
============

The ``dns`` group provides all DNS analysis, monitoring, and security
commands.

.. code-block:: bash

   nadzoring dns --help

----

.. _dns-resolve:

dns resolve
-----------

Resolve one or more domain names for the specified DNS record types.

.. code-block:: text

   nadzoring dns resolve [OPTIONS] DOMAIN [DOMAIN ...]

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-t / --type``
     - ``A``
     - Record type to query. Repeatable. Use ``ALL`` for all types.
       Choices: ``A``, ``AAAA``, ``CNAME``, ``MX``, ``NS``, ``TXT``, ``ALL``
   * - ``-n / --nameserver``
     - system
     - Custom nameserver IP (e.g. ``8.8.8.8``)
   * - ``--short``
     - off
     - Compact output (one line per record)
   * - ``--show-ttl``
     - off
     - Include TTL value in output
   * - ``--format-style``
     - ``standard``
     - Output style: ``standard``, ``bind``, ``host``, ``dig``
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout for the entire operation (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds). Falls back to ``--timeout``.
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds). Falls back to ``--timeout``.

Examples
~~~~~~~~

.. code-block:: bash

   # Basic A record
   nadzoring dns resolve example.com

   # All record types
   nadzoring dns resolve -t ALL example.com

   # Multiple types
   nadzoring dns resolve -t MX -t TXT gmail.com

   # Show TTL; use Google DNS
   nadzoring dns resolve --show-ttl -n 8.8.8.8 example.com

   # Multiple domains
   nadzoring dns resolve example.com google.com github.com

   # JSON output saved to file
   nadzoring dns resolve -t A -t AAAA -o json --save out.json example.com

   # Custom timeouts for slow networks
   nadzoring dns resolve --connect-timeout 10 --read-timeout 20 example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer
   from nadzoring.utils.timeout import TimeoutConfig

   # Using default timeouts
   result = resolve_with_timer("example.com", "A")
   if result["error"]:
       print("Error:", result["error"])
   else:
       print(result["records"])        # ['93.184.216.34']
       print(result["response_time"])  # e.g. 42.5

   # With TTL and custom nameserver
   result = resolve_with_timer(
       "example.com",
       "MX",
       nameserver="8.8.8.8",
       include_ttl=True,
   )
   print(result["records"])  # ['10 mail.example.com']
   print(result["ttl"])      # e.g. 3600

   # Custom timeout configuration
   config = TimeoutConfig(connect=3.0, read=8.0, lifetime=20.0)
   result = resolve_with_timer("example.com", "A", timeout_config=config)

----

.. _dns-reverse:

dns reverse
-----------

Perform reverse DNS lookup (PTR record) for one or more IP addresses.

.. code-block:: text

   nadzoring dns reverse [OPTIONS] IP [IP ...]

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-n / --nameserver``
     - system
     - Custom nameserver IP
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds)
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds)

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns reverse 8.8.8.8
   nadzoring dns reverse 1.1.1.1 8.8.8.8 9.9.9.9
   nadzoring dns reverse -n 208.67.222.222 8.8.4.4
   nadzoring dns reverse -o json --save reverse.json 8.8.8.8

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.reverse import reverse_dns
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=5.0)

   result = reverse_dns("8.8.8.8", timeout_config=config)

   if result["error"]:
       print("Lookup failed:", result["error"])
       # "No PTR record", "No reverse DNS", "Query timeout",
       # "Invalid IP address: …"
   else:
       print(result["hostname"])      # 'dns.google'
       print(result["response_time"]) # e.g. 18.3

   # IPv6
   result = reverse_dns("2001:4860:4860::8888")
   print(result["hostname"])  # 'dns.google'

----

.. _dns-health:

dns health
----------

Score a domain's DNS configuration from 0 to 100.

.. code-block:: text

   nadzoring dns health [OPTIONS] DOMAIN

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-n / --nameserver``
     - system
     - Custom nameserver IP
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds)
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds)

Scoring thresholds:

- **80–100** → Healthy
- **50–79** → Degraded
- **0–49** → Unhealthy

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns health example.com
   nadzoring dns health -n 1.1.1.1 google.com
   nadzoring dns health -o json --save health.json example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.health import health_check_dns
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=8.0)
   result = health_check_dns("example.com", timeout_config=config)

   print(f"Score: {result['score']}/100")
   print(f"Status: {result['status']}")  # healthy | degraded | unhealthy

   for issue in result["issues"]:
       print("  CRITICAL:", issue)
   for warn in result["warnings"]:
       print("  WARN:", warn)
   for rtype, score in result["record_scores"].items():
       print(f"  {rtype}: {score}/100")

----

.. _dns-check:

dns check
---------

Detailed per-record-type DNS check with optional MX and TXT validation.

.. code-block:: text

   nadzoring dns check [OPTIONS] DOMAIN

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-t / --type``
     - all types
     - Record type to check (repeatable)
   * - ``--validate-mx``
     - off
     - Validate MX priority uniqueness
   * - ``--validate-txt``
     - off
     - Validate SPF and DKIM TXT records
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds)
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds)

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns check example.com
   nadzoring dns check -t MX -t TXT --validate-mx --validate-txt gmail.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.health import check_dns
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=10.0)
   result = check_dns(
       "example.com",
       record_types=["MX", "TXT"],
       validate_mx=True,
       validate_txt=True,
       timeout_config=config,
   )

   print(result["records"])
   # {'MX': ['10 mail.example.com'], 'TXT': ['v=spf1 ...']}

   print(result["errors"])
   # {'AAAA': 'No AAAA records'}  — only failed types appear here

   print(result["validations"])
   # {'mx': {'valid': True, 'issues': [], 'warnings': []},
   #  'txt': {'valid': True, 'issues': [], 'warnings': [...]}}

----

.. _dns-trace:

dns trace
---------

Follow the DNS delegation chain from root servers to the authoritative
answer (equivalent to ``dig +trace``).

.. code-block:: text

   nadzoring dns trace [OPTIONS] DOMAIN

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-n / --nameserver``
     - root (198.41.0.4)
     - Starting nameserver IP
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds)
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds)

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns trace example.com
   nadzoring dns trace -n 8.8.8.8 google.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.trace import trace_dns
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=5.0, lifetime=30.0)
   result = trace_dns("example.com", timeout_config=config)

   for hop in result["hops"]:
       ns = hop["nameserver"]
       rtt = f"{hop['response_time']} ms" if hop["response_time"] else "timeout"
       err = f" ERROR: {hop['error']}" if hop.get("error") else ""
       print(f"  {ns}  {rtt}{err}")
       for rec in hop.get("records", []):
           print(f"    {rec}")

   if result["final_answer"]:
       print("Final answer:", result["final_answer"]["records"])
   else:
       print("No authoritative answer found")

----

.. _dns-compare:

dns compare
-----------

Compare DNS responses from multiple servers to detect discrepancies.

.. code-block:: text

   nadzoring dns compare [OPTIONS] DOMAIN

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-s / --server``
     - Google + Cloudflare
     - Nameserver to include (repeatable)
   * - ``-t / --type``
     - ``A``
     - Record type (repeatable)

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns compare example.com
   nadzoring dns compare -t A -t MX -s 8.8.8.8 -s 1.1.1.1 -s 9.9.9.9 example.com

Python API
~~~~~~~~~~

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
               f" {diff['type']} records"
           )
           print(f"  Expected: {diff['expected']}")
           print(f"  Got:      {diff['got']}")

----

.. _dns-benchmark:

dns benchmark
-------------

Measure the performance of multiple DNS resolvers.

.. code-block:: text

   nadzoring dns benchmark [OPTIONS]

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-s / --server``
     - all public
     - Nameserver to benchmark (repeatable)
   * - ``-d / --domain``
     - ``google.com``
     - Domain to query
   * - ``-t / --type``
     - ``A``
     - Record type
   * - ``--queries``
     - ``10``
     - Queries per server
   * - ``--parallel/--sequential``
     - ``--parallel``
     - Run benchmarks concurrently or sequentially
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds)
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds)

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns benchmark
   nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 --queries 20
   nadzoring dns benchmark -t MX -d gmail.com --sequential

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.benchmark import benchmark_dns_servers
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=8.0, lifetime=60.0)

   results = benchmark_dns_servers(
       servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
       queries=10,
       timeout_config=config,
   )
   # Results are sorted fastest-first
   for r in results:
       print(
           f"{r['server']}: "
           f"avg={r['avg_response_time']:.1f}ms  "
           f"min={r['min_response_time']:.1f}ms  "
           f"ok={r['success_rate']}%"
       )

----

.. _dns-poisoning:

dns poisoning
-------------

Check whether DNS responses show signs of poisoning, censorship, or CDN
routing anomalies.

.. code-block:: text

   nadzoring dns poisoning [OPTIONS] DOMAIN

Severity levels: ``NONE`` → ``LOW`` → ``MEDIUM`` → ``HIGH`` → ``CRITICAL`` / ``SUSPICIOUS``

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-c / --control-server``
     - ``8.8.8.8``
     - Trusted control nameserver
   * - ``-t / --test-servers``
     - all public
     - Servers to test against control
   * - ``-T / --type``
     - ``A``
     - Primary record type
   * - ``-a / --additional-types``
     - none
     - Additional record types to query on control server
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds)
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds)

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns poisoning example.com
   nadzoring dns poisoning -c 1.1.1.1 -a MX -a TXT google.com
   nadzoring dns poisoning -o html --save report.html twitter.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.poisoning import check_dns_poisoning
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=10.0, lifetime=45.0)
   result = check_dns_poisoning("example.com", timeout_config=config)

   print(f"Level: {result.get('poisoning_level', 'NONE')}")
   print(f"Confidence: {result.get('confidence', 0):.0f}%")

   if result.get("poisoned"):
       for inc in result.get("inconsistencies", []):
           print("Inconsistency:", inc)

   if result.get("cdn_detected"):
       print(f"CDN: {result['cdn_owner']} ({result['cdn_percentage']:.0f}%)")

----

.. _dns-monitor:

dns monitor
-----------

Continuously monitor DNS health and performance for a domain, logging
each cycle to a structured JSONL file.

See :doc:`/monitoring_dns` for the full monitoring guide.

.. code-block:: text

   nadzoring dns monitor [OPTIONS] DOMAIN

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``-n / --nameserver``
     - 8.8.8.8, 1.1.1.1
     - Nameserver to monitor (repeatable)
   * - ``--interval``
     - ``60``
     - Seconds between check cycles
   * - ``-t / --type``
     - ``A``
     - Record type: A, AAAA, MX, NS, TXT
   * - ``-q / --queries``
     - ``3``
     - Queries per server per cycle
   * - ``--max-rt``
     - ``500``
     - Alert threshold: max response time (ms)
   * - ``--min-success``
     - ``0.95``
     - Alert threshold: minimum success rate (0–1)
   * - ``--no-health``
     - off
     - Skip health check each cycle
   * - ``-l / --log-file``
     - none
     - Path to JSONL log file
   * - ``-c / --cycles``
     - ``0``
     - Number of cycles to run (0 = infinite)
   * - ``--timeout``
     - ``30.0``
     - Lifetime timeout (seconds)
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds)
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds)

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns monitor example.com \
       --interval 60 \
       --log-file dns_monitor.jsonl

   nadzoring dns monitor example.com \
       -n 8.8.8.8 -n 1.1.1.1 -n 9.9.9.9 \
       --interval 30 --max-rt 150 --min-success 0.99 \
       --log-file /var/log/dns_monitor.jsonl

----

.. _dns-monitor-report:

dns monitor-report
------------------

Analyse a JSONL log file created by ``dns monitor``.

.. code-block:: text

   nadzoring dns monitor-report [OPTIONS] LOG_FILE

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Option
     - Description
   * - ``-s / --server``
     - Filter statistics to a specific server IP

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns monitor-report dns_monitor.jsonl
   nadzoring dns monitor-report dns_monitor.jsonl --server 8.8.8.8 -o json

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.monitor import load_log
   from statistics import mean

   cycles = load_log("dns_monitor.jsonl")
   rts = [
       s["avg_response_time_ms"]
       for c in cycles
       for s in c["samples"]
       if s["avg_response_time_ms"] is not None
   ]
   print(f"Mean RT: {mean(rts):.2f}ms")
   print(f"Total cycles: {len(cycles)}")
