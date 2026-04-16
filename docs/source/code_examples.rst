===============
Code Examples
===============

Practical examples for common use cases.

----

DNS Diagnostics
---------------

.. code-block:: bash

   nadzoring dns health example.com
   nadzoring dns trace example.com
   nadzoring dns compare -t A -t MX example.com
   nadzoring dns check -t ALL -v example.com

----

Reverse DNS Batch Lookup
------------------------

.. code-block:: bash

   # Look up multiple IPs at once
   nadzoring dns reverse 8.8.8.8 1.1.1.1 9.9.9.9 208.67.222.222

   # Save results
   nadzoring dns reverse -o json --save ptr_records.json 8.8.8.8 1.1.1.1

----

DNS Poisoning Detection
-----------------------

.. code-block:: bash

   nadzoring dns poisoning -v twitter.com
   nadzoring dns poisoning -c 8.8.8.8 -c 1.1.1.1 example.com
   nadzoring dns poisoning -o html --save poisoning_report.html github.com

----

DNS Performance Benchmarking
----------------------------

.. code-block:: bash

   nadzoring dns benchmark --queries 20 --parallel
   nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 208.67.222.222 -s 9.9.9.9
   nadzoring dns benchmark -t MX -d gmail.com --queries 15

----

Port Scanning
-------------

.. code-block:: bash

   nadzoring network-base port-scan --mode full --protocol tcp example.com
   nadzoring network-base port-scan --mode custom --ports 20-1024 example.com
   nadzoring network-base port-scan -o csv --save network_scan.csv 192.168.1.1

----

HTTP Service Probing
--------------------

.. code-block:: bash

   nadzoring network-base http-ping --show-headers https://api.example.com/health
   nadzoring network-base http-ping https://google.com https://cloudflare.com https://github.com
   nadzoring network-base http-ping -o csv --save http_metrics.csv https://example.com

----

SSL/TLS Certificate Auditing
----------------------------

.. code-block:: bash

   # Quick check — compact summary
   nadzoring security check-ssl example.com

   # Check multiple domains with a 30-day warning window
   nadzoring security check-ssl --days-before 30 google.com github.com cloudflare.com ya.ru

   # Full details including SAN list, protocol versions, chain info
   nadzoring security check-ssl --full example.com

   # Check without verifying the chain (self-signed / internal CA)
   nadzoring security check-ssl --no-verify https://internal.corp.example.com

   # Save full report as JSON
   nadzoring security check-ssl --full -o json --save ssl_audit.json example.com github.com

----

HTTP Security Header Auditing
-----------------------------

.. code-block:: bash

   # Single URL
   nadzoring security check-headers https://example.com

   # Batch audit of several services
   nadzoring security check-headers \
       https://api.example.com \
       https://admin.example.com \
       https://static.example.com

   # Skip SSL verification for internal endpoints
   nadzoring security check-headers --no-verify https://internal.corp.example.com

   # Export as JSON for CI / dashboard integration
   nadzoring security check-headers -o json --save headers_audit.json https://example.com

----

Email Security Validation
-------------------------

.. code-block:: bash

   # Check a single domain
   nadzoring security check-email example.com

   # Audit multiple domains
   nadzoring security check-email gmail.com outlook.com yahoo.com proton.me

   # Export full JSON report with SPF/DKIM/DMARC details
   nadzoring security check-email -o json --save email_audit.json example.com

   # Check all your owned domains at once
   nadzoring security check-email corp.example.com mail.example.com newsletter.example.com

----

Subdomain Discovery
-------------------

.. code-block:: bash

   # CT logs + built-in wordlist brute-force
   nadzoring security subdomains example.com

   # CT logs only — faster, no DNS brute-force
   nadzoring security subdomains --no-bruteforce example.com

   # Custom wordlist and more threads for deeper scanning
   nadzoring security subdomains \
       --wordlist /path/to/big-wordlist.txt \
       --threads 100 \
       --connect-timeout 5 \
       example.com

   # Save discovered subdomains as JSON
   nadzoring security subdomains -o json --save subdomains.json example.com

----

Continuous SSL Monitoring
-------------------------

.. code-block:: bash

   # Monitor a single domain indefinitely (Ctrl-C to stop)
   nadzoring security watch-ssl example.com

   # Monitor multiple domains with a 14-day warning threshold
   nadzoring security watch-ssl --days-before 14 \
       example.com github.com cloudflare.com api.example.com

   # Check every 5 minutes for a critical service
   nadzoring security watch-ssl --interval 300 api.example.com

   # Run 10 cycles with a 60-second interval and save all results
   nadzoring security watch-ssl --cycles 10 --interval 60 \
       -o json --save ssl_monitor_history.json example.com

