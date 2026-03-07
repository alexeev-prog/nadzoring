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
   * - ``--show-ttl``
     - off
     - Include TTL value in output
   * - ``--timeout``
     - ``5.0``
     - Per-query timeout in seconds
   * - ``--lifetime``
     - ``10.0``
     - Total query lifetime in seconds

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

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer

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

   result = reverse_dns("8.8.8.8")

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

Scoring thresholds:

- **80–100** → Healthy
- **50–79** → Degraded
- **0–49** → Unhealthy

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns health example.com
   nadzoring dns health -n 1.1.1.1 example.com
   nadzoring dns health -o json --save health.json example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.health import health_check_dns

   result = health_check_dns("example.com")

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

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns check example.com
   nadzoring dns check -t MX -t TXT --validate-mx --validate-txt gmail.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.health import check_dns

   result = check_dns(
       "example.com",
       record_types=["MX", "TXT"],
       validate_mx=True,
       validate_txt=True,
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

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring dns trace example.com
   nadzoring dns trace -n 8.8.8.8 google.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.trace import trace_dns

   result = trace_dns("example.com")

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
   * - ``--sequential``
     - off
     - Disable parallel benchmarking

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

   results = benchmark_dns_servers(
       servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
       queries=10,
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
   * - ``-c / --control``
     - ``8.8.8.8``
     - Trusted control nameserver
   * - ``-a / --additional``
     - none
     - Additional record types to check
   * - ``-t / --type``
     - ``A``
     - Primary record type

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

   result = check_dns_poisoning("example.com")

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
   * - ``--cycles``
     - unlimited
     - Number of cycles to run (0 = infinite)
   * - ``--max-rt``
     - ``300``
     - Alert threshold: max response time (ms)
   * - ``--min-success``
     - ``0.95``
     - Alert threshold: minimum success rate (0–1)
   * - ``--log-file``
     - none
     - Path to JSONL log file

----

dns monitor-report
------------------

Analyse a JSONL log file created by ``dns monitor``.

.. code-block:: text

   nadzoring dns monitor-report [OPTIONS] LOG_FILE

.. code-block:: bash

   nadzoring dns monitor-report dns_monitor.jsonl
   nadzoring dns monitor-report dns_monitor.jsonl --server 8.8.8.8 -o json
