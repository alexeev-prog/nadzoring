Network Commands
================

The ``network-base`` group provides host reachability checks, HTTP
probing, port scanning, service detection, geolocation, WHOIS,
comprehensive domain information, traceroute, and local network
information commands.

.. code-block:: bash

   nadzoring network-base --help

----

network-base ping
-----------------

Check ICMP reachability for one or more hosts.

.. code-block:: text

   nadzoring network-base ping [OPTIONS] HOST [HOST ...]

.. code-block:: bash

   nadzoring network-base ping 8.8.8.8
   nadzoring network-base ping google.com 1.1.1.1 cloudflare.com
   nadzoring network-base ping -o json https://example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.ping_address import ping_addr

   # Works with IPs, hostnames, and full URLs
   if ping_addr("8.8.8.8"):
       print("Reachable")

   # Note: ICMP may be blocked even for live hosts
   reachable = ping_addr("https://google.com")

----

network-base http-ping
-----------------------

Probe a URL and measure DNS resolution, time-to-first-byte (TTFB), and
total download time.

.. code-block:: text

   nadzoring network-base http-ping [OPTIONS] URL

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Option
     - Default
     - Description
   * - ``--timeout``
     - ``10.0``
     - Request timeout in seconds — sets both connect and read
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds). Falls back to ``--timeout``.
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds). Falls back to ``--timeout``.
   * - ``--no-ssl-verify``
     - off
     - Skip SSL certificate verification
   * - ``--no-redirects``
     - off
     - Do not follow HTTP redirects
   * - ``--show-headers``
     - off
     - Include response headers in output

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring network-base http-ping https://example.com
   nadzoring network-base http-ping --show-headers https://github.com
   nadzoring network-base http-ping --timeout 5 --no-ssl-verify https://self-signed.badssl.com
   nadzoring network-base http-ping --connect-timeout 3 --read-timeout 15 https://slow.example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.http_ping import http_ping
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=2.0, read=10.0, lifetime=30.0)
   result = http_ping("https://example.com", timeout_config=config, include_headers=True)

   if result.error:
       print("Failed:", result.error)
   else:
       print(f"Status:  {result.status_code}")
       print(f"DNS:     {result.dns_ms} ms")
       print(f"TTFB:    {result.ttfb_ms} ms")
       print(f"Total:   {result.total_ms} ms")
       print(f"Size:    {result.content_length} bytes")
       if result.final_url:
           print(f"Redirect→ {result.final_url}")

----

network-base host-to-ip
------------------------

Resolve a hostname to its IPv4 address.

.. code-block:: text

   nadzoring network-base host-to-ip [OPTIONS] HOSTNAME

.. code-block:: bash

   nadzoring network-base host-to-ip example.com
   nadzoring network-base host-to-ip google.com github.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.utils.validators import resolve_hostname

   ip = resolve_hostname("example.com")
   if ip is None:
       print("Resolution failed")
   else:
       print(ip)  # "93.184.216.34"

----

network-base parse-url
-----------------------

Parse a URL into its components (scheme, hostname, port, path, query, fragment, etc.).

.. code-block:: text

   nadzoring network-base parse-url [OPTIONS] URL [URL ...]

.. code-block:: bash

   nadzoring network-base parse-url https://example.com/path?q=1#section
   nadzoring network-base parse-url "postgresql://user:pass@localhost:5432/db"

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.parse_url import parse_url

   result = parse_url("https://user:pass@example.com:8080/path?key=value#frag")
   print(result["protocol"])   # 'https'
   print(result["hostname"])   # 'example.com'
   print(result["port"])       # 8080
   print(result["username"])   # 'user'
   print(result["password"])   # 'pass'
   print(result["path"])       # '/path'
   print(result["query_params"])  # [('key', 'value')]
   print(result["fragment"])   # 'frag'

----

network-base geolocation
------------------------

Get geographic information for a public IP address.

.. code-block:: text

   nadzoring network-base geolocation [OPTIONS] IP [IP ...]

.. code-block:: bash

   nadzoring network-base geolocation 8.8.8.8
   nadzoring network-base geolocation 8.8.8.8 1.1.1.1 -o json

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.geolocation_ip import geo_ip

   result = geo_ip("8.8.8.8")

   if not result:
       print("Geolocation unavailable")
   else:
       print(f"{result['city']}, {result['country']}")
       print(f"Lat/Lon: {result['lat']}, {result['lon']}")

