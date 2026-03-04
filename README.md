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
    <a href="https://alexeev-prog.github.io/nadzoring/v0.1.4">v0.1.4 Documentation</a>
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

Nadzoring (from Russian "надзор" - supervision/oversight + English "-ing" suffix) is a FOSS (Free and Open Source Software) command-line tool for detecting website blocks, monitoring service availability, and network analysis. It helps you investigate network connectivity issues, check if websites are accessible, and analyze network configurations with comprehensive DNS diagnostics, including advanced DNS poisoning detection.

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
      - [geolocation](#geolocation)
      - [params](#params)
      - [host-to-ip](#host-to-ip)
      - [port-service](#port-service)
      - [port-scan](#port-scan)
      - [http-ping](#http-ping)
      - [whois](#whois)
      - [connections](#connections)
      - [traceroute](#traceroute)
      - [route](#route)
    - [ARP Commands](#arp-commands)
      - [arp cache](#arp-cache)
      - [arp detect-spoofing](#arp-detect-spoofing)
      - [arp monitor-spoofing](#arp-monitor-spoofing)
  - [Output Formats](#output-formats)
    - [Table Format (default)](#table-format-default)
    - [JSON Format](#json-format)
    - [CSV Format](#csv-format)
    - [HTML Format](#html-format)
  - [Saving Results](#saving-results)
  - [Logging Levels](#logging-levels)
  - [Examples](#examples)
    - [DNS Diagnostics](#dns-diagnostics)
    - [DNS Poisoning Detection](#dns-poisoning-detection)
    - [DNS Performance Benchmarking](#dns-performance-benchmarking)
    - [Port Scanning](#port-scanning)
    - [HTTP Service Probing](#http-service-probing)
    - [ARP Spoofing Detection](#arp-spoofing-detection)
    - [Network Path Analysis](#network-path-analysis)
    - [Complete Network Diagnostics](#complete-network-diagnostics)
    - [Automated Monitoring Script](#automated-monitoring-script)
    - [Quick Website Block Check](#quick-website-block-check)
  - [Contributing](#contributing)
  - [Documentation](#documentation)
  - [License \& Support](#license--support)

# Getting Started

### Prerequisites

- Python 3.12+
- pip
- traceroute
- whois
- ip tools (Linux) or route (Windows)

### Installation

```bash
pip install nadzoring
```

Verify the installation:

```bash
nadzoring --help
```

## Usage

Nadzoring uses a hierarchical command structure with three main command groups: `dns`, `network-base`, and `arp`. All commands support common global options for output formatting and logging.

### Global Options

These options are available for all commands:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Enable verbose output with execution timing | `False` |
| `--quiet` | `-q` | Suppress non-error output (progress bars, logs) | `False` |
| `--no-color` | - | Disable colored output | `False` |
| `--output` | `-o` | Output format (`table`, `json`, `csv`, `html`, `html_table`) | `table` |
| `--save` | - | Save results to file (provide filename) | None |

### DNS Commands

The `dns` command group provides comprehensive DNS analysis and troubleshooting capabilities.

#### dns resolve

Resolve DNS records for one or more domains with support for multiple record types.

**Syntax:**
```bash
nadzoring dns resolve [OPTIONS] DOMAINS...
```

**Arguments:**
- `DOMAINS...` - One or more domain names to resolve (required)

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--type` | `-t` | DNS record type (A, AAAA, CNAME, MX, NS, TXT, ALL) | `A` |
| `--nameserver` | `-n` | Specific nameserver to use | System default |
| `--short` | - | Compact output like host command style | `False` |
| `--show-ttl` | - | Show TTL for each record | `False` |
| `--format-style` | - | Output style (standard, bind, host, dig) | `standard` |

**Examples:**
```bash
# Basic A record lookup
nadzoring dns resolve google.com

# Multiple record types
nadzoring dns resolve -t A -t MX -t TXT example.com

# ALL record types with specific nameserver
nadzoring dns resolve -t ALL -n 8.8.8.8 github.com

# Multiple domains with TTL display
nadzoring dns resolve --show-ttl google.com cloudflare.com

# Short format like host command
nadzoring dns resolve --short --type ALL example.com
```

#### dns reverse

Perform reverse DNS lookup (PTR records) for IP addresses.

**Syntax:**
```bash
nadzoring dns reverse [OPTIONS] IP_ADDRESSES...
```

**Arguments:**
- `IP_ADDRESSES...` - One or more IP addresses to look up (required)

**Options:**
| Option | Short | Description |
|--------|-------|-------------|
| `--nameserver` | `-n` | Specific nameserver to use |

**Examples:**
```bash
# Basic reverse lookup
nadzoring dns reverse 8.8.8.8

# Multiple IPs
nadzoring dns reverse 1.1.1.1 8.8.8.8 9.9.9.9

# Using specific nameserver
nadzoring dns reverse -n 208.67.222.222 8.8.4.4
```

#### dns check

Perform comprehensive DNS check including validation of MX priorities and TXT records (SPF/DKIM).

**Syntax:**
```bash
nadzoring dns check [OPTIONS] DOMAINS...
```

**Arguments:**
- `DOMAINS...` - One or more domain names to check (required)

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--nameserver` | `-n` | Specific nameserver to use | System default |
| `--types` | `-t` | Record types to check (A, AAAA, CNAME, MX, NS, TXT, ALL) | `ALL` |

**Features:**
- MX record validation (duplicate priority detection)
- TXT record validation (SPF policy checks, DKIM key presence)
- Comprehensive error reporting

**Examples:**
```bash
# Complete DNS check
nadzoring dns check example.com

# Check specific record types
nadzoring dns check -t MX -t TXT gmail.com

# Multiple domains with custom nameserver
nadzoring dns check -n 9.9.9.9 google.com cloudflare.com
```

#### dns trace

Trace the DNS resolution path from root servers to authoritative nameservers.

**Syntax:**
```bash
nadzoring dns trace [OPTIONS] DOMAIN
```

**Arguments:**
- `DOMAIN` - Domain name to trace (required)

**Options:**
| Option | Short | Description |
|--------|-------|-------------|
| `--nameserver` | `-n` | Starting nameserver (default: a.root-servers.net - 198.41.0.4) |

**Output shows:**
- Each hop with nameserver IP
- Response time per nameserver
- Records returned at each level
- Delegation information
- Final authoritative answer

**Examples:**
```bash
# Trace from root servers
nadzoring dns trace example.com

# Trace starting from specific nameserver
nadzoring dns trace -n 8.8.8.8 google.com

# Verbose trace with timing
nadzoring dns trace -v github.com
```

#### dns compare

Compare DNS responses from different nameservers to detect discrepancies.

**Syntax:**
```bash
nadzoring dns compare [OPTIONS] DOMAIN
```

**Arguments:**
- `DOMAIN` - Domain name to compare (required)

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--servers` | `-s` | DNS servers to compare | `8.8.8.8`, `1.1.1.1`, `9.9.9.9` |
| `--type` | `-t` | Record types to compare | `A` |

**Features:**
- Response time comparison
- Record consistency checking
- Automatic discrepancy detection
- Progress indicator for multiple queries

**Examples:**
```bash
# Compare A records across default servers
nadzoring dns compare example.com

# Compare MX records with custom servers
nadzoring dns compare -t MX -s 8.8.8.8 -s 208.67.222.222 -s 9.9.9.9 gmail.com

# Multiple record types
nadzoring dns compare -t A -t AAAA -t NS cloudflare.com
```

#### dns health

Perform comprehensive DNS health check with scoring system.

**Syntax:**
```bash
nadzoring dns health [OPTIONS] DOMAIN
```

**Arguments:**
- `DOMAIN` - Domain name to check (required)

**Options:**
| Option | Short | Description |
|--------|-------|-------------|
| `--nameserver` | `-n` | Nameserver to use for checks |

**Health Scoring:**
- **80-100**: Healthy - All records properly configured
- **50-79**: Degraded - Some issues detected
- **0-49**: Unhealthy - Critical configuration problems

**Validation includes:**
- Record presence for all standard types
- MX priority uniqueness
- SPF policy completeness
- DKIM key presence
- CNAME configuration rules
- Subdomain-specific checks

**Examples:**
```bash
# Basic health check
nadzoring dns health example.com

# Health check with custom nameserver
nadzoring dns health -n 1.1.1.1 google.com

# Verbose health report
nadzoring dns health -v github.com
```

#### dns benchmark

Benchmark DNS server performance with configurable queries.

**Syntax:**
```bash
nadzoring dns benchmark [OPTIONS]
```

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--domain` | `-d` | Domain to use for benchmarking | `google.com` |
| `--servers` | `-s` | DNS servers to benchmark (can be used multiple times) | Public DNS servers |
| `--type` | `-t` | Record type to query (A, AAAA, MX, NS, TXT) | `A` |
| `--queries` | `-q` | Number of queries per server | `10` |
| `--parallel/--sequential` | - | Run benchmarks in parallel or sequentially | `parallel` |

**Output includes:**
- Average response time
- Minimum/maximum response time
- Success rate percentage
- Failed queries count

**Examples:**
```bash
# Benchmark default servers
nadzoring dns benchmark

# Benchmark specific servers with 20 queries each
nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 9.9.9.9 --queries 20

# Benchmark MX records sequentially
nadzoring dns benchmark -t MX --sequential

# Save results as JSON
nadzoring dns benchmark -o json --save dns_benchmark.json
```

#### dns poisoning

Detect DNS poisoning, censorship, or CDN-based routing variations.

**Syntax:**
```bash
nadzoring dns poisoning [OPTIONS] DOMAIN
```

**Arguments:**
- `DOMAIN` - Domain name to check for poisoning (required)

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--control-server` | `-c` | Control server to compare against | `8.8.8.8` |
| `--test-servers` | `-t` | Test servers to check (can be used multiple times) | All public DNS servers |
| `--type` | `-T` | Record type to check | `A` |
| `--additional-types` | `-a` | Additional record types to check on control server | None |

**Detection Capabilities:**
- **CDN Detection**: Identifies legitimate CDN networks (Cloudflare, Google, Akamai, AWS, etc.)
- **Anycast/GeoDNS**: Recognizes normal anycast routing behavior
- **IP Pattern Analysis**: Analyzes IP ownership, geographic diversity, and network ranges
- **Consensus Checking**: Determines most common response across servers
- **Severity Classification**: Categorizes issues as INFO, LOW, MEDIUM, HIGH, or CRITICAL

**Output includes:**
- Poisoning level (NONE, LOW, MEDIUM, HIGH, CRITICAL, SUSPICIOUS)
- Confidence percentage
- Control server analysis
- IP ownership detection
- CDN detection with provider identification
- Inconsistency details per server
- Geo-diversity metrics
- Final verdict with explanation

**Examples:**
```bash
# Basic poisoning check
nadzoring dns poisoning example.com

# Check with custom control server and additional record types
nadzoring dns poisoning -c 1.1.1.1 -a MX -a TXT google.com

# Verbose poisoning analysis
nadzoring dns poisoning -v github.com

# Save detailed HTML report
nadzoring dns poisoning -o html --save poisoning_report.html example.com
```

### Network Base Commands

The `network-base` command group provides basic and advanced network operations and diagnostics.

#### ping

Ping one or more addresses to check reachability.

**Syntax:**
```bash
nadzoring network-base ping [OPTIONS] ADDRESSES...
```

**Arguments:**
- `ADDRESSES...` - One or more IP addresses or hostnames (required)

**Examples:**
```bash
# Ping single address
nadzoring network-base ping 8.8.8.8

# Multiple addresses
nadzoring network-base ping google.com cloudflare.com 1.1.1.1

# JSON output
nadzoring network-base ping -o json github.com
```

#### geolocation

Get geolocation information for IP addresses.

**Syntax:**
```bash
nadzoring network-base geolocation [OPTIONS] IPS...
```

**Arguments:**
- `IPS...` - One or more IP addresses (required)

**Output includes:**
- Latitude/Longitude
- Country
- City

**Examples:**
```bash
# Geolocate IPs
nadzoring network-base geolocation 8.8.8.8 1.1.1.1

# Save results
nadzoring network-base geolocation --save locations.json 8.8.8.8
```

#### params

Display detailed network configuration parameters of your system.

**Syntax:**
```bash
nadzoring network-base params [OPTIONS]
```

**Output includes:**
- Default interface name
- IPv4 address
- IPv6 address
- Router (gateway) IP
- MAC address
- Public IP address

**Examples:**
```bash
# Basic network info
nadzoring network-base params

# JSON output for scripting
nadzoring network-base params -o json

# Save configuration
nadzoring network-base params --save network_config.json
```

#### host-to-ip

Resolve hostnames to IP addresses with IPv4/IPv6 availability checking.

**Syntax:**
```bash
nadzoring network-base host-to-ip [OPTIONS] HOSTNAMES...
```

**Arguments:**
- `HOSTNAMES...` - One or more domain names (required)

**Output includes:**
- Resolved IP address
- IPv4 connectivity check
- IPv6 connectivity check
- Router IPv4/IPv6 addresses

**Examples:**
```bash
# Resolve multiple domains
nadzoring network-base host-to-ip google.com github.com cloudflare.com

# CSV output for analysis
nadzoring network-base host-to-ip -o csv --save resolutions.csv example.com
```

#### port-service

Identify which service typically runs on specified ports.

**Syntax:**
```bash
nadzoring network-base port-service [OPTIONS] PORTS...
```

**Arguments:**
- `PORTS...` - One or more port numbers (required)

**Examples:**
```bash
# Check common ports
nadzoring network-base port-service 80 443 22 53 3306

# JSON output for integration
nadzoring network-base port-service -o json 8080 5432 27017
```

#### port-scan

Scan for open ports on one or more targets with configurable scanning modes.

**Syntax:**
```bash
nadzoring network-base port-scan [OPTIONS] TARGETS...
```

**Arguments:**
- `TARGETS...` - One or more IP addresses or hostnames to scan (required)

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--mode` | - | Scan mode: fast, full, or custom | `fast` |
| `--ports` | - | Custom ports or range (e.g., '22,80,443' or '1-1024') | None |
| `--protocol` | - | Protocol to scan (tcp, udp) | `tcp` |
| `--timeout` | - | Socket timeout in seconds | `2.0` |
| `--workers` | - | Maximum number of concurrent workers per target | `50` |
| `--show-closed` | - | Show closed ports in results | `False` |
| `--no-banner` | - | Disable banner grabbing | `False` |

**Scan Modes:**
- **fast**: Scans 20 most common ports
- **full**: Scans all ports (1-65535)
- **custom**: Uses --ports specification

**Features:**
- Concurrent scanning with worker pool
- Banner grabbing for service identification
- Progress bar with real-time updates
- Support for TCP and UDP protocols
- Custom port ranges and lists

**Examples:**
```bash
# Fast scan of common ports
nadzoring network-base port-scan example.com

# Full port scan
nadzoring network-base port-scan --mode full 192.168.1.1

# Custom port range with UDP
nadzoring network-base port-scan --mode custom --ports 1-1024 --protocol udp example.com

# Multiple targets with banner grabbing
nadzoring network-base port-scan --show-closed 192.168.1.1 192.168.1.2

# Save results as JSON
nadzoring network-base port-scan -o json --save scan_results.json example.com
```

#### http-ping

Check HTTP/HTTPS response timing and headers for one or more URLs.

**Syntax:**
```bash
nadzoring network-base http-ping [OPTIONS] URLS...
```

**Arguments:**
- `URLS...` - One or more URLs to probe (required)

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--timeout` | - | Request timeout in seconds | `10.0` |
| `--no-ssl-verify` | - | Disable SSL certificate verification | `False` |
| `--no-redirects` | - | Do not follow HTTP redirects | `False` |
| `--show-headers` | - | Include response headers in output | `False` |

**Output includes:**
- DNS resolution time (ms)
- Time to first byte (TTFB) (ms)
- Total download time (ms)
- HTTP status code
- Content size (bytes)
- Redirect target (if any)
- Response headers (if requested)

**Examples:**
```bash
# Basic HTTP ping
nadzoring network-base http-ping https://example.com

# Multiple URLs with header inspection
nadzoring network-base http-ping --show-headers https://google.com https://github.com

# Custom timeout with SSL verification disabled
nadzoring network-base http-ping --timeout 5 --no-ssl-verify https://self-signed.badssl.com

# CSV output for analysis
nadzoring network-base http-ping -o csv --save http_times.csv https://api.github.com
```

#### whois

Look up WHOIS registration information for one or more domains or IPs.

**Syntax:**
```bash
nadzoring network-base whois [OPTIONS] TARGETS...
```

**Arguments:**
- `TARGETS...` - One or more domain names or IP addresses (required)

**Requirements:**
- System 'whois' utility must be installed
  - Debian/Ubuntu: `apt install whois`
  - macOS: `brew install whois`
  - RHEL/CentOS: `yum install whois`

**Output includes:**
- Registrar information
- Creation and expiration dates
- Name servers
- Registrant contact (if available)
- Domain status codes

**Examples:**
```bash
# WHOIS lookup for domain
nadzoring network-base whois example.com

# Multiple targets
nadzoring network-base whois google.com cloudflare.com 8.8.8.8

# JSON output for automation
nadzoring network-base whois -o json --save whois_data.json github.com
```

#### connections

List active network connections (TCP/UDP) with process information.

**Syntax:**
```bash
nadzoring network-base connections [OPTIONS]
```

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--protocol` | `-p` | Filter by protocol (tcp, udp, all) | `all` |
| `--state` | `-s` | Filter by state substring (e.g., LISTEN, ESTABLISHED) | None |
| `--no-process` | - | Skip process/PID info (avoids permission errors) | `False` |

**Output includes:**
- Protocol (TCP/UDP)
- Local address and port
- Remote address and port
- Connection state
- PID and process name (if available)

**Examples:**
```bash
# List all connections
nadzoring network-base connections

# Show only listening TCP ports
nadzoring network-base connections --protocol tcp --state LISTEN

# UDP connections without process info
nadzoring network-base connections --protocol udp --no-process

# Save as CSV for analysis
nadzoring network-base connections -o csv --save connections.csv
```

#### traceroute

Trace the network path to one or more hosts.

**Syntax:**
```bash
nadzoring network-base traceroute [OPTIONS] TARGETS...
```

**Arguments:**
- `TARGETS...` - One or more hostnames or IP addresses (required)

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--max-hops` | - | Maximum number of hops | `30` |
| `--timeout` | - | Per-hop timeout in seconds | `2.0` |
| `--sudo` | - | Run traceroute with sudo (required on some Linux systems) | `False` |

**Requirements:**
- On Linux, raw-socket access needed: run with --sudo, as root, or grant capability:
  ```
  sudo setcap cap_net_raw+ep $(which traceroute)
  ```
- tracepath is tried automatically as a root-free fallback

**Output includes:**
- Hop number
- Hostname (if resolvable)
- IP address
- Round-trip times (three probes)

**Examples:**
```bash
# Basic traceroute
nadzoring network-base traceroute google.com

# Multiple targets with custom max hops
nadzoring network-base traceroute --max-hops 20 github.com cloudflare.com

# With sudo on Linux
nadzoring network-base traceroute --sudo example.com

# HTML report generation
nadzoring network-base traceroute -o html --save trace_report.html 8.8.8.8
```

#### route

Display the system IP routing table.

**Syntax:**
```bash
nadzoring network-base route [OPTIONS]
```

**Requirements:**
- Linux: 'ip' utility
- Windows: 'route' utility

**Output includes:**
- Destination network
- Gateway address
- Netmask
- Interface
- Metric

**Examples:**
```bash
# Display routing table
nadzoring network-base route

# JSON output for scripting
nadzoring network-base route -o json

# Save routing table
nadzoring network-base route --save routing_table.json
```

### ARP Commands

The `arp` command group provides ARP cache management and spoofing detection capabilities.

#### arp cache

Show current ARP cache table.

**Syntax:**
```bash
nadzoring arp cache [OPTIONS]
```

**Output includes:**
- IP address
- MAC address
- Network interface
- ARP state (PERMANENT, STALE, REACHABLE, INCOMPLETE)

**Examples:**
```bash
# Display ARP cache
nadzoring arp cache

# Save as CSV
nadzoring arp cache -o csv --save arp_cache.csv

# JSON output for automation
nadzoring arp cache -o json
```

#### arp detect-spoofing

Detect potential ARP spoofing attacks on one or more interfaces.

**Syntax:**
```bash
nadzoring arp detect-spoofing [OPTIONS] [INTERFACES]...
```

**Arguments:**
- `INTERFACES...` - Network interfaces to check (optional, checks all interfaces if none specified)

**Detection capabilities:**
- Multiple IPs mapping to the same MAC address
- Duplicate MAC addresses on the same interface
- Invalid MAC addresses (broadcast, multicast, null)
- MAC address changes over time

**Output includes:**
- Alert type (DUPLICATE_IP, DUPLICATE_MAC, INVALID_MAC, CHANGED_MAC)
- IP address involved
- MAC address involved
- Network interface
- Description of the issue

**Examples:**
```bash
# Check all interfaces
nadzoring arp detect-spoofing

# Check specific interfaces
nadzoring arp detect-spoofing eth0 wlan0

# Save detection results
nadzoring arp detect-spoofing -o json --save spoofing_alerts.json
```

#### arp monitor-spoofing

Monitor network for ARP spoofing attacks in real-time.

**Syntax:**
```bash
nadzoring arp monitor-spoofing [OPTIONS]
```

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--interface` | `-i` | Network interface to monitor | All interfaces |
| `--count` | `-c` | Number of packets to capture | `10` |
| `--timeout` | `-t` | Timeout in seconds | `30` |

**Features:**
- Real-time ARP packet capture
- IP-to-MAC mapping tracking
- Duplicate IP detection
- MAC address change detection
- Real-time alerts with colorized output

**Examples:**
```bash
# Monitor all interfaces
nadzoring arp monitor-spoofing

# Monitor specific interface for 100 packets
nadzoring arp monitor-spoofing --interface eth0 --count 100

# Monitor with 60 second timeout
nadzoring arp monitor-spoofing --timeout 60

# Save captured alerts
nadzoring arp monitor-spoofing -o json --save arp_alerts.json
```

## Output Formats

Nadzoring supports four output formats controlled by the `-o/--output` flag:

### Table Format (default)
```
┌─────────────┬────────┬─────────────┐
│ domain      │ type   │ value       │
├─────────────┼────────┼─────────────┤
│ example.com │ A      │ 93.184.216.34│
│ example.com │ MX     │ 10 mail.example.com│
└─────────────┴────────┴─────────────┘
```

### JSON Format
```json
[
  {
    "domain": "example.com",
    "type": "A",
    "value": "93.184.216.34"
  }
]
```

### CSV Format
```csv
domain,type,value
example.com,A,93.184.216.34
```

### HTML Format
Generates styled HTML tables or complete web pages with CSS styling.

## Saving Results

Use the `--save` option to save command output to a file. The format is determined by the `-o/--output` flag:

```bash
# Save DNS check as HTML report
nadzoring dns check -o html --save dns_report.html example.com

# Save comparison as CSV
nadzoring dns compare -o csv --save comparison.csv google.com

# Save poisoning detection as JSON
nadzoring dns poisoning -o json --save poisoning_results.json example.com

# Save trace as HTML
nadzoring dns trace -o html --save trace.html cloudflare.com

# Save port scan results
nadzoring network-base port-scan -o json --save scan.json example.com

# Save ARP cache
nadzoring arp cache -o csv --save arp.csv
```

## Logging Levels

Nadzoring provides three logging modes:

- **Normal mode** (no flags): Shows command output and warnings with progress bars
- **Verbose mode** (`-v/--verbose`): Shows detailed execution information, timing, and debug logs
- **Quiet mode** (`-q/--quiet`): Suppresses progress bars and non-error output, ideal for scripting

## Examples

### DNS Diagnostics
```bash
# Complete DNS investigation workflow
nadzoring dns health example.com
nadzoring dns trace example.com
nadzoring dns compare -t A -t MX example.com
nadzoring dns check -t ALL -v example.com
```

### DNS Poisoning Detection
```bash
# Check if a domain might be censored or poisoned
nadzoring dns poisoning -v twitter.com

# Compare with multiple control servers
nadzoring dns poisoning -c 8.8.8.8 -c 1.1.1.1 -c 9.9.9.9 example.com

# Generate detailed HTML report
nadzoring dns poisoning -o html --save poisoning_report.html github.com
```

### DNS Performance Benchmarking
```bash
# Find fastest DNS server for your location
nadzoring dns benchmark --queries 20 --parallel

# Compare specific servers
nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 208.67.222.222 -s 9.9.9.9

# Benchmark different record types
nadzoring dns benchmark -t MX -d gmail.com --queries 15
```

### Port Scanning
```bash
# Comprehensive port scan
nadzoring network-base port-scan --mode full --protocol tcp example.com

# Service identification with banner grabbing
nadzoring network-base port-scan --mode custom --ports 20-1024 --no-banner example.com

# Multiple target scan with CSV export
nadzoring network-base port-scan -o csv --save network_scan.csv 192.168.1.0/24
```

### HTTP Service Probing
```bash
# Monitor web service performance
nadzoring network-base http-ping --show-headers https://api.example.com/health

# Check multiple endpoints
nadzoring network-base http-ping https://google.com https://cloudflare.com https://github.com

# Save timing metrics
nadzoring network-base http-ping -o csv --save http_metrics.csv https://example.com
```

### ARP Spoofing Detection
```bash
# Detect existing spoofing
nadzoring arp detect-spoofing eth0

# Real-time monitoring
nadzoring arp monitor-spoofing --interface eth0 --timeout 60

# Save alerts for forensic analysis
nadzoring arp monitor-spoofing -o json --save arp_alerts.json
```

### Network Path Analysis
```bash
# Trace route with timing
nadzoring network-base traceroute --max-hops 30 github.com

# Compare routes to multiple destinations
nadzoring network-base traceroute google.com cloudflare.com amazon.com

# Display routing table
nadzoring network-base route

# Check active connections
nadzoring network-base connections --state LISTEN
```

### Complete Network Diagnostics
```bash
# Run comprehensive network diagnostics
nadzoring network-base params -v
nadzoring network-base host-to-ip google.com cloudflare.com github.com
nadzoring network-base ping 8.8.8.8 1.1.1.1 google.com
nadzoring network-base geolocation 8.8.8.8 1.1.1.1
nadzoring network-base port-scan --mode fast example.com
nadzoring network-base traceroute cloudflare.com
nadzoring arp cache
```

### Automated Monitoring Script
```bash
#!/bin/bash
# Check DNS health and network status with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# DNS health check
nadzoring dns health -o json --save "dns_health_${TIMESTAMP}.json" example.com

# DNS poisoning check
nadzoring dns poisoning -o html --save "poisoning_${TIMESTAMP}.html" example.com

# DNS trace
nadzoring dns trace -o html --save "dns_trace_${TIMESTAMP}.html" example.com

# Network parameters
nadzoring network-base params -o csv --save "network_${TIMESTAMP}.csv"

# DNS benchmark summary
nadzoring dns benchmark -o table --save "benchmark_${TIMESTAMP}.txt"

# Port scan of critical services
nadzoring network-base port-scan -o json --save "port_scan_${TIMESTAMP}.json" example.com

# HTTP service check
nadzoring network-base http-ping --show-headers -o html --save "http_${TIMESTAMP}.html" https://example.com

# ARP cache snapshot
nadzoring arp cache -o csv --save "arp_${TIMESTAMP}.csv"
```

### Quick Website Block Check
```bash
# Check if a website might be blocked
nadzoring dns resolve -t ALL example.com
nadzoring dns trace example.com
nadzoring network-base ping example.com
nadzoring dns compare example.com
nadzoring dns poisoning example.com
nadzoring network-base http-ping https://example.com
nadzoring network-base traceroute example.com
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

**Areas we'd love help with:**
- Additional DNS record type support
- New validation rules for health checks
- CDN network database expansion
- Performance optimizations
- Additional output formats
- IDE/editor integration plugins
- Additional ARP detection heuristics
- New network diagnostic commands

**Workflow:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

| Version | Link | Status |
|---------|------|--------|
| **main** | [Latest (development)](https://alexeev-prog.github.io/nadzoring/main) | 🟡 Development |
| **v0.1.4** | [Stable release](https://alexeev-prog.github.io/nadzoring/v0.1.4) | 🟢 Stable |
| v0.1.3 | [Stable release](https://alexeev-prog.github.io/nadzoring/v0.1.3) | ⚪ Legacy |
| v0.1.2 | [Previous stable](https://alexeev-prog.github.io/nadzoring/v0.1.2) | ⚪ Legacy |
| v0.1.1 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.1) | ⚪ Legacy |
| v0.1.0 | [Initial release](https://alexeev-prog.github.io/nadzoring/v0.1.0) | ⚪ Legacy |

## License & Support

This project is licensed under the **GNU GPL v3 License** — see [LICENSE](https://github.com/alexeev-prog/nadzoring/blob/main/LICENSE) for details.

For commercial support or enterprise features, contact [alexeev.dev@mail.ru](mailto:alexeev.dev@mail.ru).

[📖 Explore Docs](https://alexeev-prog.github.io/nadzoring) · [🐛 Report Issue](https://github.com/alexeev-prog/nadzoring/issues)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
Copyright © 2025 Alexeev Bronislav. Distributed under GNU GPL v3 license.
