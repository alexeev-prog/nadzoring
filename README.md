# Nadzoring

<a id="readme-top"></a>

<div align="center">
  <p align="center">
    An open source tool for detecting website blocks, downdetecting and network analysis
    <br />
    <a href="https://alexeev-prog.github.io/nadzoring/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#-getting-started">Getting Started</a>
    ·
    <a href="#-usage-examples">Basic Usage</a>
    ·
    <a href="https://alexeev-prog.github.io/nadzoring/v0.1.5">Stable Documentation</a>
    ·
    <a href="https://alexeev-prog.github.io/nadzoring/main">Latest Documentation</a>
    ·
    <a href="https://github.com/alexeev-prog/nadzoring/blob/main/LICENSE">License</a>
  </p>
</div>
<br>
<p align="center">
    <img src="https://img.shields.io/github/languages/top/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/github/languages/count/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/github/license/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/github/stars/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/github/issues/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/github/last-commit/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/pypi/wheel/nadzoring?style=for-the-badge">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/nadzoring?style=for-the-badge">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/nadzoring?style=for-the-badge">
    <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/alexeev-prog/nadzoring?style=for-the-badge">
</p>
<p align="center">
    <img src="https://raw.githubusercontent.com/alexeev-prog/nadzoring/refs/heads/main/docs/pallet-0.png">
</p>

Nadzoring (from Russian "надзор" — supervision/oversight + English "-ing" suffix) is a free and open-source command-line tool for detecting website blocks, monitoring service availability, and network analysis. It helps you investigate network connectivity issues, check if websites are accessible, analyze network configurations with comprehensive DNS diagnostics — including reverse DNS, DNS poisoning detection, ARP spoofing monitoring, and much more.

## Table of Contents