.. note::
   ip-api.com rate-limits free callers to 45 requests per minute.
   Private addresses (e.g. ``192.168.x.x``) return an empty result.

----

network-base whois
------------------

Perform a WHOIS lookup for a domain or IP address.

.. code-block:: text

   nadzoring network-base whois [OPTIONS] TARGET

.. code-block:: bash

   nadzoring network-base whois example.com
   nadzoring network-base whois 8.8.8.8
   nadzoring network-base whois -o json --save whois.json example.com

.. note::
   Requires the ``whois`` system utility.  See :doc:`/installation` for
   installation instructions.

----

network-base domain-info
-------------------------

Retrieve comprehensive information about a domain in a single call.
Aggregates WHOIS registration data, DNS record lookups (A, AAAA, MX, NS,
TXT), IP geolocation for the primary resolved address, and reverse DNS.

.. code-block:: text

   nadzoring network-base domain-info [OPTIONS] DOMAIN [DOMAIN ...]

.. code-block:: bash

   nadzoring network-base domain-info example.com

   # Multiple domains
   nadzoring network-base domain-info google.com github.com cloudflare.com

   # Export as JSON
   nadzoring network-base domain-info -o json --save domain_report.json example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.domain_info import get_domain_info

   info = get_domain_info("example.com")

   # WHOIS registration data
   print(info["whois"]["registrar"])
   print(info["whois"]["creation_date"])
   print(info["whois"]["expiry_date"])

   # Resolved IP addresses
   print(info["dns"]["ipv4"])    # '93.184.216.34'
   print(info["dns"]["ipv6"])    # '2606:2800:220:1:248:1893:25c8:1946'

   # DNS records by type
   for rtype, records in info["dns"]["records"].items():
       print(f"  {rtype}: {records}")

   # Geolocation of the primary IP
   geo = info["geolocation"]
   if geo:
       print(f"{geo['city']}, {geo['country']}  ({geo['lat']}, {geo['lon']})")

   # Reverse DNS for the primary IP
   print(info["reverse_dns"])    # 'example.com' or None

----

network-base port-scan
-----------------------

Scan TCP or UDP ports on one or more targets.

.. code-block:: text

   nadzoring network-base port-scan [OPTIONS] TARGET [TARGET ...]

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``--mode``
     - ``fast``
     - Scan mode: ``fast`` (common ports), ``full`` (1–65535), ``custom``
   * - ``--protocol``
     - ``tcp``
     - Protocol: ``tcp`` or ``udp``
   * - ``--ports``
     - —
     - Custom port list or range (e.g. ``22,80,443`` or ``1-1024``)
   * - ``--timeout``
     - ``2.0``
     - Socket timeout (seconds) — sets connect timeout
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds). Falls back to ``--timeout``.
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds) for banner grabbing
   * - ``--workers``
     - ``50``
     - Number of concurrent threads
   * - ``--no-banner``
     - off
     - Disable banner grabbing
   * - ``--show-closed``
     - off
     - Show closed ports in results

Examples
~~~~~~~~

.. code-block:: bash

   nadzoring network-base port-scan example.com
   nadzoring network-base port-scan --mode full 192.168.1.1
   nadzoring network-base port-scan --mode custom --ports 1-1024 example.com
   nadzoring network-base port-scan --protocol udp --mode fast example.com
   nadzoring network-base port-scan --connect-timeout 1 --read-timeout 3 example.com

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.port_scanner import ScanConfig, scan_ports
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=1.5, read=5.0, lifetime=60.0)
   scan_config = ScanConfig(
       targets=["example.com"],
       mode="fast",
       protocol="tcp",
       timeout_config=config,
   )
   results = scan_ports(scan_config)

   for scan in results:
       print(f"Target: {scan.target}  ({scan.target_ip})")
       print(f"Open ports: {scan.open_ports}")
       for port in scan.open_ports:
           r = scan.results[port]
           print(f"  {port}/tcp  {r.service}  {r.response_time}ms")
           if r.banner:
               print(f"  Banner: {r.banner[:80]}")

