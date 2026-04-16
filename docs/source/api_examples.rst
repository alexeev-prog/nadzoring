===========
Python API Examples
===========

This page provides practical Python API examples for all Nadzoring modules.

----

DNS Lookup API
--------------

.. code-block:: python

   from nadzoring.dns_lookup.utils import resolve_with_timer, get_public_dns_servers
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=8.0)

   # Resolve any record type
   result = resolve_with_timer("example.com", "MX", include_ttl=True, timeout_config=config)
   if result["error"]:
       print("Error:", result["error"])
   else:
       print(result["records"])  # ['10 mail.example.com']
       print(result["ttl"])  # 3600
       print(result["response_time"])  # 45.2

   # List built-in public servers
   servers = get_public_dns_servers()  # ['8.8.8.8', '1.1.1.1', ...]

----

Reverse DNS API
---------------

.. code-block:: python

   from nadzoring.dns_lookup.reverse import reverse_dns
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=5.0)

   # Standard reverse lookup
   result = reverse_dns("8.8.8.8", timeout_config=config)
   if result["error"]:
       # Possible values: 'No PTR record', 'No reverse DNS',
       # 'Query timeout', 'Invalid IP address: ...'
       print("Failed:", result["error"])
   else:
       print(result["hostname"])  # 'dns.google'

   # With a custom nameserver
   result = reverse_dns("1.1.1.1", nameserver="8.8.8.8")
   print(result["hostname"])  # 'one.one.one.one'

   # Compact error-safe pattern
   hostname = result["hostname"] or f"[{result['error']}]"

----

Network Base API
----------------

.. code-block:: python

   from nadzoring.network_base.ping_address import ping_addr
   from nadzoring.network_base.http_ping import http_ping
   from nadzoring.network_base.geolocation_ip import geo_ip
   from nadzoring.network_base.traceroute import traceroute
   from nadzoring.network_base.connections import get_connections
   from nadzoring.network_base.route_table import get_route_table
   from nadzoring.network_base.network_params import network_param
   from nadzoring.network_base.whois_lookup import whois_lookup
   from nadzoring.network_base.domain_info import get_domain_info
   from nadzoring.network_base.port_scanner import ScanConfig, scan_ports
   from nadzoring.network_base.service_detector import detect_service_on_host
   from nadzoring.network_base.parse_url import parse_url
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=8.0, lifetime=30.0)

   # Ping — returns bool
   alive = ping_addr("8.8.8.8")

   # HTTP probe — check .error before reading timing fields
   r = http_ping("https://example.com", timeout_config=config)
   if not r.error:
       print(r.ttfb_ms, r.status_code)

   # URL parsing
   parsed = parse_url("https://example.com/path?q=1")
   print(parsed["hostname"], parsed["path"])

   # Geolocation — returns {} on failure
   loc = geo_ip("8.8.8.8")
   if loc:
       print(loc["country"], loc["city"])

   # Comprehensive domain info — WHOIS + DNS + geo + reverse DNS
   info = get_domain_info("example.com")
   print(info["whois"]["registrar"])
   print(info["dns"]["ipv4"])
   print(info["geolocation"]["country"])
   print(info["reverse_dns"])

   # Traceroute
   for hop in traceroute("8.8.8.8", max_hops=10, per_hop_timeout=config.connect):
       print(hop.hop, hop.ip, hop.rtt_ms)

   # Active connections
   for conn in get_connections(protocol="tcp", state_filter="ESTABLISHED"):
       print(conn.local_address, "->", conn.remote_address)

   # Port scan
   scan_config = ScanConfig(targets=["example.com"], mode="fast", timeout_config=config)
   for result in scan_ports(scan_config):
       print("Open ports:", result.open_ports)

   # Service detection on a specific port
   service = detect_service_on_host("example.com", 80, timeout_config=config)
   print(service.detected_service or service.guessed_service)

----

Security API
------------

.. code-block:: python

   from nadzoring.security.check_website_ssl_cert import (
       check_ssl_certificate,
       check_ssl_expiry,
       check_ssl_expiry_with_fallback,
   )
   from nadzoring.security.http_headers import check_http_security_headers
   from nadzoring.security.email_security import check_email_security
   from nadzoring.security.subdomain_scan import scan_subdomains
   from nadzoring.security.ssl_monitor import SSLMonitor
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=10.0)

   # SSL/TLS certificate check
   result = check_ssl_certificate("example.com", days_before=14, timeout_config=config)
   print(result["status"], result["remaining_days"])
   print(result["protocols"]["supported"])  # ['TLSv1.2', 'TLSv1.3']
   print(result["public_key"]["strength"])  # 'good'

   # Fallback mode for self-signed / problematic certs
   result = check_ssl_expiry_with_fallback("self-signed.example.com")

   # HTTP security header audit
   headers = check_http_security_headers("https://example.com", timeout_config=config)
   print(headers["score"])  # 0–100
   print(headers["missing"])  # list of absent recommended headers
   print(headers["leaking"])  # {'Server': 'nginx/1.18.0'}

   # Email security (SPF / DKIM / DMARC)
   email = check_email_security("example.com")
   print(email["overall_score"])  # 0–3
   print(email["spf"]["all_qualifier"])  # '~' (softfail)
   print(email["dmarc"]["policy"])  # 'reject'
   print(email["all_issues"])  # aggregated issue list

   # Subdomain discovery
   subdomains = scan_subdomains(
       "example.com",
       max_threads=30,
       timeout_config=config,
   )
   for s in subdomains:
       print(s["subdomain"], s["ip"], s["source"])

   # Continuous SSL monitoring
   monitor = SSLMonitor(["example.com", "github.com"], interval=3600, days_before=14, timeout_config=config)
   monitor.set_alert_callback(lambda domain, msg: print(f"ALERT {domain}: {msg}"))
   results = monitor.run_cycles(cycles=3)
   for r in monitor.history():
       print(r["domain"], r["status"], r["remaining_days"])

----

ARP API
-------

.. code-block:: python

   from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError
   from nadzoring.arp.detector import ARPSpoofingDetector
   from nadzoring.arp.realtime import ARPRealtimeDetector
   from nadzoring.utils.timeout import TimeoutConfig

   # ARP cache — raises ARPCacheRetrievalError on system failure
   try:
       cache = ARPCache()
       for entry in cache.get_cache():
           print(entry.ip_address, entry.mac_address, entry.state.value)
   except ARPCacheRetrievalError as exc:
       print("ARP cache unavailable:", exc)

   # Static spoofing detection
   detector = ARPSpoofingDetector(cache)
   for alert in detector.detect():
       print(alert.alert_type, alert.description)

   # Real-time monitoring with timeouts
   config = TimeoutConfig(connect=2.0, read=8.0, lifetime=45.0)
   rt = ARPRealtimeDetector()
   alerts = rt.monitor(interface="eth0", count=50, timeout_config=config)
   print(rt.get_stats())