----

ARP Spoofing Detection
----------------------

.. code-block:: bash

   nadzoring arp detect-spoofing eth0
   nadzoring arp monitor-spoofing --interface eth0 --timeout 60
   nadzoring arp monitor-spoofing -o json --save arp_alerts.json

----

Network Path Analysis
---------------------

.. code-block:: bash

   nadzoring network-base traceroute --max-hops 30 github.com
   nadzoring network-base traceroute google.com cloudflare.com amazon.com
   nadzoring network-base route
   nadzoring network-base connections --state LISTEN

----

Complete Network Diagnostics
----------------------------

.. code-block:: bash

   nadzoring network-base params -v
   nadzoring network-base host-to-ip google.com cloudflare.com github.com
   nadzoring network-base ping 8.8.8.8 1.1.1.1 google.com
   nadzoring network-base geolocation 8.8.8.8 1.1.1.1
   nadzoring network-base domain-info example.com
   nadzoring network-base port-scan --mode fast example.com
   nadzoring network-base traceroute cloudflare.com
   nadzoring security check-ssl example.com
   nadzoring security check-headers https://example.com
   nadzoring security check-email example.com
   nadzoring arp cache

----

Automated DNS Server Monitoring
-------------------------------

This section covers three integration approaches for continuous monitoring:
a **shell script** for use with cron/systemd, a **Python script** for
in-process loops with alerting, and **scheduling setup** for both Linux and Windows.

**Shell script with alerting thresholds**

Save as ``dns_monitor.sh`` and make executable (``chmod +x dns_monitor.sh``):

