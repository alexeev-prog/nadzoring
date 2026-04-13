
<a id="readme-top"></a>

<div align="center">
  <p align="center">
    <img src="https://raw.githubusercontent.com/alexeev-prog/nadzoring/refs/heads/main/docs/logo.png" width=300>
    <h2>Nadzoring</h2>
    <p>An open source tool and python library for detecting website blocks, downdetecting and network analysis</p>
    <a href="https://alexeev-prog.github.io/nadzoring/v0.2.1"><strong>Explore the docs »</strong></a>
  </p>
  <p align="center">
    <a href="#-getting-started">Getting Started</a>
    ·
    <a href="#-usage-examples">Basic Usage</a>
    ·
    <a href="https://www.pitchhut.com/project/nadzoring-tool">Pitchhut</a>
    ·
    <a href="https://context7.com/alexeev-prog/nadzoring">Context7</a>
    ·
    <a href="https://deepwiki.com/alexeev-prog/nadzoring">Deepwiki</a>
    ·
    <a href="https://alexeev-prog.github.io/nadzoring/main">Latest Documentation</a>
    ·
    <a href="https://github.com/alexeev-prog/nadzoring/blob/main/LICENSE">License</a>
  </p>
</div>
<hr>
<p align="center">
    <img src="https://img.shields.io/github/languages/top/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/github/languages/count/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/badge/Maintained-yes-green.svg?style=for-the-badge">
    <img alt="GitHub License" src="https://img.shields.io/github/license/alexeev-prog/nadzoring?style=for-the-badge&logo=gnu">
    <img alt="GitHub forks" src="https://img.shields.io/github/forks/alexeev-prog/nadzoring?style=for-the-badge&logo=github">
    <img src="https://img.shields.io/github/stars/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/github/issues/alexeev-prog/nadzoring?style=for-the-badge">
    <img src="https://img.shields.io/github/last-commit/alexeev-prog/nadzoring?style=for-the-badge">
    <img alt="GitHub commits since latest release" src="https://img.shields.io/github/commits-since/alexeev-prog/nadzoring/latest?style=for-the-badge">
    <img alt="GitHub Release Date" src="https://img.shields.io/github/release-date-pre/alexeev-prog/nadzoring?style=for-the-badge">
    <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/alexeev-prog/nadzoring/docs.yml?style=for-the-badge&logo=github&label=docs">
    <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/alexeev-prog/nadzoring/python-package.yml?style=for-the-badge&logo=python&label=python%20package%20lint">
    <img src="https://img.shields.io/pypi/wheel/nadzoring?style=for-the-badge">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/nadzoring?style=for-the-badge">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/nadzoring?style=for-the-badge">
    <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/alexeev-prog/nadzoring?style=for-the-badge">
</p>
<p align="center">
    <img src="https://raw.githubusercontent.com/alexeev-prog/nadzoring/refs/heads/main/docs/pallet-0.png">
</p>

Nadzoring (from Russian "надзор" — supervision/oversight + the English "-ing" suffix) is a free and open-source command-line tool and Python library designed for in-depth network diagnostics, service availability monitoring, and website block detection. It empowers you to investigate connectivity issues, analyze network configurations, and audit security postures through a comprehensive suite of tools. From DNS diagnostics (including reverse lookups, poisoning detection, and delegation tracing) to ARP spoofing monitoring, SSL/TLS certificate analysis, HTTP security header auditing, email security validation (SPF/DKIM/DMARC), and subdomain discovery — Nadzoring brings together a wide range of capabilities in a single, consistent interface.

Built from the ground up with AI-friendliness in mind, Nadzoring is fully type-annotated, enforces a strict zero-warnings linter policy, and is architected according to SOLID principles with a strong emphasis on modularity and the Single Responsibility Principle (SRP). This architectural clarity ensures that the codebase remains maintainable, testable, and easy to extend. The project's high-quality typing and well-structured domain logic make it equally suitable for use as a reliable Python library in your own applications, as well as a powerful standalone CLI tool.

## Star History

<a href="https://www.star-history.com/?repos=alexeev-prog%2Fnadzoring&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=alexeev-prog/nadzoring&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=alexeev-prog/nadzoring&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=alexeev-prog/nadzoring&type=date&legend=top-left" />
 </picture>
</a>

<p align="center">
    <a href="https://deepwiki.com/alexeev-prog/nadzoring"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
    <img src="https://scrutinizer-ci.com/g/alexeev-prog/nadzoring/badges/quality-score.png?b=main">
    <a href="https://sloprank.io/repo/alexeev-prog/nadzoring"><img src="https://sloprank.io/badge/alexeev-prog/nadzoring.svg" alt="sloprank"></a>
    <a href='https://coveralls.io/github/alexeev-prog/nadzoring?branch=main'><img src='https://coveralls.io/repos/github/alexeev-prog/nadzoring/badge.svg?branch=main' alt='Coverage' /></a>
    <img src="https://img.shields.io/coderabbit/prs/github/alexeev-prog/nadzoring?utm_source=oss&utm_medium=github&utm_campaign=alexeev-prog%2Fnadzoring&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews" alt="CodeRabbit Pull Request Reviews">
</p>

## Table of Contents

- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running with Docker](#running-with-docker)
  - [Usage](#usage)
    - [Global Options](#global-options)
    - [Shell Completions](#shell-completions)
      - [Bash](#bash)
      - [Zsh](#zsh)
      - [Fish](#fish)
      - [PowerShell](#powershell)
      - [Testing Completions](#testing-completions)
      - [Manual Activation (without saving to profile)](#manual-activation-without-saving-to-profile)
      - [Troubleshooting Completions](#troubleshooting-completions)
      - [Completions Commands Reference](#completions-commands-reference)
    - [DNS Commands](#dns-commands)
      - [dns resolve](#dns-resolve)
      - [dns reverse](#dns-reverse)
      - [dns check](#dns-check)
      - [dns trace](#dns-trace)
      - [dns compare](#dns-compare)
      - [dns health](#dns-health)
      - [dns benchmark](#dns-benchmark)
      - [dns poisoning](#dns-poisoning)
      - [dns monitor](#dns-monitor)
      - [dns monitor-report](#dns-monitor-report)
    - [Network Base Commands](#network-base-commands)
      - [ping](#ping)
      - [http-ping](#http-ping)
      - [host-to-ip](#host-to-ip)
      - [parse-url](#parse-url)
      - [geolocation](#geolocation)
      - [params](#params)
      - [port-scan](#port-scan)
      - [detect-service](#detect-service)
      - [port-service](#port-service)
      - [whois](#whois)
      - [domain-info](#domain-info)
      - [connections](#connections)
      - [traceroute](#traceroute)
      - [route](#route)
    - [Security Commands](#security-commands)
      - [security check-ssl](#security-check-ssl)
      - [security check-headers](#security-check-headers)
      - [security check-email](#security-check-email)
      - [security subdomains](#security-subdomains)
      - [security watch-ssl](#security-watch-ssl)
    - [ARP Commands](#arp-commands)
      - [arp cache](#arp-cache)
      - [arp detect-spoofing](#arp-detect-spoofing)
      - [arp monitor-spoofing](#arp-monitor-spoofing)
  - [Output Formats](#output-formats)
  - [Saving Results](#saving-results)
  - [Logging Levels](#logging-levels)
  - [Timeout Configuration](#timeout-configuration)
  - [Error Handling](#error-handling)
  - [Python API](#python-api)
    - [DNS Lookup API](#dns-lookup-api)
    - [Reverse DNS API](#reverse-dns-api)
    - [Network Base API](#network-base-api)
    - [Security API](#security-api)
    - [ARP API](#arp-api)
  - [Examples](#examples)
    - [DNS Diagnostics](#dns-diagnostics)
    - [Reverse DNS Batch Lookup](#reverse-dns-batch-lookup)
    - [DNS Poisoning Detection](#dns-poisoning-detection)
    - [DNS Performance Benchmarking](#dns-performance-benchmarking)
    - [Port Scanning](#port-scanning)
    - [HTTP Service Probing](#http-service-probing)
    - [SSL/TLS Certificate Auditing](#ssltls-certificate-auditing)
    - [HTTP Security Header Auditing](#http-security-header-auditing)
    - [Email Security Validation](#email-security-validation)
    - [Subdomain Discovery](#subdomain-discovery)
    - [Continuous SSL Monitoring](#continuous-ssl-monitoring)
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
| `dig` / `nslookup` | `security check-email` (DNS TXT lookups; `dnspython` used when available) |

> **Note:** The Python package `netifaces` (used by `network-base params`) is distributed as source code and requires compilation on Linux. If you encounter errors during installation (e.g., `gcc: command not found`), install the required build tools first:
> `sudo apt update && sudo apt install build-essential python3-dev` (Debian/Ubuntu)
> or the equivalent for your distribution. On other platforms (Windows, macOS) pre‑compiled wheels are usually available.

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

### Running with Docker

For Linux users, Docker provides the easiest and most stable way to run Nadzoring without system dependency issues. The container comes with all necessary network capabilities pre-configured.

> **📘 Detailed Docker Guide:** See [Docker.md](Docker.md) for complete Docker setup instructions, including native Windows alternatives, development tips, and troubleshooting.

**Quick start with Docker:**

```bash
# Clone the repository
git clone https://github.com/alexeev-prog/nadzoring.git
cd nadzoring

# Build the Docker image
docker build -t nadzoring:latest .

# Create a convenient alias (add to ~/.bashrc or ~/.zshrc)
alias nadzoring='docker run --rm -it \
  --network host \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  nadzoring:latest'

# Now use Nadzoring normally
nadzoring --help
nadzoring dns resolve google.com
nadzoring network-base port-scan 192.168.1.0/24
nadzoring arp detect-spoofing
```

**Benefits of using Docker:**
- ✅ **Isolated environment** — No Python version conflicts or dependency issues
- ✅ **Easy updates** — Just rebuild the image with `git pull && docker build`
- ✅ **No system modifications** — Leaves your host system untouched
- ✅ **Consistent behavior** — Works the same across different Linux distributions
- ✅ **Network capabilities** — Pre-configured with NET_ADMIN and NET_RAW for full functionality

**Platform recommendation:**

| Platform | Recommended Method | Best For |
|----------|-------------------|----------|
| **Linux** | Docker (with alias) | Most users, servers, CI/CD |
| **Linux** | Native (pipx) | Performance, development |
| **Windows** | Native (pipx) | Best networking compatibility |

> **Note for Windows users:** Docker on Windows has limitations with raw sockets and local network access. Native installation via pipx is strongly recommended for Windows. See [Docker.md](Docker.md) for Windows-specific guidance.

---

## Usage

Nadzoring uses a hierarchical command structure: `nadzoring <group> <command> [OPTIONS]`.
The four main groups are `dns`, `network-base`, `security`, and `arp`.

### Global Options

These options work with every command:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | | Enable debug output with execution timing | `False` |
| `--quiet` | | Suppress non-error output | `False` |
| `--no-color` | | Disable colored output | `False` |
| `--output` | `-o` | Output format: `table`, `json`, `csv`, `html`, `html_table`, `yaml` | `table` |
| `--save` | | Save results to file | None |
| `--timeout` | | Lifetime timeout for the entire operation (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds). Falls back to `--timeout` | `5.0` |
| `--read-timeout` | | Read timeout (seconds). Falls back to `--timeout` | `10.0` |

**Timeout resolution order:**
1. Explicit `--connect-timeout` / `--read-timeout`
2. Generic `--timeout` (applies to both phases when phase-specific not set)
3. Module-level defaults (shown above)

### Shell Completions

Nadzoring provides tab-completion support for **bash**, **zsh**, **fish**, and **PowerShell**. Enable it for your preferred shell using the commands below.

#### Bash

Add to `~/.bashrc` (or `~/.bash_profile` on macOS):

```bash
echo 'eval "$(nadzoring completion bash)"' >> ~/.bashrc
source ~/.bashrc
```

Alternative — save to a file and source it:

```bash
nadzoring completion bash > ~/.nadzoring-complete.bash
echo 'source ~/.nadzoring-complete.bash' >> ~/.bashrc
```

#### Zsh

Add to `~/.zshrc`:

```bash
echo 'eval "$(nadzoring completion zsh)"' >> ~/.zshrc
source ~/.zshrc
```

Or save to a file in your `fpath`:

```bash
nadzoring completion zsh > "${fpath[1]}/_nadzoring"
```

#### Fish

Save directly to Fish completions directory:

```bash
nadzoring completion fish > ~/.config/fish/completions/nadzoring.fish
```

Or source it temporarily:

```bash
nadzoring completion fish | source
```

#### PowerShell

Add to your PowerShell profile (`$PROFILE`):

```powershell
nadzoring completion powershell >> $PROFILE
```

To reload the profile immediately:

```powershell
. $PROFILE
```

Or use it in the current session only:

```powershell
nadzoring completion powershell | Invoke-Expression
```

#### Testing Completions

After installation, type `nadzoring ` followed by **TAB** to see available commands:

```bash
nadzoring [TAB]
# Should show: arp  completion  dns  network-base  security
```

Type a command followed by space and **TAB** to see options:

```bash
nadzoring dns [TAB]
# Should show: resolve  reverse  check  trace  compare  health  benchmark  poisoning  monitor
```

#### Manual Activation (without saving to profile)

If you don't want to modify your shell profile, you can activate completions manually:

```bash
# Bash / Zsh
source <(nadzoring completion bash)

# Fish
nadzoring completion fish | source

# PowerShell
nadzoring completion powershell | Invoke-Expression
```

#### Troubleshooting Completions

**Completions not working?** Check these common issues:

1. **Shell not reloaded** — restart your terminal or run `source ~/.bashrc` (bash) / `source ~/.zshrc` (zsh)
2. **Wrong shell** — ensure you're using the correct completion command for your shell
3. **PATH issue** — verify `nadzoring` is in your PATH: `which nadzoring`
4. **Completion not registered** — run the activation command directly to see if there are any errors

**Debugging bash completions:**

```bash
# Enable debug output
set -x
nadzoring [TAB]
set +x
```

**Check if completion is registered:**

```bash
# Bash
complete -p | grep nadzoring
# Should output: complete -o nosort -F _nadzoring_completion nadzoring

# Zsh
echo $fpath | grep nadzoring
```

**Show installation hints:**

```bash
nadzoring completion hints bash      # For bash
nadzoring completion hints zsh       # For zsh
nadzoring completion hints fish      # For fish
nadzoring completion hints powershell  # For PowerShell
```

#### Completions Commands Reference

| Command | Description |
|---------|-------------|
| `nadzoring completion bash` | Generate bash completion script |
| `nadzoring completion zsh` | Generate zsh completion script |
| `nadzoring completion fish` | Generate fish completion script |
| `nadzoring completion powershell` | Generate PowerShell completion script |
| `nadzoring completion hints <shell>` | Show detailed installation hints |

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
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

```bash
# A record lookup
nadzoring dns resolve google.com

# Multiple record types
nadzoring dns resolve -t MX -t TXT -t A example.com

# All record types with a specific nameserver
nadzoring dns resolve -t ALL -n 8.8.8.8 github.com

# Show TTL values
nadzoring dns resolve --show-ttl --type A cloudflare.com

# Custom timeouts for slow networks
nadzoring dns resolve --connect-timeout 10 --read-timeout 20 example.com
```

**Python API:**

```python
from nadzoring.dns_lookup.utils import resolve_with_timer
from nadzoring.utils.timeout import TimeoutConfig

# Using default timeouts
result = resolve_with_timer("example.com", "A")
if result["error"]:
    # Possible values:
    # "Domain does not exist"  — NXDOMAIN
    # "No A records"           — record type not found
    # "Query timeout"          — nameserver did not respond
    print("DNS error:", result["error"])
else:
    print(result["records"])  # ['93.184.216.34']
    print(result["response_time"])  # milliseconds

# With TTL and custom nameserver
result = resolve_with_timer(
    "example.com",
    "MX",
    nameserver="8.8.8.8",
    include_ttl=True,
)
print(result["records"])  # ['10 mail.example.com']
print(result["ttl"])  # e.g. 3600

# Custom timeout configuration
config = TimeoutConfig(connect=3.0, read=8.0, lifetime=20.0)
result = resolve_with_timer("example.com", "A", timeout_config=config)
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
from nadzoring.utils.timeout import TimeoutConfig

# IPv4 reverse lookup
result = reverse_dns("8.8.8.8")
if result["error"]:
    # Possible values:
    # "No PTR record"          — IP has no reverse entry
    # "No reverse DNS"         — NXDOMAIN on reverse zone
    # "Query timeout"          — resolver timed out
    # "Invalid IP address: …"  — malformed input
    print("Lookup failed:", result["error"])
else:
    print(result["hostname"])  # 'dns.google'
    print(result["response_time"])  # milliseconds

# IPv6 reverse lookup
result = reverse_dns("2001:4860:4860::8888")
print(result["hostname"])  # 'dns.google'

# Compact error-safe pattern
hostname = result["hostname"] or f"[{result['error']}]"

# Custom nameserver and timeout
config = TimeoutConfig(connect=2.0, read=5.0)
result = reverse_dns("8.8.8.8", nameserver="1.1.1.1", timeout_config=config)
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
| `--validate-mx` | | Validate MX priority uniqueness | `False` |
| `--validate-txt` | | Validate SPF and DKIM TXT records | `False` |
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

```bash
# Full DNS check
nadzoring dns check example.com

# Check MX and TXT only with validation
nadzoring dns check -t MX -t TXT --validate-mx --validate-txt gmail.com

# Multiple domains
nadzoring dns check -n 9.9.9.9 google.com cloudflare.com
```

**Python API:**

```python
from nadzoring.dns_lookup.health import check_dns
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=3.0, read=10.0, lifetime=15.0)
result = check_dns(
    "example.com",
    record_types=["MX", "TXT"],
    validate_mx=True,
    validate_txt=True,
    timeout_config=config,
)
print(result["records"])  # {'MX': ['10 mail.example.com']}
print(result["errors"])  # {'AAAA': 'No AAAA records'} — only failed types
print(result["response_times"])  # per-type timing in ms
print(result["validations"])  # {'mx': {'valid': True, 'issues': [], 'warnings': []}}
```

---

#### dns trace

Trace the complete DNS resolution delegation chain from root to authoritative nameserver.

```bash
nadzoring dns trace [OPTIONS] DOMAIN
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--nameserver` | `-n` | Starting nameserver | root `198.41.0.4` |
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

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
if not result["differences"]:
    print("All servers agree")
else:
    for diff in result["differences"]:
        print(f"Server {diff['server']} — {diff['type']} mismatch")
        print(f"  Expected (baseline): {diff['expected']}")
        print(f"  Got:                 {diff['got']}")
        if diff["ttl_difference"] is not None:
            print(f"  TTL delta: {diff['ttl_difference']}s")
```

---

#### dns health

Perform a scored DNS health check across all standard record types.

```bash
nadzoring dns health [OPTIONS] DOMAIN
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--nameserver` | `-n` | Nameserver IP | System default |
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

Health score: **80–100** = Healthy · **50–79** = Degraded · **0–49** = Unhealthy

```bash
nadzoring dns health example.com
nadzoring dns health -n 1.1.1.1 google.com
nadzoring dns health -o json --save health.json example.com
```

**Python API:**

```python
from nadzoring.dns_lookup.health import health_check_dns
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=2.0, read=8.0)
result = health_check_dns("example.com", timeout_config=config)

print(f"Score: {result['score']}/100")
print(f"Status: {result['status']}")  # 'healthy' | 'degraded' | 'unhealthy'

for issue in result["issues"]:
    print("  CRITICAL:", issue)
for warn in result["warnings"]:
    print("  WARN:", warn)
for rtype, score in result["record_scores"].items():
    print(f"  {rtype}: {score}/100")
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
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

```bash
nadzoring dns benchmark
nadzoring dns benchmark -s 8.8.8.8 -s 1.1.1.1 -s 9.9.9.9 --queries 20
nadzoring dns benchmark -t MX -d gmail.com --sequential
nadzoring dns benchmark -o json --save benchmark.json
```

**Python API:**

```python
from nadzoring.dns_lookup.benchmark import benchmark_dns_servers, benchmark_single_server
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=2.0, read=8.0, lifetime=60.0)

# Single server
result = benchmark_single_server("8.8.8.8", queries=10, timeout_config=config)
print(f"avg={result['avg_response_time']:.1f}ms  success={result['success_rate']}%")

# Multiple servers — returned sorted fastest-first
results = benchmark_dns_servers(
    servers=["8.8.8.8", "1.1.1.1", "9.9.9.9"],
    queries=10,
    parallel=True,
    timeout_config=config,
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
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

Severity levels: `NONE` → `LOW` → `MEDIUM` → `HIGH` → `CRITICAL` / `SUSPICIOUS`

```bash
nadzoring dns poisoning example.com
nadzoring dns poisoning -c 1.1.1.1 -a MX -a TXT google.com
nadzoring dns poisoning -o html --save poisoning_report.html twitter.com
```

**Python API:**

```python
from nadzoring.dns_lookup.poisoning import check_dns_poisoning
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=3.0, read=10.0, lifetime=45.0)
result = check_dns_poisoning("example.com", timeout_config=config)

level = result.get("poisoning_level", "NONE")
confidence = result.get("confidence", 0.0)
print(f"Level: {level}  Confidence: {confidence:.0f}%")

if result.get("poisoned"):
    for inc in result.get("inconsistencies", []):
        print("Inconsistency:", inc)

if result.get("cdn_detected"):
    print(f"CDN: {result['cdn_owner']} ({result['cdn_percentage']:.0f}%)")
```

---

#### dns monitor

Continuously monitor DNS health and performance for a domain. Logs each cycle to a structured JSONL file and fires configurable alerts when response time or success rate thresholds are breached.

```bash
nadzoring dns monitor [OPTIONS] DOMAIN
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--nameservers` | `-n` | DNS server to monitor (repeatable) | `8.8.8.8`, `1.1.1.1` |
| `--interval` | `-i` | Seconds between monitoring cycles | `60` |
| `--type` | `-t` | Record type: A, AAAA, MX, NS, TXT | `A` |
| `--queries` | `-q` | Queries per server per cycle | `3` |
| `--max-rt` | | Alert threshold: max avg response time (ms) | `500` |
| `--min-success` | | Alert threshold: minimum success rate (0–1) | `0.95` |
| `--no-health` | | Skip DNS health check each cycle | `False` |
| `--log-file` | `-l` | JSONL file to append all cycle results to | None |
| `--cycles` | `-c` | Stop after N cycles (0 = indefinite) | `0` |
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

```bash
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
```

After Ctrl-C (or after `--cycles` completes), a statistical summary is printed automatically.

**Python API:**

```python
from nadzoring.dns_lookup.monitor import AlertEvent, DNSMonitor, MonitorConfig
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=2.0, read=8.0, lifetime=30.0)


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
    timeout_config=config,
)

monitor = DNSMonitor(config)
monitor.run()
print(monitor.report())
```

---

#### dns monitor-report

Analyse a JSONL log file produced by `dns monitor`.

```bash
nadzoring dns monitor-report [OPTIONS] LOG_FILE
```

| Option | Description |
|--------|-------------|
| `--server` | Filter statistics to a specific server IP |

```bash
nadzoring dns monitor-report dns_monitor.jsonl
nadzoring dns monitor-report dns_monitor.jsonl --server 8.8.8.8 -o json
```

**Python API:**

```python
from nadzoring.dns_lookup.monitor import load_log
from statistics import mean

cycles = load_log("dns_monitor.jsonl")

rts = [s["avg_response_time_ms"] for c in cycles for s in c["samples"] if s["avg_response_time_ms"] is not None]
alerts = [a for c in cycles for a in c.get("alerts", [])]

print(f"Cycles      : {len(cycles)}")
print(f"Avg RT (ms) : {mean(rts):.2f}")
print(f"Alerts      : {len(alerts)}")
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

print(ping_addr("8.8.8.8"))  # True
print(ping_addr("https://google.com"))  # True — URLs are normalised automatically
print(ping_addr("192.0.2.1"))  # False — unreachable

# Note: ICMP may be blocked by firewalls even for reachable hosts
```

---

#### http-ping

Measure HTTP/HTTPS response timing and inspect headers.

```bash
nadzoring network-base http-ping [OPTIONS] URLS...
```

| Option | Description | Default |
|--------|-------------|---------|
| `--timeout` | Request timeout (seconds) — sets both connect and read | `10.0` |
| `--connect-timeout` | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | Read timeout (seconds) | `10.0` |
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
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=2.0, read=10.0, lifetime=30.0)
result = http_ping("https://example.com", timeout_config=config, include_headers=True)

if result.error:
    print("HTTP probe failed:", result.error)
else:
    print(f"Status:  {result.status_code}")
    print(f"DNS:     {result.dns_ms} ms")
    print(f"TTFB:    {result.ttfb_ms} ms")
    print(f"Total:   {result.total_ms} ms")
    print(f"Size:    {result.content_length} bytes")
    if result.final_url:
        print(f"Redirect → {result.final_url}")
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
from nadzoring.utils.validators import resolve_hostname

ip = resolve_hostname("example.com")
if ip is None:
    print("Resolution failed")
else:
    print(ip)  # "93.184.216.34"

# Validate IP format before resolving
from nadzoring.utils.validators import validate_ip, validate_ipv4, validate_ipv6

validate_ip("8.8.8.8")  # True
validate_ipv4("::1")  # False
validate_ipv6("::1")  # True

# Get router/gateway IP
from nadzoring.network_base.router_ip import router_ip

gateway = router_ip()  # '192.168.1.1' on most home networks
gateway6 = router_ip(ipv6=True)
```

---

#### parse-url

Parse a URL into its components (scheme, hostname, port, path, query, fragment, etc.).

```bash
nadzoring network-base parse-url URLS...
```

```bash
nadzoring network-base parse-url https://example.com/path?q=1#section
nadzoring network-base parse-url "postgresql://user:pass@localhost:5432/db"
```

**Python API:**

```python
from nadzoring.network_base.parse_url import parse_url

result = parse_url("https://user:pass@example.com:8080/path?key=value#frag")
print(result["protocol"])  # 'https'
print(result["hostname"])  # 'example.com'
print(result["port"])  # 8080
print(result["username"])  # 'user'
print(result["password"])  # 'pass'
print(result["path"])  # '/path'
print(result["query_params"])  # [('key', 'value')]
print(result["fragment"])  # 'frag'
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

if not result:
    # Empty dict returned on failure (private IP, rate-limit, network error)
    print("Geolocation unavailable")
else:
    print(f"{result['city']}, {result['country']}")
    print(f"Coordinates: {result['lat']}, {result['lon']}")
```

> **Note:** ip-api.com rate-limits free callers to 45 requests per minute.
> Private/reserved IP addresses (e.g. `192.168.x.x`) return an empty dict.

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
print(info["IPv4 address"])  # '192.168.1.42'
print(info["Router ip-address"])  # '192.168.1.1'
print(info["MAC-address"])  # '00:11:22:33:44:55'
print(info["Public IP address"])  # your external IP
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
| `--timeout` | Socket timeout (seconds) — sets connect timeout | `2.0` |
| `--connect-timeout` | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | Read timeout (seconds) for banner grabbing | `10.0` |
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

**Python API:**

```python
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
```

---

#### detect-service

Actively connect to ports and detect actual running services by banner analysis.

```bash
nadzoring network-base detect-service [OPTIONS] TARGET PORTS...
```

| Option | Description | Default |
|--------|-------------|---------|
| `--timeout` | Connection timeout (seconds) — sets connect timeout | `3.0` |
| `--connect-timeout` | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | Read timeout (seconds) for banner | `10.0` |
| `--no-probe` | Disable sending protocol-specific probes | `False` |

```bash
# Detect services on common ports
nadzoring network-base detect-service example.com 80 443 22

# Database ports with longer timeout
nadzoring network-base detect-service --connect-timeout 5 192.168.1.100 3306 5432 6379
```

**Python API:**

```python
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

print(get_service_on_port(80))  # 'http'
print(get_service_on_port(443))  # 'https'
print(get_service_on_port(22))  # 'ssh'
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
print(result["registrar"])  # 'RESERVED-Internet Assigned Numbers Authority'
print(result["creation_date"])  # '1995-08-14T04:00:00Z'
print(result["expiry_date"])
print(result["name_servers"])
if result.get("error"):
    print("Error:", result["error"])  # whois not installed, lookup failed, etc.
```

---

#### domain-info

Retrieve comprehensive information about a domain in a single call. Aggregates WHOIS registration data, DNS record lookups (A, AAAA, MX, NS, TXT), IP geolocation for the primary resolved address, and reverse DNS — all returned as a structured response.

```bash
nadzoring network-base domain-info [OPTIONS] DOMAINS...
```

```bash
nadzoring network-base domain-info example.com
nadzoring network-base domain-info google.com github.com cloudflare.com
nadzoring network-base domain-info -o json --save domain_report.json example.com
```

**Python API:**

```python
from nadzoring.network_base.domain_info import get_domain_info

info = get_domain_info("example.com")

# WHOIS registration data
print(info["whois"]["registrar"])
print(info["whois"]["creation_date"])
print(info["whois"]["expiry_date"])

# Resolved IP addresses
print(info["dns"]["ipv4"])  # '93.184.216.34'
print(info["dns"]["ipv6"])  # '2606:2800:220:1:248:1893:25c8:1946'

# DNS records by type
for rtype, records in info["dns"]["records"].items():
    print(f"  {rtype}: {records}")

# Geolocation of the primary IP
geo = info["geolocation"]
if geo:
    print(f"{geo['city']}, {geo['country']}  ({geo['lat']}, {geo['lon']})")

# Reverse DNS for the primary IP
print(info["reverse_dns"])  # 'example.com' or None
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
| `--timeout` | Per-hop timeout (seconds) — sets connect timeout | `2.0` |
| `--connect-timeout` | Per-hop timeout (seconds) | `5.0` |
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
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=1.5, read=5.0)
hops = traceroute("8.8.8.8", max_hops=15, per_hop_timeout=config.connect)
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

### Security Commands

The `security` group provides SSL/TLS certificate inspection, HTTP security header auditing, email security record validation, subdomain discovery, and continuous certificate monitoring.

```bash
nadzoring security --help
```

---

#### security check-ssl

Inspect the SSL/TLS certificate for one or more domains. Checks expiry, issuer, subject, Subject Alternative Names, key strength, domain match, and which TLS protocol versions the server accepts (TLSv1.0 through TLSv1.3).

By default only a compact summary is shown. Use `--full` to see all fields including the complete SAN list, protocol details, chain length, and raw serial number.

```bash
nadzoring security check-ssl [OPTIONS] DOMAINS...
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--days-before` | `-d` | Days before expiry to flag as `warning` status | `7` |
| `--no-verify` | | Disable certificate chain verification (falls back automatically) | `False` |
| `--full` | | Show all certificate fields instead of compact summary | `False` |
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

**Status values:**

| Status | Meaning |
|--------|---------|
| `valid` | Certificate is valid and not near expiry |
| `warning` | Fewer than `--days-before` days remaining |
| `expired` | Certificate has already expired |
| `error` | Could not connect or parse the certificate |

```bash
# Basic check — compact summary table
nadzoring security check-ssl example.com

# Check multiple domains with a 30-day warning window
nadzoring security check-ssl --days-before 30 google.com github.com cloudflare.com

# Check without verifying the certificate chain (useful for self-signed certs)
nadzoring security check-ssl --no-verify internal.corp.example.com

# Full details including SAN list, protocol support, chain info
nadzoring security check-ssl --full ya.ru

# Save results as JSON for further processing
nadzoring security check-ssl -o json --save ssl_report.json example.com github.com
```

**Python API:**

```python
from nadzoring.security.check_website_ssl_cert import (
    check_ssl_certificate,
    check_ssl_expiry,
    check_ssl_expiry_with_fallback,
)
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=3.0, read=8.0)

# Verified check (full certificate chain validation)
result = check_ssl_certificate("example.com", days_before=14, timeout_config=config)

print(result["status"])  # 'valid' | 'warning' | 'expired' | 'error'
print(result["remaining_days"])  # e.g. 142
print(result["expiry_date"])  # '2025-10-15T12:00:00+00:00'
print(result["verification"])  # 'verified' | 'unverified' | 'failed'

# Subject and issuer dicts
print(result["subject"]["CN"])  # 'example.com'
print(result["issuer"]["CN"])  # 'DigiCert TLS RSA SHA256 2020 CA1'
print(result["issuer"]["O"])  # 'DigiCert Inc'

# Subject Alternative Names
for san in result.get("san", []):
    print(san)  # 'DNS:example.com', 'DNS:www.example.com', ...

# Domain matching
print(result["domain_match"])  # True
print(result["matched_names"])  # ['DNS:example.com']

# Public key info
key = result["public_key"]
print(key["algorithm"])  # 'RSA' | 'EC' | 'Ed25519' | ...
print(key.get("key_size"))  # 2048 (RSA/DSA)
print(key.get("curve"))  # 'secp256r1' (EC)
print(key["strength"])  # 'weak' | 'good' | 'strong'

# Protocol support (TLSv1.0 – TLSv1.3)
protos = result["protocols"]
print(protos["supported"])  # ['TLSv1.2', 'TLSv1.3']
print(protos["has_outdated"])  # False

# Chain info (only when verify=True)
print(result.get("chain_length"))  # 3
print(result.get("chain_valid"))  # True

# Simplified expiry-only check
result = check_ssl_expiry("example.com")

# Automatic fallback to unverified mode if chain check fails
result = check_ssl_expiry_with_fallback("self-signed.badssl.com")
print(result["verification"])  # 'unverified' when fallback was used
```

---

#### security check-headers

Analyse the HTTP security headers returned by one or more URLs. Checks for the presence of eleven recommended headers, flags deprecated headers (e.g. `X-XSS-Protection`), identifies information-leaking headers (e.g. `Server`, `X-Powered-By`), and produces a 0–100 coverage score.

```bash
nadzoring security check-headers [OPTIONS] URLS...
```

| Option | Description | Default |
|--------|-------------|---------|
| `--timeout` | Request timeout in seconds — sets both connect and read | `10.0` |
| `--connect-timeout` | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | Read timeout (seconds) | `10.0` |
| `--no-verify` | Disable SSL certificate verification | `False` |

**Checked security headers:**

| Header | Purpose |
|--------|---------|
| `Strict-Transport-Security` | Enforce HTTPS (HSTS) |
| `Content-Security-Policy` | Mitigate XSS and injection attacks |
| `X-Content-Type-Options` | Prevent MIME-type sniffing |
| `X-Frame-Options` | Prevent clickjacking |
| `X-XSS-Protection` | Legacy XSS filter (deprecated) |
| `Referrer-Policy` | Control referrer information leakage |
| `Permissions-Policy` | Restrict browser feature access |
| `Cross-Origin-Embedder-Policy` | Isolate cross-origin resources |
| `Cross-Origin-Opener-Policy` | Isolate browsing context |
| `Cross-Origin-Resource-Policy` | Control cross-origin resource sharing |
| `Cache-Control` | Prevent caching of sensitive responses |

```bash
# Check a single URL
nadzoring security check-headers https://example.com

# Check multiple URLs and save results
nadzoring security check-headers https://google.com https://github.com https://cloudflare.com

# Skip SSL verification for internal/self-signed endpoints
nadzoring security check-headers --no-verify https://internal.corp.example.com

# Export as JSON for CI integration or dashboards
nadzoring security check-headers -o json --save headers_audit.json https://example.com

# Adjust timeout for slow servers
nadzoring security check-headers --connect-timeout 20 https://slow-api.example.com
```

**Python API:**

```python
from nadzoring.security.http_headers import check_http_security_headers
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=5.0, read=15.0)
result = check_http_security_headers("https://example.com", timeout_config=config)

print(result["url"])  # final URL after redirects
print(result["status_code"])  # 200
print(result["score"])  # 0–100 coverage score

# Present security headers
for header, value in result["present"].items():
    print(f"  ✓ {header}: {value}")

# Missing security headers
for header in result["missing"]:
    print(f"  ✗ {header}")

# Deprecated headers found in the response
for header in result["deprecated"]:
    print(f"  ⚠ deprecated: {header}")

# Information-leaking headers
for header, value in result["leaking"].items():
    print(f"  ⚠ leaking: {header} = {value}")

if result["error"]:
    print("Request failed:", result["error"])
```

---

#### security check-email

Validate the email security configuration for one or more domains. Checks SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail) by probing common selectors, and DMARC (Domain-based Message Authentication, Reporting and Conformance). Returns structured findings including detected issues and an overall score.

> **Note:** Requires `dig` or `nslookup` to be available on the system, or `dnspython` installed in the Python environment (`pip install dnspython`). `dnspython` is preferred as it handles multi-chunk TXT records reliably.

```bash
nadzoring security check-email [OPTIONS] DOMAINS...
```

```bash
# Check a single domain
nadzoring security check-email gmail.com

# Check multiple domains at once
nadzoring security check-email google.com github.com cloudflare.com

# Export full JSON report
nadzoring security check-email -o json --save email_security.json example.com

# Quiet mode for scripting — results only, no progress bars
nadzoring security check-email --quiet example.com
```

**Python API:**

```python
from nadzoring.security.email_security import check_email_security

result = check_email_security("example.com")

print(result["domain"])

# Overall score: 0 = none of SPF/DKIM/DMARC found, 3 = all found
print(result["overall_score"])  # e.g. 3

# SPF analysis
spf = result["spf"]
print(spf["found"])  # True
print(spf["record"])  # 'v=spf1 include:_spf.example.com ~all'
print(spf["mechanisms"])  # ['include:_spf.example.com']
print(spf["all_qualifier"])  # '~'  (softfail — recommended minimum)
for issue in spf["issues"]:
    print("  SPF issue:", issue)

# DKIM analysis
dkim = result["dkim"]
print(dkim["found"])  # True
print(dkim["selectors_checked"])  # list of 13 common selectors probed
for selector, record in dkim["records"].items():
    print(f"  DKIM selector '{selector}': {record[:60]}...")
for issue in dkim["issues"]:
    print("  DKIM issue:", issue)

# DMARC analysis
dmarc = result["dmarc"]
print(dmarc["found"])  # True
print(dmarc["record"])  # 'v=DMARC1; p=reject; rua=mailto:...'
print(dmarc["policy"])  # 'none' | 'quarantine' | 'reject'
print(dmarc["subdomain_policy"])  # sp= tag value or None
print(dmarc["pct"])  # percentage of messages the policy applies to
print(dmarc["rua"])  # aggregate report addresses
print(dmarc["ruf"])  # forensic report addresses
for issue in dmarc["issues"]:
    print("  DMARC issue:", issue)

# All issues aggregated across SPF + DKIM + DMARC
for issue in result["all_issues"]:
    print("Issue:", issue)
```

**Common issues reported:**

| Category | Issue |
|----------|-------|
| SPF | No SPF record found |
| SPF | Multiple SPF records (RFC violation) |
| SPF | `+all` allows any sender (insecure) |
| SPF | Missing `all` mechanism |
| SPF | Exceeds 10 DNS lookup limit |
| DKIM | No DKIM records found for common selectors |
| DMARC | No DMARC record found |
| DMARC | Policy `p=none` does not protect against spoofing |
| DMARC | No aggregate report address (`rua=`) configured |
| DMARC | Policy applies to less than 100% of messages |

---

#### security subdomains

Discover subdomains for a target domain using two complementary methods: certificate transparency (CT) log queries via [crt.sh](https://crt.sh) and concurrent DNS brute-force using a built-in wordlist of 80+ common prefixes (or a custom wordlist file). Each result is tagged with its discovery source.

```bash
nadzoring security subdomains [OPTIONS] DOMAIN
```

| Option | Description | Default |
|--------|-------------|---------|
| `--wordlist` | Path to a custom wordlist file (one prefix per line) | Built-in 80+ prefix list |
| `--threads` | Number of concurrent DNS resolution threads | `20` |
| `--timeout` | Per-host DNS resolution timeout in seconds | `3.0` |
| `--connect-timeout` | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | Read timeout (seconds) | `10.0` |
| `--no-bruteforce` | Skip DNS brute-force entirely, use CT logs only | `False` |

```bash
# Discover subdomains using CT logs + built-in wordlist
nadzoring security subdomains example.com

# CT logs only — no brute-force DNS
nadzoring security subdomains --no-bruteforce example.com

# Use a custom wordlist file
nadzoring security subdomains --wordlist /path/to/subdomains.txt example.com

# Increase concurrency and timeout for faster / more thorough scanning
nadzoring security subdomains --threads 50 --connect-timeout 5 example.com

# Export results as JSON
nadzoring security subdomains -o json --save subdomains.json example.com

# Quiet mode for scripting
nadzoring security subdomains --quiet example.com
```

**Python API:**

```python
from nadzoring.security.subdomain_scan import scan_subdomains
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=2.0, read=8.0)

# CT logs + built-in wordlist brute-force
results = scan_subdomains("example.com", max_threads=20, timeout_config=config)

for r in results:
    print(f"{r['subdomain']:40}  {r['ip']:16}  [{r['source']}]")

# CT logs only
results = scan_subdomains("example.com", wordlist_path="")

# Custom wordlist
results = scan_subdomains(
    "example.com",
    wordlist_path="/path/to/custom_wordlist.txt",
    max_threads=50,
    timeout_config=config,
)

# Source values: 'ct_log' | 'brute_force'
ct_found = [r for r in results if r["source"] == "ct_log"]
brute_found = [r for r in results if r["source"] == "brute_force"]
print(f"CT log: {len(ct_found)}  Brute-force: {len(brute_found)}")
```

**Built-in wordlist includes prefixes for:**
common web services (`www`, `mail`, `ftp`, `smtp`), admin panels (`admin`, `portal`, `cpanel`, `whm`, `plesk`), APIs and apps (`api`, `app`, `dev`, `staging`, `test`, `beta`), infrastructure (`vpn`, `proxy`, `lb`, `waf`, `gateway`, `ns`, `ns1`, `ns2`), CDN and static assets (`cdn`, `static`, `assets`, `media`, `images`), DevOps tooling (`git`, `gitlab`, `jenkins`, `ci`, `cd`, `docker`, `k8s`, `grafana`, `kibana`), databases (`db`, `mysql`, `postgres`, `mongo`, `redis`, `elastic`), and more.

---

#### security watch-ssl

Continuously monitor SSL/TLS certificates for one or more domains. On each check cycle the certificate is re-fetched and alerts are fired for: near-expiry (`status == warning`), expired certificates, certificate changes (expiry date difference between consecutive checks), and check failures. Runs indefinitely until Ctrl-C or for a fixed number of cycles.

```bash
nadzoring security watch-ssl [OPTIONS] DOMAINS...
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--interval` | `-i` | Seconds between full check cycles | `3600` |
| `--cycles` | `-c` | Number of cycles to run (`0` = run indefinitely) | `0` |
| `--days-before` | `-d` | Days before expiry to trigger a warning alert | `7` |
| `--timeout` | | Lifetime timeout (seconds) | `30.0` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

```bash
# Monitor ya.ru indefinitely, check every hour
nadzoring security watch-ssl ya.ru

# Monitor multiple domains with a 14-day warning threshold
nadzoring security watch-ssl --days-before 14 example.com github.com cloudflare.com

# Run exactly 5 check cycles with a 60-second interval (useful for CI/testing)
nadzoring security watch-ssl --cycles 5 --interval 60 example.com

# Frequent checks — every 5 minutes — for a critical service
nadzoring security watch-ssl --interval 300 api.example.com

# Save all check results as JSON after monitoring ends
nadzoring security watch-ssl --cycles 3 -o json --save ssl_history.json example.com

# Quiet mode — suppress progress output, emit only alert lines
nadzoring security watch-ssl --quiet --cycles 10 --interval 30 example.com
```

**Alert events fired:**

| Trigger | Message example |
|---------|-----------------|
| Check failure | `Check failed: [Errno 111] Connection refused` |
| Expired certificate | `Certificate has EXPIRED` |
| Near expiry | `Certificate expires in 5 day(s)` |
| Certificate changed | `Certificate changed: expiry 2025-06-01 → 2025-12-01` |

**Python API:**

```python
from nadzoring.security.ssl_monitor import SSLMonitor
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=3.0, read=10.0)

# Create monitor for multiple domains
monitor = SSLMonitor(
    domains=["example.com", "github.com", "cloudflare.com"],
    interval=3600,  # seconds between cycles
    days_before=14,  # alert when fewer than 14 days remain
    timeout_config=config,
)


# Custom alert handler
def on_alert(domain: str, message: str) -> None:
    print(f"ALERT  {domain}: {message}")
    # send to Slack, PagerDuty, email, etc.


monitor.set_alert_callback(on_alert)

# Run a fixed number of cycles (blocking)
results = monitor.run_cycles(cycles=5)

# Or run indefinitely until KeyboardInterrupt
try:
    monitor.run()
except KeyboardInterrupt:
    pass

# Retrieve full history of all check results
for entry in monitor.history():
    print(entry["domain"], entry["status"], entry["remaining_days"], entry["checked_at"])
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
from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError

try:
    cache = ARPCache()
    entries = cache.get_cache()
except ARPCacheRetrievalError as exc:
    print("Cannot read ARP cache:", exc)
else:
    for entry in entries:
        print(f"{entry.ip_address}  {entry.mac_address or '(incomplete)'}  {entry.interface}  {entry.state.value}")
```

---

#### arp detect-spoofing

Statically detect ARP spoofing by analyzing the current ARP cache.

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
from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError
from nadzoring.arp.detector import ARPSpoofingDetector

try:
    cache = ARPCache()
    detector = ARPSpoofingDetector(cache)
    alerts = detector.detect()
except ARPCacheRetrievalError as exc:
    print("ARP cache error:", exc)
else:
    if not alerts:
        print("No spoofing detected")
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
| `--timeout` | `-t` | Capture timeout (seconds) — sets lifetime timeout | `30` |
| `--connect-timeout` | | Connection timeout (seconds) | `5.0` |
| `--read-timeout` | | Read timeout (seconds) | `10.0` |

```bash
nadzoring arp monitor-spoofing
nadzoring arp monitor-spoofing --interface eth0 --count 200 --timeout 60
nadzoring arp monitor-spoofing -o json --save arp_alerts.json
```

**Python API:**

```python
from nadzoring.arp.realtime import ARPRealtimeDetector
from nadzoring.utils.timeout import TimeoutConfig

config = TimeoutConfig(connect=2.0, read=8.0, lifetime=45.0)
detector = ARPRealtimeDetector()
alerts = detector.monitor(interface="eth0", count=100, timeout_config=config)
for alert in alerts:
    print(f"{alert['timestamp']}  {alert['message']}")
    print(f"  src_ip={alert['src_ip']}  src_mac={alert['src_mac']}")

# Get monitoring stats
stats = detector.get_stats()
print(f"Processed: {stats['packets_processed']}  Alerts: {stats['alerts_generated']}")


# Custom callback for integration with external systems
def on_packet(packet, alert):
    if alert:
        print("ALERT:", alert)  # integrate with your alerting pipeline here


detector.monitor(interface=None, count=0, timeout=0, packet_callback=on_packet)
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
| `yaml` | YAML format |

```bash
nadzoring dns resolve -o json example.com
nadzoring dns health -o html --save health.html example.com
nadzoring network-base connections -o csv --save conns.csv
nadzoring security check-ssl -o json example.com
nadzoring security check-headers -o json --save headers.json https://example.com
nadzoring security check-email -o json --save email_audit.json example.com
nadzoring security subdomains -o json --save subdomains.json example.com
```

## Saving Results

```bash
nadzoring dns check -o html --save dns_report.html example.com
nadzoring dns compare -o csv --save comparison.csv google.com
nadzoring dns poisoning -o json --save poisoning.json example.com
nadzoring network-base port-scan -o json --save scan.json example.com
nadzoring network-base domain-info -o json --save domain_info.json example.com
nadzoring security check-ssl -o json --save ssl_report.json example.com
nadzoring security check-headers -o json --save headers_report.json https://example.com
nadzoring security check-email -o json --save email_security.json example.com
nadzoring security subdomains -o json --save subdomains.json example.com
nadzoring arp cache -o csv --save arp.csv
```

## Logging Levels

| Mode | Flag | Behaviour |
|------|------|-----------|
| Normal | (none) | Warnings + progress bars |
| Verbose | `--verbose` | Debug logs + execution timing |
| Quiet | `--quiet` | Results only — ideal for scripting |

---

## Timeout Configuration

Nadzoring provides three timeout options that work together:

| Option | Description | Default | Fallback |
|--------|-------------|---------|----------|
| `--timeout` | Lifetime timeout for the entire operation | `30.0` | — |
| `--connect-timeout` | Timeout for establishing connections | `5.0` | Falls back to `--timeout` |
| `--read-timeout` | Timeout for read operations after connection | `10.0` | Falls back to `--timeout` |

**Resolution order per phase:**
1. Phase-specific option (`--connect-timeout` / `--read-timeout`)
2. Generic `--timeout`
3. Module default (shown above)

**Example:**
```bash
# All three phases have explicit timeouts
nadzoring dns resolve --timeout 60 --connect-timeout 5 --read-timeout 30 example.com

# Connect timeout inherits from generic timeout (30s), read uses default (10s)
nadzoring dns resolve --timeout 30 example.com

# Connect timeout = 3s, read timeout = 3s (both inherit from --timeout)
nadzoring dns resolve --timeout 3 example.com
```

**Python API `TimeoutConfig`:**
```python
from nadzoring.utils.timeout import TimeoutConfig, OperationTimeoutError, with_lifetime_timeout

# Create configuration
config = TimeoutConfig(
    connect=3.0,  # connection phase
    read=8.0,  # read operations
    lifetime=30.0,  # total operation limit
)

# Apply to a socket
sock = socket.socket()
config.apply_to_socket(sock)  # sets read timeout only

# Context manager for lifetime timeout
try:
    with timeout_context(config):
        result = long_running_operation()
except OperationTimeoutError:
    print("Operation exceeded lifetime timeout")


# Decorator for lifetime timeout
@with_lifetime_timeout(config)
def fetch_data():
    return expensive_network_operation()
```

---

## Error Handling

Every public Python API function follows a consistent error contract — functions never raise on expected DNS or network failures. All errors are returned as structured data so that scripts can handle them uniformly.

**DNS result-dict pattern** — check `result["error"]` before using `result["records"]`:

```python
from nadzoring.dns_lookup.utils import resolve_with_timer

result = resolve_with_timer("example.com", "A")
if result["error"]:
    # "Domain does not exist"  — NXDOMAIN
    # "No A records"           — record type not present
    # "Query timeout"          — nameserver did not respond
    print("DNS error:", result["error"])
else:
    print(result["records"])
    print(f"RTT: {result['response_time']} ms")
```

**Return-None / empty-dict pattern** — used where a result cannot be partially valid:

```python
from nadzoring.network_base.geolocation_ip import geo_ip

result = geo_ip("8.8.8.8")
if not result:
    print("Geolocation unavailable")
else:
    print(f"{result['city']}, {result['country']}")
```

**Timeout exceptions** — raised only when lifetime timeout is exceeded:

```python
from nadzoring.utils.timeout import OperationTimeoutError, timeout_context, TimeoutConfig

config = TimeoutConfig(lifetime=5.0)
try:
    with timeout_context(config):
        result = resolve_with_timer("example.com", "A")
except OperationTimeoutError:
    print("Operation exceeded 5 second lifetime limit")
```

**Exception pattern** — used only for system-level failures (missing commands, unsupported OS):

```python
from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError

try:
    cache = ARPCache()
    entries = cache.get_cache()
except ARPCacheRetrievalError as exc:
    print("Cannot read ARP cache:", exc)
```

All library exceptions inherit from `nadzoring.utils.errors.NadzoringError` and can be caught at any granularity:

```python
from nadzoring.utils.errors import NadzoringError, DNSError, NetworkError, ARPError
```

For a complete reference of all error patterns and possible error values, see the [Error Handling guide](https://alexeev-prog.github.io/nadzoring/main/error_handling.html) in the documentation.

---

## Python API

Nadzoring can be used as a Python library — all functionality is accessible programmatically without invoking the CLI.

### DNS Lookup API

```python
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
```

### Reverse DNS API

```python
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
```

### Security API

```python
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
```

### ARP API

```python
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

### SSL/TLS Certificate Auditing

```bash
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
```

### HTTP Security Header Auditing

```bash
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
```

### Email Security Validation

```bash
# Check a single domain
nadzoring security check-email example.com

# Audit multiple domains
nadzoring security check-email gmail.com outlook.com yahoo.com proton.me

# Export full JSON report with SPF/DKIM/DMARC details
nadzoring security check-email -o json --save email_audit.json example.com

# Check all your owned domains at once
nadzoring security check-email corp.example.com mail.example.com newsletter.example.com
```

### Subdomain Discovery

```bash
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
```

### Continuous SSL Monitoring

```bash
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
nadzoring network-base domain-info example.com
nadzoring network-base port-scan --mode fast example.com
nadzoring network-base traceroute cloudflare.com
nadzoring security check-ssl example.com
nadzoring security check-headers https://example.com
nadzoring security check-email example.com
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
Environment=DNS_CONNECT_TIMEOUT=5
Environment=DNS_READ_TIMEOUT=10
Environment=DNS_LIFETIME_TIMEOUT=30
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
```

**Finite cycles (CI pipelines, cron scripts):**

```python
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
```

**Analyse saved log:**

```python
from nadzoring.dns_lookup.monitor import load_log
from statistics import mean

cycles = load_log("dns_monitor.jsonl")
rts = [s["avg_response_time_ms"] for c in cycles for s in c["samples"] if s["avg_response_time_ms"] is not None]
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
nadzoring security check-ssl example.com
nadzoring security check-headers https://example.com
nadzoring security check-email example.com
nadzoring security subdomains example.com
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
- Extended security auditing (HSTS preload check, certificate transparency monitoring, CAA record validation)

---

## Documentation

| Version | Link | Status |
|---------|------|--------|
| **main** | [Latest (development)](https://alexeev-prog.github.io/nadzoring/main) | 🟡 Development |
| **v0.2.1** | [Release](https://alexeev-prog.github.io/nadzoring/v0.2.1) | 🟢 Stable |
| v0.2.0 | [Release](https://alexeev-prog.github.io/nadzoring/v0.2.0) | 🟢 Stable |
| v0.1.9 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.9) | ⚪ Legacy |
| v0.1.8 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.8) | ⚪ Legacy |
| v0.1.7 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.7) | ⚪ Legacy |
| v0.1.6 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.6) | ⚪ Legacy |
| v0.1.5 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.5) | ⚪ Legacy |
| v0.1.4 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.4) | ⚪ Legacy |
| v0.1.3 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.3) | ⚪ Legacy |
| v0.1.2 | [Legacy](https://alexeev-prog.github.io/nadzoring/v0.1.2) | ⚪ Legacy |
| v0.1.1 | [First version](https://alexeev-prog.github.io/nadzoring/v0.1.1) | ⚪ Legacy |

The documentation site includes (examples for `main`):
- [Error Handling guide](https://alexeev-prog.github.io/nadzoring/main/error_handling.html) — complete reference of all error patterns and return values
- [Architecture overview](https://alexeev-prog.github.io/nadzoring/main/architecture.html) — layer design, SRP/DRY/KISS principles applied
- [DNS command reference](https://alexeev-prog.github.io/nadzoring/main/commands/dns.html) — full CLI + Python API per command
- [Security command reference](https://alexeev-prog.github.io/nadzoring/main/commands/security.html) — SSL, headers, email, subdomains, monitoring
- [DNS monitoring guide](https://alexeev-prog.github.io/nadzoring/main/monitoring_dns.html) — systemd, cron, trend analysis

---

## License & Support

This project is licensed under the **GNU GPL v3 License** — see [LICENSE](https://github.com/alexeev-prog/nadzoring/blob/main/LICENSE) for details.

For commercial support or enterprise features, contact [alexeev.dev@mail.ru](mailto:alexeev.dev@mail.ru).

[📖 Explore Docs](https://alexeev-prog.github.io/nadzoring) · [🐛 Report Issue](https://github.com/alexeev-prog/nadzoring/issues)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
Copyright © 2025 Alexeev Bronislav. Distributed under GNU GPL v3 license.
