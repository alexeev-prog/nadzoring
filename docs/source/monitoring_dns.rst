Continuous DNS Monitoring
=========================

Nadzoring provides a built-in monitoring loop that periodically checks one
or more DNS servers, tracks trends over time, fires threshold-based alerts,
and persists all results to a JSONL log for later analysis.

----

Quick Start
-----------

Monitor ``example.com`` against two DNS servers every 60 seconds:

.. code-block:: bash

   nadzoring dns monitor example.com \
       -n 8.8.8.8 -n 1.1.1.1 \
       --interval 60 \
       --log-file dns_monitor.jsonl

Press **Ctrl-C** to stop. A statistical summary prints automatically.

Analyse the log afterwards:

.. code-block:: bash

   nadzoring dns monitor-report dns_monitor.jsonl
   nadzoring dns monitor-report dns_monitor.jsonl --server 8.8.8.8 -o json

----

CLI Reference: ``dns monitor``
--------------------------------

.. code-block:: text

   nadzoring dns monitor [OPTIONS] DOMAIN

.. list-table::
   :header-rows: 1
   :widths: 24 6 52 18

   * - Option
     - Short
     - Description
     - Default
   * - ``--nameservers``
     - ``-n``
     - DNS server IP to monitor (repeatable)
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
     - Skip health check each cycle
     - ``False``
   * - ``--log-file``
     - ``-l``
     - JSONL file to append all cycle results to
     - None
   * - ``--cycles``
     - ``-c``
     - Stop after N cycles (0 = indefinite)
     - ``0``
   * - ``--output``
     - ``-o``
     - Output format: table, json, csv, html
     - ``table``
   * - ``--quiet``
     -
     - Suppress all console output
     - ``False``
   * - ``--timeout``
     -
     - Lifetime timeout (seconds)
     - ``30.0``
   * - ``--connect-timeout``
     -
     - Connection timeout (seconds). Falls back to ``--timeout``.
     - ``5.0``
   * - ``--read-timeout``
     -
     - Read timeout (seconds). Falls back to ``--timeout``.
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

   # Custom timeouts for slow networks
   nadzoring dns monitor example.com \
       --connect-timeout 10 --read-timeout 20 --interval 60

----

CLI Reference: ``dns monitor-report``
---------------------------------------

Analyse a saved JSONL log and print aggregated per-server statistics:

.. code-block:: text

   nadzoring dns monitor-report [OPTIONS] LOG_FILE

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--server / -s``
     - Filter statistics to a specific server IP

.. code-block:: bash

   # Basic analysis
   nadzoring dns monitor-report dns_monitor.jsonl

   # Filter to a single server, export JSON
   nadzoring dns monitor-report dns_monitor.jsonl --server 8.8.8.8 -o json

   # Save as HTML report for dashboard
   nadzoring dns monitor-report dns_monitor.jsonl -o html --save report.html

----

What Happens Each Cycle
------------------------

1. **Benchmark** — sends ``--queries`` queries to each server and records
   average, min, and max response times plus the success rate.

2. **Resolve** — one additional query captures the current DNS records
   returned by each server.

3. **Health check** (skip with ``--no-health``) — computes an overall
   score (0–100) across A, AAAA, MX, NS, TXT, and CNAME records.

4. **Threshold evaluation** — compares metrics against configured
   thresholds and generates alert events for any breaches.

5. **Alert dispatch** — calls the configured ``alert_callback`` (if any)
   and prints warnings to the console.

6. **Persistence** — appends a JSON line to the log file (if configured).

7. **Sleep** — waits ``--interval`` seconds before the next cycle.

----

Alert Types
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Type
     - Triggered when
   * - ``resolution_failure``
     - All queries failed (success rate = 0 %)
   * - ``high_latency``
     - Average response time exceeds ``--max-rt``
   * - ``low_success_rate``
     - Success rate falls below ``--min-success``
   * - ``health_degraded``
     - DNS health score drops below 80

----

Log File Format
---------------

Each line in the JSONL log is a complete cycle result:

.. code-block:: json

   {
     "cycle": 42,
     "timestamp": "2025-06-01T14:23:10.123456+00:00",
     "domain": "example.com",
     "samples": [
       {
         "server": "8.8.8.8",
         "timestamp": "2025-06-01T14:23:10.123456+00:00",
         "avg_response_time_ms": 18.4,
         "min_response_time_ms": 14.1,
         "max_response_time_ms": 24.7,
         "success_rate": 1.0,
         "records": ["93.184.216.34"],
         "error": null
       }
     ],
     "health_score": 85,
     "health_status": "healthy",
     "alerts": []
   }

----

Python API
----------

Basic continuous monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.monitor import DNSMonitor, MonitorConfig
   from nadzoring.utils.timeout import TimeoutConfig

   timeout_config = TimeoutConfig(connect=3.0, read=10.0, lifetime=30.0)

   config = MonitorConfig(
       domain="example.com",
       nameservers=["8.8.8.8", "1.1.1.1"],
       interval=60.0,
       max_response_time_ms=500.0,
       min_success_rate=0.95,
       log_file="dns_monitor.jsonl",
       timeout_config=timeout_config,
   )

   monitor = DNSMonitor(config)
   monitor.run()
   print(monitor.report())