.. code-block:: bash

   #!/bin/bash
   # dns_monitor.sh — continuous DNS health and performance monitor
   # Designed to be called by cron or systemd timer.

   set -euo pipefail

   # ── Configuration ────────────────────────────────────────────────────────────
   TARGET_DOMAIN="${1:-example.com}"
   DNS_SERVER="${2:-8.8.8.8}"
   REPORT_DIR="${DNS_MONITOR_DIR:-/var/log/nadzoring}"
   ALERT_EMAIL="${DNS_ALERT_EMAIL:-}"        # leave empty to disable email alerts
   HEALTH_THRESHOLD=70                       # score below this triggers an alert
   BENCHMARK_QUERIES=5                       # queries per server for each run
   CONNECT_TIMEOUT="${DNS_CONNECT_TIMEOUT:-5}"
   READ_TIMEOUT="${DNS_READ_TIMEOUT:-10}"
   LIFETIME_TIMEOUT="${DNS_LIFETIME_TIMEOUT:-30}"

   # ── Setup ────────────────────────────────────────────────────────────────────
   mkdir -p "$REPORT_DIR"
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   LOG_FILE="$REPORT_DIR/monitor_${TIMESTAMP}.log"
   SUMMARY_FILE="$REPORT_DIR/summary.jsonl"  # append-only JSONL for trend analysis

   log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
   alert() {
       log "ALERT: $*"
       if [[ -n "$ALERT_EMAIL" ]]; then
           echo "$*" | mail -s "[nadzoring] DNS alert: $TARGET_DOMAIN" "$ALERT_EMAIL" || true
       fi
   }

   # ── DNS Health Check ─────────────────────────────────────────────────────────
   log "Starting DNS health check for $TARGET_DOMAIN via $DNS_SERVER"

   HEALTH_JSON="$REPORT_DIR/health_${TIMESTAMP}.json"
   if nadzoring dns health -n "$DNS_SERVER" -o json --quiet \
           --connect-timeout "$CONNECT_TIMEOUT" \
           --read-timeout "$READ_TIMEOUT" \
           --timeout "$LIFETIME_TIMEOUT" \
           --save "$HEALTH_JSON" "$TARGET_DOMAIN"; then
       SCORE=$(python3 -c "import json,sys; d=json.load(open('$HEALTH_JSON')); print(d.get('score',0))" 2>/dev/null || echo 0)
       STATUS=$(python3 -c "import json,sys; d=json.load(open('$HEALTH_JSON')); print(d.get('status','unknown'))" 2>/dev/null || echo unknown)
       log "Health score: $SCORE ($STATUS)"

       if [[ "$SCORE" -lt "$HEALTH_THRESHOLD" ]]; then
           alert "Health score $SCORE is below threshold $HEALTH_THRESHOLD (status: $STATUS) for $TARGET_DOMAIN"
       fi
   else
       alert "dns health check command failed for $TARGET_DOMAIN"
       SCORE=0; STATUS="error"
   fi

   # ── DNS Benchmark ────────────────────────────────────────────────────────────
   BENCH_JSON="$REPORT_DIR/benchmark_${TIMESTAMP}.json"
   if nadzoring dns benchmark -s "$DNS_SERVER" -s 8.8.8.8 -s 1.1.1.1 \
           -d "$TARGET_DOMAIN" -q "$BENCHMARK_QUERIES" \
           --connect-timeout "$CONNECT_TIMEOUT" \
           --read-timeout "$READ_TIMEOUT" \
           --timeout "$LIFETIME_TIMEOUT" \
           -o json --quiet --save "$BENCH_JSON"; then
       AVG_MS=$(python3 -c "
   import json
   data = json.load(open('$BENCH_JSON'))
   target = next((r for r in data if r['server'] == '$DNS_SERVER'), None)
   print(round(target['avg_response_time'], 1) if target else 'N/A')
   " 2>/dev/null || echo "N/A")
       log "Benchmark avg response time for $DNS_SERVER: ${AVG_MS}ms"
   else
       log "WARNING: benchmark failed"
       AVG_MS="N/A"
   fi

   # ── DNS Compare (discrepancy detection) ─────────────────────────────────────
   COMPARE_JSON="$REPORT_DIR/compare_${TIMESTAMP}.json"
   nadzoring dns compare -t A -t MX \
       -s "$DNS_SERVER" -s 8.8.8.8 -s 1.1.1.1 \
       -o json --quiet --save "$COMPARE_JSON" "$TARGET_DOMAIN" || true

   DIFFS=$(python3 -c "
   import json
   data = json.load(open('$COMPARE_JSON'))
   diffs = data.get('differences', [])
   print(len(diffs))
   " 2>/dev/null || echo 0)

   if [[ "$DIFFS" -gt 0 ]]; then
       alert "$DIFFS DNS discrepancies detected for $TARGET_DOMAIN — possible poisoning or misconfiguration"
   fi
   log "DNS compare: $DIFFS discrepancies found"

   # ── Reverse DNS Spot-check ───────────────────────────────────────────────────
   RESOLVED_IP=$(nadzoring network-base host-to-ip --quiet -o json "$TARGET_DOMAIN" 2>/dev/null \
       | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0].get('ip','') if d else '')" 2>/dev/null || echo "")

   REVERSE_HOST="N/A"
   if [[ -n "$RESOLVED_IP" ]]; then
       REVERSE_JSON="$REPORT_DIR/reverse_${TIMESTAMP}.json"
       nadzoring dns reverse -n "$DNS_SERVER" -o json --quiet \
           --connect-timeout "$CONNECT_TIMEOUT" \
           --read-timeout "$READ_TIMEOUT" \
           --save "$REVERSE_JSON" "$RESOLVED_IP" || true
       REVERSE_HOST=$(python3 -c "
   import json
   data = json.load(open('$REVERSE_JSON'))
   print(data[0].get('hostname','N/A') if data else 'N/A')
   " 2>/dev/null || echo "N/A")
       log "Reverse DNS for $RESOLVED_IP → $REVERSE_HOST"
   fi

   # ── Append to JSONL summary for trend analysis ───────────────────────────────
   python3 - <<EOF >> "$SUMMARY_FILE"
   import json, datetime
   print(json.dumps({
       "timestamp": "$TIMESTAMP",
       "domain": "$TARGET_DOMAIN",
       "dns_server": "$DNS_SERVER",
       "health_score": $SCORE,
       "health_status": "$STATUS",
       "avg_response_ms": "$AVG_MS",
       "discrepancies": $DIFFS,
       "resolved_ip": "$RESOLVED_IP",
       "reverse_host": "$REVERSE_HOST",
   }))
   EOF

   log "Run complete. Reports saved to $REPORT_DIR"

**Scheduling with cron (Linux/macOS)**

.. code-block:: bash

   # Edit crontab
   crontab -e

   # Run every 5 minutes
   */5 * * * * /path/to/dns_monitor.sh example.com 8.8.8.8

   # Run every hour with email alerts
   0 * * * * DNS_ALERT_EMAIL=ops@example.com /path/to/dns_monitor.sh example.com 8.8.8.8

   # Run every 15 minutes, logging cron output
   */15 * * * * /path/to/dns_monitor.sh example.com 8.8.8.8 >> /var/log/nadzoring/cron.log 2>&1

**Scheduling with systemd timer (Linux, recommended)**

Create ``/etc/systemd/system/nadzoring-dns-monitor.service``:

.. code-block:: ini

   [Unit]
   Description=Nadzoring DNS health monitor
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=oneshot
   ExecStart=/path/to/dns_monitor.sh example.com 8.8.8.8
   Environment=DNS_MONITOR_DIR=/var/log/nadzoring
   Environment=DNS_ALERT_EMAIL=ops@example.com
   Environment=DNS_CONNECT_TIMEOUT=5
   Environment=DNS_READ_TIMEOUT=10
   Environment=DNS_LIFETIME_TIMEOUT=30
   StandardOutput=journal
   StandardError=journal

Create ``/etc/systemd/system/nadzoring-dns-monitor.timer``:

.. code-block:: ini

   [Unit]
   Description=Run Nadzoring DNS monitor every 5 minutes

   [Timer]
   OnBootSec=60
   OnUnitActiveSec=5min
   Persistent=true

   [Install]
   WantedBy=timers.target

Enable and start:

.. code-block:: bash

   sudo systemctl daemon-reload
   sudo systemctl enable --now nadzoring-dns-monitor.timer
   sudo systemctl status nadzoring-dns-monitor.timer
   journalctl -u nadzoring-dns-monitor.service -f   # follow live logs

**Python continuous monitoring loop (in-process)**

Use ``DNSMonitor`` directly for in-process monitoring with custom alerting:

*Infinite loop (blocks until Ctrl-C or SIGTERM):*

.. code-block:: python

   from nadzoring.dns_lookup.monitor import AlertEvent, DNSMonitor, MonitorConfig
   from nadzoring.utils.timeout import TimeoutConfig

   timeout_config = TimeoutConfig(connect=3.0, read=10.0, lifetime=30.0)


   def send_alert(alert: AlertEvent) -> None:
       print(f"ALERT [{alert.alert_type}]: {alert.message}")


   config = MonitorConfig(
       domain="example.com",
       nameservers=["8.8.8.8", "1.1.1.1"],
       interval=60.0,
       max_response_time_ms=500.0,
       min_success_rate=0.95,
       log_file="dns_monitor.jsonl",
       alert_callback=send_alert,
       timeout_config=timeout_config,
   )

   monitor = DNSMonitor(config)
   monitor.run()
   print(monitor.report())

*Finite cycles (CI pipelines, cron scripts):*

.. code-block:: python

   from nadzoring.dns_lookup.monitor import DNSMonitor, MonitorConfig
   from nadzoring.utils.timeout import TimeoutConfig
   from statistics import mean

   timeout_config = TimeoutConfig(connect=2.0, read=8.0)

   config = MonitorConfig(
       domain="example.com",
       nameservers=["8.8.8.8", "1.1.1.1"],
       interval=10.0,
       run_health_check=False,
       timeout_config=timeout_config,
   )
   monitor = DNSMonitor(config)
   history = monitor.run_cycles(6)

   rts = [s.avg_response_time_ms for c in history for s in c.samples if s.avg_response_time_ms is not None]
   print(f"Mean RT: {mean(rts):.1f}ms")
   print(monitor.report())

*Analyse saved log:*

.. code-block:: python

   from nadzoring.dns_lookup.monitor import load_log
   from statistics import mean

   cycles = load_log("dns_monitor.jsonl")
   rts = [s["avg_response_time_ms"] for c in cycles for s in c["samples"] if s["avg_response_time_ms"] is not None]
   alerts = [a for c in cycles for a in c.get("alerts", [])]
   print(f"Cycles: {len(cycles)}  Mean RT: {mean(rts):.1f}ms  Alerts: {len(alerts)}")

----

Quick Website Block Check
-------------------------

.. code-block:: bash

   nadzoring dns resolve -t ALL example.com
   nadzoring dns reverse 93.184.216.34
   nadzoring dns trace example.com
   nadzoring network-base ping example.com
   nadzoring dns compare example.com
   nadzoring dns poisoning example.com
   nadzoring network-base http-ping https://example.com
   nadzoring network-base traceroute example.com
   nadzoring security check-ssl example.com
   nadzoring security check-headers https://example.com
   nadzoring security check-email example.com
   nadzoring security subdomains example.com