----

network-base detect-service
---------------------------

Actively connect to ports on a target host and detect the actual running
services by analyzing banners.

.. code-block:: text

   nadzoring network-base detect-service [OPTIONS] TARGET PORTS...

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``--timeout``
     - ``3.0``
     - Connection timeout (seconds) — sets connect timeout
   * - ``--connect-timeout``
     - ``5.0``
     - Connection timeout (seconds). Falls back to ``--timeout``.
   * - ``--read-timeout``
     - ``10.0``
     - Read timeout (seconds) for banner
   * - ``--no-probe``
     - off
     - Disable sending protocol-specific probes

Examples
~~~~~~~~

.. code-block:: bash

   # Detect services on common ports
   nadzoring network-base detect-service example.com 80 443 22

   # Multiple ports including database
   nadzoring network-base detect-service 192.168.1.100 3306 5432 6379

   # Longer timeout for slow services
   nadzoring network-base detect-service --connect-timeout 5 example.com 8080

   # JSON output for scripting
   nadzoring network-base detect-service -o json example.com 80 443

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.service_detector import detect_service_on_host
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=3.0, read=8.0)
   result = detect_service_on_host("example.com", 80, timeout_config=config)

   if result.detected_service:
       print(f"Service: {result.detected_service} (method: {result.method})")
       print(f"Banner: {result.banner}")
   else:
       print(f"Fallback guess: {result.guessed_service}")
       if result.error:
           print(f"Error: {result.error}")

----

network-base port-service
--------------------------

Identify the service name associated with a port number.

.. code-block:: text

   nadzoring network-base port-service [OPTIONS] PORT [PORT ...]

.. code-block:: bash

   nadzoring network-base port-service 80 443 22 3306

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.service_on_port import get_service_on_port

   print(get_service_on_port(80))    # "http"
   print(get_service_on_port(22))    # "ssh"
   print(get_service_on_port(9999))  # "unknown"

----

network-base traceroute
------------------------

Trace the network path to a target host.

.. code-block:: text

   nadzoring network-base traceroute [OPTIONS] TARGET

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``--max-hops``
     - ``30``
     - Maximum number of hops
   * - ``--timeout``
     - ``2.0``
     - Per-hop timeout (seconds) — sets connect timeout
   * - ``--connect-timeout``
     - ``5.0``
     - Per-hop timeout (seconds). Falls back to ``--timeout``.
   * - ``--sudo``
     - off
     - Prefix command with ``sudo`` (Linux only)

.. code-block:: bash

   nadzoring network-base traceroute 8.8.8.8
   nadzoring network-base traceroute --max-hops 20 --sudo example.com

.. note::
   On Linux, ``traceroute`` requires raw-socket privileges.  Use
   ``--sudo``, run as root, or grant the capability to the binary.
   ``tracepath`` is tried automatically as a fallback.

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.network_base.traceroute import traceroute
   from nadzoring.utils.timeout import TimeoutConfig

   config = TimeoutConfig(connect=1.5, read=5.0)
   hops = traceroute("8.8.8.8", max_hops=15, per_hop_timeout=config.connect)
   for hop in hops:
       rtts = [f"{r}ms" if r else "*" for r in hop.rtt_ms]
       print(f"{hop.hop:2}  {hop.ip or '*':16}  {' '.join(rtts)}")

----

network-base connections
------------------------

List active TCP/UDP connections (like ``netstat`` / ``ss``).

.. code-block:: text

   nadzoring network-base connections [OPTIONS]

.. code-block:: bash

   nadzoring network-base connections
   nadzoring network-base connections --protocol tcp --state LISTEN
   nadzoring network-base connections -o json --save conns.json

----

network-base route
------------------

Display the system IP routing table.

.. code-block:: text

   nadzoring network-base route [OPTIONS]

.. code-block:: bash

   nadzoring network-base route
   nadzoring network-base route -o json

----

network-base params
--------------------

Show local network interface parameters: interface name, IPv4/IPv6, MAC
address, gateway, and public IP.

.. code-block:: text

   nadzoring network-base params [OPTIONS]

.. code-block:: bash

   nadzoring network-base params
   nadzoring network-base params -o json --save net.json