- [Nadzoring](#nadzoring)
  - [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
    - [Global Options](#global-options)
    - [DNS Commands](#dns-commands)
      - [dns resolve](#dns-resolve)
      - [dns reverse](#dns-reverse)
      - [dns check](#dns-check)
      - [dns trace](#dns-trace)
      - [dns compare](#dns-compare)
      - [dns health](#dns-health)
      - [dns benchmark](#dns-benchmark)
      - [dns poisoning](#dns-poisoning)
    - [Network Base Commands](#network-base-commands)
      - [ping](#ping)
      - [http-ping](#http-ping)
      - [host-to-ip](#host-to-ip)
      - [geolocation](#geolocation)
      - [params](#params)
      - [port-scan](#port-scan)
      - [port-service](#port-service)
      - [whois](#whois)
      - [connections](#connections)
      - [traceroute](#traceroute)
      - [route](#route)
    - [ARP Commands](#arp-commands)
      - [arp cache](#arp-cache)
      - [arp detect-spoofing](#arp-detect-spoofing)
      - [arp monitor-spoofing](#arp-monitor-spoofing)
  - [Output Formats](#output-formats)
  - [Saving Results](#saving-results)
  - [Logging Levels](#logging-levels)
  - [Python API](#python-api)
    - [DNS Lookup API](#dns-lookup-api)
    - [Reverse DNS API](#reverse-dns-api)
    - [Network Base API](#network-base-api)
    - [ARP API](#arp-api)
  - [Examples](#examples)
    - [DNS Diagnostics](#dns-diagnostics)
    - [Reverse DNS Batch Lookup](#reverse-dns-batch-lookup)
    - [DNS Poisoning Detection](#dns-poisoning-detection)
    - [DNS Performance Benchmarking](#dns-performance-benchmarking)
    - [Port Scanning](#port-scanning)
    - [HTTP Service Probing](#http-service-probing)
    - [ARP Spoofing Detection](#arp-spoofing-detection)
    - [Network Path Analysis](#network-path-analysis)
    - [Complete Network Diagnostics](#complete-network-diagnostics)
    - [Automated DNS Server Monitoring](#automated-dns-server-monitoring)
      - [Shell script with alerting thresholds](#shell-script-with-alerting-thresholds)
      - [Scheduling with cron (Linux/macOS)](#scheduling-with-cron-linuxmacos)
      - [Scheduling with systemd timer (Linux, recommended)](#scheduling-with-systemd-timer-linux-recommended)
      - [Python continuous monitoring loop (in-process)](#python-continuous-monitoring-loop-in-process)
    - [Quick Website Block Check](#quick-website-block-check)
  - [Contributing](#contributing)
  - [Documentation](#documentation)
  - [License \& Support](#license--support)

---

# Getting Started

### Prerequisites

- Python 3.12+
- pip

Optional system utilities:

| Utility | Required by |
|---------|-------------|
| `traceroute` / `tracepath` | `network-base traceroute` (Linux) |
| `whois` | `network-base whois` |
| `ip` / `route` | `network-base params`, `network-base route` |
| `net-tools` | `network-base params` on some Linux distros (`sudo apt install net-tools`) |
| `ss` | `network-base connections` (Linux) |

### Installation

```bash
pip install nadzoring
```

Verify:

```bash
nadzoring --help
```

**Development version:**

```bash
pip install git+https://github.com/alexeev-prog/nadzoring.git
```

---

## Usage

Nadzoring uses a hierarchical command structure: `nadzoring <group> <command> [OPTIONS]`.
The three main groups are `dns`, `network-base`, and `arp`.

### Global Options

These options work with every command:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | | Enable debug output with execution timing | `False` |
| `--quiet` | | Suppress non-error output | `False` |
| `--no-color` | | Disable colored output | `False` |
| `--output` | `-o` | Output format: `table`, `json`, `csv`, `html`, `html_table` | `table` |
| `--save` | | Save results to file | None |

---

### DNS Commands

#### dns resolve

Resolve DNS records for one or more domains.

```bash
nadzoring dns resolve [OPTIONS] DOMAINS...
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--type` | `-t` | Record type: A, AAAA, CNAME, MX, NS, TXT, ALL | `A` |
| `--nameserver` | `-n` | Nameserver IP to use | System default |
| `--short` | | Compact output | `False` |
| `--show-ttl` | | Show TTL value | `False` |
| `--format-style` | | Output style: standard, bind, host, dig | `standard` |

```bash
# A record lookup
nadzoring dns resolve google.com

# Multiple record types
nadzoring dns resolve -t MX -t TXT -t A example.com

# All record types with a specific nameserver
nadzoring dns resolve -t ALL -n 8.8.8.8 github.com

# Show TTL values
nadzoring dns resolve --show-ttl --type A cloudflare.com
```

**Python API:**

```python
from nadzoring.dns_lookup.utils import resolve_with_timer

result = resolve_with_timer("example.com", "A")
if not result["error"]:
    print(result["records"])       # ['93.184.216.34']
    print(result["response_time"]) # milliseconds

# With TTL
result = resolve_with_timer("example.com", "MX", include_ttl=True)
print(result["ttl"])  # e.g. 3600
```

---

#### dns reverse

Perform reverse DNS lookups (PTR records) to find the hostname for an IP address.

```bash
nadzoring dns reverse [OPTIONS] IP_ADDRESSES...
```

| Option | Short | Description |
|--------|-------|-------------|
| `--nameserver` | `-n` | Nameserver IP to use |

```bash
# Single IP
nadzoring dns reverse 8.8.8.8

# Multiple IPs
nadzoring dns reverse 1.1.1.1 8.8.8.8 9.9.9.9

# Use a specific nameserver
nadzoring dns reverse -n 208.67.222.222 8.8.4.4

# Save as JSON
nadzoring dns reverse -o json --save reverse_lookup.json 8.8.8.8 1.1.1.1
```

**Python API:**

```python
from nadzoring.dns_lookup.reverse import reverse_dns

# IPv4 reverse lookup
result = reverse_dns("8.8.8.8")
print(result["hostname"])       # 'dns.google'
print(result["response_time"])  # milliseconds
print(result["error"])          # None on success

# IPv6 reverse lookup
result = reverse_dns("2001:4860:4860::8888")
print(result["hostname"])  # 'dns.google'

# Handle lookup failure
result = reverse_dns("192.168.1.1")
if result["error"]:
    print(result["error"])  # 'No PTR record' or 'No reverse DNS'

# Custom nameserver
result = reverse_dns("8.8.8.8", nameserver="1.1.1.1")
print(result["hostname"])
```

---

#### dns check

Perform a comprehensive DNS check including MX priority validation and SPF/DKIM analysis.

```bash
nadzoring dns check [OPTIONS] DOMAINS...
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--nameserver` | `-n` | Nameserver IP | System default |
| `--types` | `-t` | Record types to check | ALL |

```bash
# Full DNS check
nadzoring dns check example.com

# Check MX and TXT only
nadzoring dns check -t MX -t TXT gmail.com

# Multiple domains
nadzoring dns check -n 9.9.9.9 google.com cloudflare.com
```

**Python API:**

```python
from nadzoring.dns_lookup.health import check_dns

result = check_dns(
    "example.com",
    record_types=["MX", "TXT"],
    validate_mx=True,
    validate_txt=True,
)
print(result["records"])      # {'MX': ['10 mail.example.com']}
print(result["errors"])       # {'AAAA': 'No AAAA records'} if any
print(result["response_times"]) # per-type timing in ms
print(result["validations"])  # {'mx': {'valid': True, 'issues': []}}
```

---

#### dns trace

Trace the complete DNS resolution delegation chain from root to authoritative nameserver.

```bash
nadzoring dns trace [OPTIONS] DOMAIN
```

| Option | Short | Description |
|--------|-------|-------------|
| `--nameserver` | `-n` | Starting nameserver (default: root `198.41.0.4`) |

```bash
# Trace from root servers
nadzoring dns trace example.com

# Start trace from a specific nameserver
nadzoring dns trace -n 8.8.8.8 google.com

# Verbose with timing
nadzoring dns trace -v github.com
```

**Python API:**

```python
from nadzoring.dns_lookup.trace import trace_dns

result = trace_dns("example.com")
for hop in result["hops"]:
    print(f"Hop: {hop['nameserver']}  time: {hop['response_time']}ms")
    if hop.get("records"):
        print(f"  Records: {hop['records']}")
    if hop.get("error"):
        print(f"  Error: {hop['error']}")

print("Final answer:", result["final_answer"])
```

---

#### dns compare

Compare DNS responses from multiple servers and detect discrepancies.

```bash
nadzoring dns compare [OPTIONS] DOMAIN
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--servers` | `-s` | DNS servers to compare | `8.8.8.8`, `1.1.1.1`, `9.9.9.9` |
| `--type` | `-t` | Record types to compare | `A` |

```bash
# Compare A records across default servers
nadzoring dns compare example.com

# Compare MX records with custom servers
nadzoring dns compare -t MX -s 8.8.8.8 -s 208.67.222.222 -s 9.9.9.9 gmail.com

# Multiple record types
nadzoring dns compare -t A -t AAAA -t NS cloudflare.com
```

**Python API:**

```python
from nadzoring.dns_lookup.compare import compare_dns_servers

result = compare_dns_servers(
    "example.com",
    servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
    record_types=["A", "MX"],
)
if result["differences"]:
    for diff in result["differences"]:
        print(f"Server {diff['server']} — {diff['type']} mismatch")
        print(f"  Expected: {diff['expected']}")
        print(f"  Got:      {diff['got']}")
else:
    print("All servers agree.")
```

---

#### dns health

Perform a scored DNS health check across all standard record types.

```bash
nadzoring dns health [OPTIONS] DOMAIN
```

| Option | Short | Description |
|--------|-------|-------------|
| `--nameserver` | `-n` | Nameserver IP |

Health score: **80–100** = Healthy · **50–79** = Degraded · **0–49** = Unhealthy

```bash
nadzoring dns health example.com
nadzoring dns health -n 1.1.1.1 google.com
```

**Python API:**

```python
from nadzoring.dns_lookup.health import health_check_dns

result = health_check_dns("example.com")
print(result["score"])   # 0–100
print(result["status"])  # 'healthy' | 'degraded' | 'unhealthy'
print(result["issues"])  # critical problems
print(result["warnings"]) # non-critical issues
for rtype, score in result["record_scores"].items():
    print(f"  {rtype}: {score}")
```

---

#### dns benchmark

Benchmark DNS server response times across multiple servers.

```bash
nadzoring dns benchmark [OPTIONS]
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--domain` | `-d` | Domain to query | `google.com` |
| `--servers` | `-s` | Servers to benchmark | All public servers |
| `--type` | `-t` | Record type | `A` |
| `--queries` | `-q` | Queries per server | `10` |
| `--parallel/--sequential` | | Run concurrently or one by one | `parallel` |

```bash
nadzoring dns benchmark
nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 9.9.9.9 --queries 20
nadzoring dns benchmark -t MX -d gmail.com --sequential
nadzoring dns benchmark -o json --save benchmark.json
```

**Python API:**

```python
from nadzoring.dns_lookup.benchmark import benchmark_dns_servers, benchmark_single_server

# Single server
result = benchmark_single_server("8.8.8.8", queries=10)
print(f"avg={result['avg_response_time']:.1f}ms  success={result['success_rate']}%")

# Multiple servers — returned sorted fastest-first
results = benchmark_dns_servers(
    servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
    queries=10,
    parallel=True,
)
fastest = results[0]
print(f"Fastest: {fastest['server']} at {fastest['avg_response_time']:.1f}ms")
```

---

#### dns poisoning

Detect DNS poisoning, censorship, or unusual CDN routing for a domain.

```bash
nadzoring dns poisoning [OPTIONS] DOMAIN
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--control-server` | `-c` | Trusted control resolver | `8.8.8.8` |
| `--test-servers` | `-t` | Servers to test against control | All public servers |
| `--type` | `-T` | Record type | `A` |
| `--additional-types` | `-a` | Extra record types from control server | None |

Severity levels: `NONE` → `LOW` → `MEDIUM` → `HIGH` → `CRITICAL` / `SUSPICIOUS`

```bash
nadzoring dns poisoning example.com
nadzoring dns poisoning -c 1.1.1.1 -a MX -a TXT google.com
nadzoring dns poisoning -o html --save poisoning_report.html twitter.com
```

---

### Network Base Commands

#### ping

Check reachability using ICMP ping.

```bash
nadzoring network-base ping ADDRESSES...
```

```bash
nadzoring network-base ping 8.8.8.8
nadzoring network-base ping google.com cloudflare.com 1.1.1.1
nadzoring network-base ping -o json github.com
```

**Python API:**

```python
from nadzoring.network_base.ping_address import ping_addr

print(ping_addr("8.8.8.8"))            # True
print(ping_addr("https://google.com")) # True — URLs are normalised automatically
print(ping_addr("192.0.2.1"))          # False — unreachable
```

---

#### http-ping

Measure HTTP/HTTPS response timing and inspect headers.

```bash
nadzoring network-base http-ping [OPTIONS] URLS...
```

| Option | Description | Default |
|--------|-------------|---------|
| `--timeout` | Request timeout (seconds) | `10.0` |
| `--no-ssl-verify` | Disable SSL certificate check | `False` |
| `--no-redirects` | Do not follow redirects | `False` |
| `--show-headers` | Include response headers | `False` |

Output includes: DNS time, TTFB, total download time, status code, content size, redirects.

```bash
nadzoring network-base http-ping https://example.com
nadzoring network-base http-ping --show-headers https://github.com https://google.com
nadzoring network-base http-ping --timeout 5 --no-ssl-verify https://self-signed.badssl.com
nadzoring network-base http-ping -o csv --save http_metrics.csv https://api.github.com
```

**Python API:**

```python
from nadzoring.network_base.http_ping import http_ping

result = http_ping("https://example.com", timeout=10.0, include_headers=True)
print(result.status_code)    # 200
print(result.dns_ms)         # DNS resolution time in ms
print(result.ttfb_ms)        # time-to-first-byte in ms
print(result.total_ms)       # total download time in ms
print(result.content_length) # bytes
if result.error:
    print("Error:", result.error)
```

---

#### host-to-ip

Resolve hostnames to IP addresses with IPv4/IPv6 availability checks.

```bash
nadzoring network-base host-to-ip HOSTNAMES...
```

```bash
nadzoring network-base host-to-ip google.com github.com cloudflare.com
nadzoring network-base host-to-ip -o csv --save resolutions.csv example.com
```

**Python API:**

```python
from nadzoring.network_base.router_ip import check_ipv4, check_ipv6

ipv4 = check_ipv4("google.com")  # '142.250.x.x'
ipv6 = check_ipv6("google.com")  # '2607:f8b0:...' or hostname unchanged on failure

# Get router/gateway IP
from nadzoring.network_base.router_ip import router_ip
gateway = router_ip()        # '192.168.1.1' on most home networks
gateway6 = router_ip(ipv6=True)
```

---

#### geolocation

Get geographic location for IP addresses.

```bash
nadzoring network-base geolocation IPS...
```

Output: latitude, longitude, country, city.

```bash
nadzoring network-base geolocation 8.8.8.8 1.1.1.1
nadzoring network-base geolocation --save locations.json 8.8.8.8
```

**Python API:**

```python
from nadzoring.network_base.geolocation_ip import geo_ip

result = geo_ip("8.8.8.8")
print(result["country"])  # 'United States'
print(result["city"])     # 'Mountain View'
print(result["lat"])      # '37.386'
print(result["lon"])      # '-122.0838'
```

---

#### params

Show local network interface configuration.

```bash
nadzoring network-base params [OPTIONS]
```

Output: interface name, IPv4, IPv6, gateway IP, MAC address, public IP.

```bash
nadzoring network-base params
nadzoring network-base params -o json --save net_params.json
```

**Python API:**

```python
from nadzoring.network_base.network_params import network_param

info = network_param()
print(info["IPv4 address"])        # '192.168.1.42'
print(info["Router ip-address"])   # '192.168.1.1'
print(info["MAC-address"])         # '00:11:22:33:44:55'
print(info["Public IP address"])   # your external IP
```

---

#### port-scan

Scan for open TCP/UDP ports on one or more targets.

```bash
nadzoring network-base port-scan [OPTIONS] TARGETS...
```

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | `fast`, `full`, or `custom` | `fast` |
| `--ports` | Port list or range, e.g. `22,80,443` or `1-1024` | None |
| `--protocol` | `tcp` or `udp` | `tcp` |
| `--timeout` | Socket timeout (seconds) | `2.0` |
| `--workers` | Concurrent workers | `50` |
| `--no-banner` | Disable banner grabbing | `False` |
| `--show-closed` | Show closed ports | `False` |

Scan modes: **fast** = common ports · **full** = all 1–65535 · **custom** = your list or range.

```bash
nadzoring network-base port-scan example.com
nadzoring network-base port-scan --mode full 192.168.1.1
nadzoring network-base port-scan --mode custom --ports 22,80,443,8080 example.com
nadzoring network-base port-scan --protocol udp --mode fast example.com
nadzoring network-base port-scan -o json --save scan.json example.com
```

---

#### port-service

Identify the service typically running on a port number.

```bash
nadzoring network-base port-service PORTS...
```

```bash
nadzoring network-base port-service 80 443 22 53 3306
nadzoring network-base port-service -o json 8080 5432 27017
```

**Python API:**

```python
from nadzoring.network_base.service_on_port import get_service_on_port

print(get_service_on_port(80))    # 'http'
print(get_service_on_port(443))   # 'https'
print(get_service_on_port(22))    # 'ssh'
print(get_service_on_port(9999))  # 'unknown'
```

---

#### whois

Look up WHOIS registration data for domains or IP addresses.

> **Requires** the system `whois` utility:
> - Debian/Ubuntu: `sudo apt install whois`
> - macOS: `brew install whois`
> - RHEL/Fedora: `sudo dnf install whois`

```bash
nadzoring network-base whois [OPTIONS] TARGETS...
```

```bash
nadzoring network-base whois example.com
nadzoring network-base whois google.com cloudflare.com 8.8.8.8
nadzoring network-base whois -o json --save whois_data.json github.com
```

**Python API:**

```python
from nadzoring.network_base.whois_lookup import whois_lookup

result = whois_lookup("example.com")
print(result["registrar"])      # 'RESERVED-Internet Assigned Numbers Authority'
print(result["creation_date"])  # '1995-08-14T04:00:00Z'
print(result["expiry_date"])
print(result["name_servers"])
if result.get("error"):
    print("Error:", result["error"])  # whois not installed, etc.
```

---

#### connections

List active TCP/UDP network connections.

```bash
nadzoring network-base connections [OPTIONS]
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--protocol` | `-p` | Filter: `tcp`, `udp`, `all` | `all` |
| `--state` | `-s` | State filter substring, e.g. `LISTEN` | None |
| `--no-process` | | Skip PID/process info | `False` |

```bash
nadzoring network-base connections
nadzoring network-base connections --protocol tcp --state LISTEN
nadzoring network-base connections --protocol udp --no-process
nadzoring network-base connections -o csv --save connections.csv
```

**Python API:**

```python
from nadzoring.network_base.connections import get_connections

# All connections
connections = get_connections()

# Listening TCP sockets only
listening = get_connections(protocol="tcp", state_filter="LISTEN")
for conn in listening:
    print(conn.protocol, conn.local_address, conn.state, conn.process)
```

---

#### traceroute

Trace the network path to a host.

```bash
nadzoring network-base traceroute [OPTIONS] TARGETS...
```

| Option | Description | Default |
|--------|-------------|---------|
| `--max-hops` | Maximum hops | `30` |
| `--timeout` | Per-hop timeout (seconds) | `2.0` |
| `--sudo` | Run with sudo (Linux) | `False` |

> **Linux privilege note:** `traceroute` needs raw-socket access.
> Either use `--sudo`, run as root, or: `sudo setcap cap_net_raw+ep $(which traceroute)`
> Nadzoring automatically falls back to `tracepath` (no root required) if traceroute fails.

```bash
nadzoring network-base traceroute google.com
nadzoring network-base traceroute --max-hops 20 github.com cloudflare.com
nadzoring network-base traceroute --sudo example.com
nadzoring network-base traceroute -o html --save trace.html 8.8.8.8
```

**Python API:**

```python
from nadzoring.network_base.traceroute import traceroute

hops = traceroute("8.8.8.8", max_hops=15)
for hop in hops:
    rtts = [f"{r}ms" if r else "*" for r in hop.rtt_ms]
    print(f"{hop.hop:2}  {hop.ip or '*':16}  {' '.join(rtts)}")
```

---

#### route

Display the system IP routing table.

```bash
nadzoring network-base route [OPTIONS]
```

```bash
nadzoring network-base route
nadzoring network-base route -o json
nadzoring network-base route --save routing_table.json
```

**Python API:**

```python
from nadzoring.network_base.route_table import get_route_table

routes = get_route_table()
for route in routes:
    print(route.destination, "via", route.gateway, "dev", route.interface)
```

---

### ARP Commands

#### arp cache

Show the current ARP cache table (IP-to-MAC mappings).

```bash
nadzoring arp cache [OPTIONS]
```

```bash
nadzoring arp cache
nadzoring arp cache -o csv --save arp_cache.csv
nadzoring arp cache -o json
```

**Python API:**

```python
from nadzoring.arp.cache import ARPCache

cache = ARPCache()
entries = cache.get_cache()
for entry in entries:
    print(f"{entry.ip_address} -> {entry.mac_address}  [{entry.interface}]  {entry.state.value}")
```

---

#### arp detect-spoofing

Statically detect ARP spoofing by analysing the current ARP cache.

```bash
nadzoring arp detect-spoofing [OPTIONS] [INTERFACES]...
```

Detects: duplicate MAC across IPs (`duplicate_mac`) and duplicate IP with multiple MACs (`duplicate_ip`).

```bash
nadzoring arp detect-spoofing
nadzoring arp detect-spoofing eth0 wlan0
nadzoring arp detect-spoofing -o json --save spoofing_alerts.json
```

**Python API:**

```python
from nadzoring.arp.cache import ARPCache
from nadzoring.arp.detector import ARPSpoofingDetector

cache = ARPCache()
detector = ARPSpoofingDetector(cache)
alerts = detector.detect()
for alert in alerts:
    print(f"[{alert.alert_type}] {alert.description}")
```

---

#### arp monitor-spoofing

Monitor live network traffic for ARP spoofing in real time (requires root/admin).

```bash
nadzoring arp monitor-spoofing [OPTIONS]
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--interface` | `-i` | Interface to monitor | All |
| `--count` | `-c` | Packets to capture | `10` |
| `--timeout` | `-t` | Capture timeout (seconds) | `30` |

```bash
nadzoring arp monitor-spoofing
nadzoring arp monitor-spoofing --interface eth0 --count 200 --timeout 60
nadzoring arp monitor-spoofing -o json --save arp_alerts.json
```

**Python API:**

```python
from nadzoring.arp.realtime import ARPRealtimeDetector

detector = ARPRealtimeDetector()
alerts = detector.monitor(interface="eth0", count=100, timeout=30)
for alert in alerts:
    print(f"{alert['timestamp']}  {alert['message']}")
    print(f"  src_ip={alert['src_ip']}  src_mac={alert['src_mac']}")

# Get monitoring stats
stats = detector.get_stats()
print(f"Processed: {stats['packets_processed']}  Alerts: {stats['alerts_generated']}")
```

---

## Output Formats

Use `-o` / `--output` to change the output format:

| Format | Description |
|--------|-------------|
| `table` | Rich terminal table (default) |
| `json` | JSON array, suitable for scripting |
| `csv` | Comma-separated values |
| `html` | Complete HTML page with CSS |
| `html_table` | HTML table fragment only |

```bash
nadzoring dns resolve -o json example.com
nadzoring dns health -o html --save health.html example.com
nadzoring network-base connections -o csv --save conns.csv
```

## Saving Results

```bash
nadzoring dns check -o html --save dns_report.html example.com
nadzoring dns compare -o csv --save comparison.csv google.com
nadzoring dns poisoning -o json --save poisoning.json example.com
nadzoring network-base port-scan -o json --save scan.json example.com
nadzoring arp cache -o csv --save arp.csv
```

## Logging Levels

| Mode | Flag | Behaviour |
|------|------|-----------|
| Normal | (none) | Warnings + progress bars |
| Verbose | `--verbose` | Debug logs + execution timing |
| Quiet | `--quiet` | Results only — ideal for scripting |

---

## Python API

Nadzoring can be used as a Python library — all functionality is accessible programmatically without invoking the CLI.

### DNS Lookup API

```python
from nadzoring.dns_lookup.utils import resolve_with_timer, get_public_dns_servers

# Resolve any record type
result = resolve_with_timer("example.com", "MX", include_ttl=True)
print(result["records"])       # ['10 mail.example.com']
print(result["ttl"])           # 3600
print(result["response_time"]) # 45.2

# List built-in public servers
servers = get_public_dns_servers()  # ['8.8.8.8', '1.1.1.1', ...]
```

### Reverse DNS API

```python
from nadzoring.dns_lookup.reverse import reverse_dns

# Standard reverse lookup
result = reverse_dns("8.8.8.8")
print(result["hostname"])  # 'dns.google'

# With a custom nameserver
result = reverse_dns("1.1.1.1", nameserver="8.8.8.8")
print(result["hostname"])  # 'one.one.one.one'

# Error handling
result = reverse_dns("192.168.0.1")
if result["error"]:
    # possible values: 'No PTR record', 'No reverse DNS',
    # 'Query timeout', 'Invalid IP address: ...'
    print(result["error"])
```

### Network Base API

```python
from nadzoring.network_base.ping_address import ping_addr
from nadzoring.network_base.http_ping import http_ping
from nadzoring.network_base.geolocation_ip import geo_ip
from nadzoring.network_base.traceroute import traceroute
from nadzoring.network_base.connections import get_connections
from nadzoring.network_base.route_table import get_route_table
from nadzoring.network_base.network_params import network_param
from nadzoring.network_base.whois_lookup import whois_lookup
from nadzoring.network_base.port_scanner import ScanConfig, scan_ports

# Ping
alive = ping_addr("8.8.8.8")  # bool

# HTTP probe
r = http_ping("https://example.com")
print(r.ttfb_ms, r.status_code)

# Geolocation
loc = geo_ip("8.8.8.8")
print(loc["country"], loc["city"])

# Traceroute
for hop in traceroute("8.8.8.8", max_hops=10):
    print(hop.hop, hop.ip, hop.rtt_ms)

# Active connections
for conn in get_connections(protocol="tcp", state_filter="ESTABLISHED"):
    print(conn.local_address, "->", conn.remote_address)

# Port scan
config = ScanConfig(targets=["example.com"], mode="fast", timeout=2.0)
for result in scan_ports(config):
    print("Open ports:", result.open_ports)
```

### ARP API

```python
from nadzoring.arp.cache import ARPCache
from nadzoring.arp.detector import ARPSpoofingDetector
from nadzoring.arp.realtime import ARPRealtimeDetector

# ARP cache
cache = ARPCache()
for entry in cache.get_cache():
    print(entry.ip_address, entry.mac_address, entry.state.value)

# Static spoofing detection
detector = ARPSpoofingDetector(cache)
for alert in detector.detect():
    print(alert.alert_type, alert.description)

# Real-time monitoring
rt = ARPRealtimeDetector()
alerts = rt.monitor(interface="eth0", count=50, timeout=30)
```

---

## Examples

### DNS Diagnostics

```bash
nadzoring dns health example.com
nadzoring dns trace example.com
nadzoring dns compare -t A -t MX example.com
nadzoring dns check -t ALL -v example.com
```

### Reverse DNS Batch Lookup

```bash
# Look up multiple IPs at once
nadzoring dns reverse 8.8.8.8 1.1.1.1 9.9.9.9 208.67.222.222

# Save results
nadzoring dns reverse -o json --save ptr_records.json 8.8.8.8 1.1.1.1
```

### DNS Poisoning Detection

```bash
nadzoring dns poisoning -v twitter.com
nadzoring dns poisoning -c 8.8.8.8 -c 1.1.1.1 example.com
nadzoring dns poisoning -o html --save poisoning_report.html github.com
```

### DNS Performance Benchmarking

```bash
nadzoring dns benchmark --queries 20 --parallel
nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 208.67.222.222 -s 9.9.9.9
nadzoring dns benchmark -t MX -d gmail.com --queries 15
```

### Port Scanning

```bash
nadzoring network-base port-scan --mode full --protocol tcp example.com
nadzoring network-base port-scan --mode custom --ports 20-1024 example.com
nadzoring network-base port-scan -o csv --save network_scan.csv 192.168.1.1
```

### HTTP Service Probing

```bash
nadzoring network-base http-ping --show-headers https://api.example.com/health
nadzoring network-base http-ping https://google.com https://cloudflare.com https://github.com
nadzoring network-base http-ping -o csv --save http_metrics.csv https://example.com
```

### ARP Spoofing Detection

```bash
nadzoring arp detect-spoofing eth0
nadzoring arp monitor-spoofing --interface eth0 --timeout 60
nadzoring arp monitor-spoofing -o json --save arp_alerts.json
```

### Network Path Analysis

```bash
nadzoring network-base traceroute --max-hops 30 github.com
nadzoring network-base traceroute google.com cloudflare.com amazon.com
nadzoring network-base route
nadzoring network-base connections --state LISTEN
```

### Complete Network Diagnostics

```bash
nadzoring network-base params -v
nadzoring network-base host-to-ip google.com cloudflare.com github.com
nadzoring network-base ping 8.8.8.8 1.1.1.1 google.com
nadzoring network-base geolocation 8.8.8.8 1.1.1.1
nadzoring network-base port-scan --mode fast example.com
nadzoring network-base traceroute cloudflare.com
nadzoring arp cache
```

### Automated DNS Server Monitoring

This section covers three integration approaches for continuous monitoring:
a **shell script** for use with cron/systemd, a **Python script** for
in-process loops with alerting, and **scheduling setup** for both Linux and Windows.

#### Shell script with alerting thresholds

Save as `dns_monitor.sh` and make executable (`chmod +x dns_monitor.sh`):

```bash
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
```

#### Scheduling with cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Run every 5 minutes
*/5 * * * * /path/to/dns_monitor.sh example.com 8.8.8.8

# Run every hour with email alerts
0 * * * * DNS_ALERT_EMAIL=ops@example.com /path/to/dns_monitor.sh example.com 8.8.8.8

# Run every 15 minutes, logging cron output
*/15 * * * * /path/to/dns_monitor.sh example.com 8.8.8.8 >> /var/log/nadzoring/cron.log 2>&1
```

#### Scheduling with systemd timer (Linux, recommended)

Create `/etc/systemd/system/nadzoring-dns-monitor.service`:

```ini
[Unit]
Description=Nadzoring DNS health monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/path/to/dns_monitor.sh example.com 8.8.8.8
Environment=DNS_MONITOR_DIR=/var/log/nadzoring
Environment=DNS_ALERT_EMAIL=ops@example.com
StandardOutput=journal
StandardError=journal
```

Create `/etc/systemd/system/nadzoring-dns-monitor.timer`:

```ini
[Unit]
Description=Run Nadzoring DNS monitor every 5 minutes

[Timer]
OnBootSec=60
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nadzoring-dns-monitor.timer
sudo systemctl status nadzoring-dns-monitor.timer
journalctl -u nadzoring-dns-monitor.service -f   # follow live logs
```

#### Python continuous monitoring loop (in-process)

Use `DNSMonitor` directly for in-process monitoring with custom alerting:

**Infinite loop (blocks until Ctrl-C or SIGTERM):**

```python
from nadzoring.dns_lookup.monitor import AlertEvent, DNSMonitor, MonitorConfig


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
)

monitor = DNSMonitor(config)
monitor.run()
print(monitor.report())
```

**Finite cycles (CI pipelines, cron scripts):**

```python
from nadzoring.dns_lookup.monitor import DNSMonitor, MonitorConfig
from statistics import mean

config = MonitorConfig(
    domain="example.com",
    nameservers=["8.8.8.8", "1.1.1.1"],
    interval=10.0,
    run_health_check=False,
)
monitor = DNSMonitor(config)
history = monitor.run_cycles(6)

rts = [
    s.avg_response_time_ms
    for c in history
    for s in c.samples
    if s.avg_response_time_ms is not None
]
print(f"Mean RT: {mean(rts):.1f}ms")
print(monitor.report())
```

**Analyse saved log:**

```python
from nadzoring.dns_lookup.monitor import load_log
from statistics import mean

cycles = load_log("dns_monitor.jsonl")
rts = [
    s["avg_response_time_ms"]
    for c in cycles
    for s in c["samples"]
    if s["avg_response_time_ms"] is not None
]
alerts = [a for c in cycles for a in c.get("alerts", [])]
print(f"Cycles: {len(cycles)}  Mean RT: {mean(rts):.1f}ms  Alerts: {len(alerts)}")
```
### Quick Website Block Check

```bash
nadzoring dns resolve -t ALL example.com
nadzoring dns reverse 93.184.216.34
nadzoring dns trace example.com
nadzoring network-base ping example.com
nadzoring dns compare example.com
nadzoring dns poisoning example.com
nadzoring network-base http-ping https://example.com
nadzoring network-base traceroute example.com
```

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

**Workflow:**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Areas we'd love help with:**

- Additional DNS record type support
- New health check validation rules
- CDN network database expansion
- Performance optimisations
- Additional output formats
- ARP detection heuristics
- New network diagnostic commands

---

## Documentation

| Version | Link | Status |
|---------|------|--------|
| **main** | [Latest (development)](https://alexeev-prog.github.io/nadzoring/main) | 🟡 Development |
| **v0.1.5** | [Stable release](https://alexeev-prog.github.io/nadzoring/v0.1.5) | 🟢 Stable |
| v0.1.4 | [Previous release](https://alexeev-prog.github.io/nadzoring/v0.1.4) | ⚪ Legacy |
| v0.1.3 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.3) | ⚪ Legacy |
| v0.1.2 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.2) | ⚪ Legacy |
| v0.1.1 | [First version](https://alexeev-prog.github.io/nadzoring/v0.1.1) | ⚪ Legacy |

---

## License & Support

This project is licensed under the **GNU GPL v3 License** — see [LICENSE](https://github.com/alexeev-prog/nadzoring/blob/main/LICENSE) for details.

For commercial support or enterprise features, contact [alexeev.dev@mail.ru](mailto:alexeev.dev@mail.ru).

[📖 Explore Docs](https://alexeev-prog.github.io/nadzoring) · [🐛 Report Issue](https://github.com/alexeev-prog/nadzoring/issues)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
Copyright © 2025 Alexeev Bronislav. Distributed under GNU GPL v3 license.