Custom alert callback
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests
   from nadzoring.dns_lookup.monitor import AlertEvent, DNSMonitor, MonitorConfig
   from nadzoring.utils.timeout import TimeoutConfig

   SLACK_WEBHOOK = "https://hooks.slack.com/services/T.../B.../..."

   timeout_config = TimeoutConfig(connect=2.0, read=8.0)


   def send_slack_alert(alert: AlertEvent) -> None:
       requests.post(
           SLACK_WEBHOOK,
           json={"text": f":warning: *{alert.alert_type}* — {alert.message}"},
           timeout=5,
       )


   config = MonitorConfig(
       domain="example.com",
       nameservers=["8.8.8.8"],
       interval=30.0,
       max_response_time_ms=200.0,
       alert_callback=send_slack_alert,
       timeout_config=timeout_config,
   )
   DNSMonitor(config).run()

Finite-cycle monitoring (CI / cron)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.monitor import DNSMonitor, MonitorConfig
   from nadzoring.utils.timeout import TimeoutConfig
   from statistics import mean

   timeout_config = TimeoutConfig(connect=2.0, read=8.0)

   config = MonitorConfig(
       domain="example.com",
       nameservers=["8.8.8.8", "1.1.1.1"],
       interval=10.0,
       queries_per_sample=5,
       run_health_check=False,
       timeout_config=timeout_config,
   )
   monitor = DNSMonitor(config)
   history = monitor.run_cycles(6)

   rts = [
       s.avg_response_time_ms
       for c in history
       for s in c.samples
       if s.avg_response_time_ms is not None
   ]
   print(f"Mean RT over {len(history)} cycles: {mean(rts):.1f}ms")
   print(monitor.report())

Analysing a historical log
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nadzoring.dns_lookup.monitor import load_log
   from statistics import mean

   cycles = load_log("dns_monitor.jsonl")

   rts = [
       s["avg_response_time_ms"]
       for c in cycles
       for s in c["samples"]
       if s["server"] == "8.8.8.8" and s["avg_response_time_ms"] is not None
   ]
   alerts = [a for c in cycles for a in c.get("alerts", [])]

   print(f"Cycles      : {len(cycles)}")
   print(f"Avg RT (ms) : {mean(rts):.2f}")
   print(f"Alerts      : {len(alerts)}")

----

Scheduling
----------

Cron (one cycle per minute)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: cron

   * * * * * root nadzoring dns monitor example.com \
       --cycles 1 --quiet \
       --log-file /var/log/nadzoring/dns_monitor.jsonl

.. note::

   Use ``--cycles 1`` with cron — the process exits after one check
   and cron handles the interval.

systemd service (recommended for production)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``/etc/systemd/system/nadzoring-dns-monitor.service``:

.. code-block:: ini

   [Unit]
   Description=Nadzoring DNS Monitor
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=nobody
   ExecStart=/usr/local/bin/nadzoring dns monitor example.com \
       -n 8.8.8.8 -n 1.1.1.1 \
       --interval 60 \
       --max-rt 300 \
       --min-success 0.95 \
       --log-file /var/log/nadzoring/dns_monitor.jsonl \
       --quiet
   Restart=on-failure
   RestartSec=10
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target

.. code-block:: bash

   sudo systemctl daemon-reload
   sudo systemctl enable --now nadzoring-dns-monitor
   sudo journalctl -u nadzoring-dns-monitor -f

----

Complete Automation Script
---------------------------

.. code-block:: bash

   #!/usr/bin/env bash
   # dns_health_check.sh — hourly DNS health snapshot for cron
   set -euo pipefail

   DOMAIN="${1:-example.com}"
   LOG_DIR="/var/log/nadzoring"
   TODAY=$(date -u +%Y%m%d)
   TS=$(date -u +%Y%m%d_%H%M%S)
   DAILY_LOG="${LOG_DIR}/dns_monitor_${TODAY}.jsonl"
   REPORT_DIR="/var/www/html/dns-reports"

   mkdir -p "$LOG_DIR" "$REPORT_DIR"

   nadzoring dns monitor "$DOMAIN" \
       -n 8.8.8.8 -n 1.1.1.1 \
       --cycles 1 --max-rt 300 --min-success 0.95 \
       --log-file "$DAILY_LOG" --quiet

   nadzoring dns health "$DOMAIN" \
       -o json --save "${LOG_DIR}/health_${TS}.json" --quiet

   nadzoring dns benchmark --domain "$DOMAIN" --queries 5 \
       -o json --save "${LOG_DIR}/benchmark_${TS}.json" --quiet

   nadzoring dns monitor-report "$DAILY_LOG" \
       -o html --save "${REPORT_DIR}/report_${TODAY}.html"

   find "$LOG_DIR" -name "dns_monitor_*.jsonl" -mtime +30 -delete
   find "$LOG_DIR" -name "health_*.json"       -mtime +7  -delete
   find "$LOG_DIR" -name "benchmark_*.json"    -mtime +7  -delete
