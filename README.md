# nadzoring

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
    <a href="https://alexeev-prog.github.io/nadzoring/">Documentation</a>
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
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/nadzoring?style=for-the-badge">
    <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/alexeev-prog/nadzoring?style=for-the-badge">
</p>
<p align="center">
    <img src="https://raw.githubusercontent.com/alexeev-prog/nadzoring/refs/heads/main/docs/pallet-0.png">
</p>

Nadzoring (from Russian "надзор" - supervision/oversight + English "-ing" suffix) is a FOSS (Free and Open Source Software) command-line tool for detecting website blocks, monitoring service availability, and network analysis. It helps you investigate network connectivity issues, check if websites are accessible, and analyze network configurations.

## 📋 Table of Contents
- [nadzoring](#nadzoring)
  - [📋 Table of Contents](#-table-of-contents)
  - [🚀 Installation](#-installation)
  - [💻 Usage](#-usage)
    - [Global Options](#global-options)
    - [Commands](#commands)
      - [Network Base Commands](#network-base-commands)
        - [ping-address](#ping-address)
        - [get-network-params](#get-network-params)
        - [get-ip-by-hostname](#get-ip-by-hostname)
        - [get-service-by-port](#get-service-by-port)
  - [📊 Output Formats](#-output-formats)
    - [Table Format (default)](#table-format-default)
    - [JSON Format](#json-format)
    - [CSV Format](#csv-format)
  - [💾 Saving Results](#-saving-results)
  - [📝 Logging Levels](#-logging-levels)
  - [🔍 Examples](#-examples)
    - [Complete Network Diagnostics](#complete-network-diagnostics)
    - [Automated Monitoring Script](#automated-monitoring-script)
    - [Quick Website Block Check](#quick-website-block-check)
  - [Contributing](#contributing)
  - [License \& Support](#license--support)

## 🚀 Installation

```bash
pip install nadzoring
```

## 💻 Usage

Nadzoring uses a hierarchical command structure. All commands support common global options for output formatting and logging.

### Global Options

These options are available for **all** commands:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Enable verbose output | `False` |
| `--quiet` | `-q` | Suppress non-error output | `False` |
| `--no-color` | - | Disable colored output | `False` |
| `--output` | `-o` | Output format (`table`, `json`, `csv`) | `table` |
| `--save` | - | Save results to file (provide filename) | None |

### Commands

#### Network Base Commands

The `network-base` group contains commands for basic network operations.

##### ping-address

Ping one or more addresses to check if they're reachable.

**Syntax:**
```bash
nadzoring network-base ping-address [OPTIONS] ADDRESSES...
```

**Arguments:**
- `ADDRESSES...` - One or more IP addresses or hostnames to ping (required)

**Default behavior:**
- Returns a table with columns: `Address` and `IsPinged`
- "yes" (green) = host is reachable
- "no" (red) = host is unreachable

**Examples:**
```bash
# Ping a single address
nadzoring network-base ping-address 8.8.8.8

# Ping multiple addresses
nadzoring network-base ping-address google.com cloudflare.com 1.1.1.1

# Ping with JSON output
nadzoring network-base ping-address -o json github.com

# Ping and save results
nadzoring network-base ping-address -o csv --save results.csv 8.8.8.8 1.1.1.1
```

##### get-network-params

Display detailed network configuration parameters of your system.

**Syntax:**
```bash
nadzoring network-base get-network-params [OPTIONS]
```

**Default behavior:**
- Returns a table with network interface information, IP addresses, and other network parameters

**Examples:**
```bash
# Basic network params display
nadzoring network-base get-network-params

# Get network params in JSON format
nadzoring network-base get-network-params -o json

# Save network params to file with verbose logging
nadzoring network-base get-network-params -v --save network_config.json
```

##### get-ip-by-hostname

Resolve hostnames to IP addresses and check IPv4/IPv6 availability.

**Syntax:**
```bash
nadzoring network-base get-ip-by-hostname [OPTIONS] HOSTNAMES...
```

**Arguments:**
- `HOSTNAMES...` - One or more domain names to resolve (required)

**Output columns:**
- `Hostname` - The original hostname
- `IP Address` - Resolved IP address
- `IPv4 Check` - "passed"/"failed" for IPv4 connectivity
- `IPv6 Check` - "passed"/"failed" for IPv6 connectivity
- `Router IPv4` - Your router's IPv4 address (or "Not found")
- `Router IPv6` - Your router's IPv6 address (or "Not found")

**Examples:**
```bash
# Resolve a single hostname
nadzoring network-base get-ip-by-hostname google.com

# Resolve multiple hostnames
nadzoring network-base get-ip-by-hostname google.com github.com stackoverflow.com

# Quiet mode - only show results
nadzoring network-base get-ip-by-hostname -q example.com

# Save results as CSV
nadzoring network-base get-ip-by-hostname --save dns_results.csv google.com cloudflare.com
```

##### get-service-by-port

Identify which service typically runs on specified ports.

**Syntax:**
```bash
nadzoring network-base get-service-by-port [OPTIONS] PORTS...
```

**Arguments:**
- `PORTS...` - One or more port numbers to check (required)

**Output columns:**
- `port` - The port number
- `service` - Service name (or "Unknown" if not recognized)

**Examples:**
```bash
# Check common ports
nadzoring network-base get-service-by-port 80 443 22 53

# Check a range of ports (using shell expansion)
nadzoring network-base get-service-by-port 20 21 22 23 25 80 443

# JSON output for programmatic use
nadzoring network-base get-service-by-port -o json 3306 5432 27017

# Save service information
nadzoring network-base get-service-by-port --save services.csv 80 443 22 3389
```

## 📊 Output Formats

Nadzoring supports three output formats controlled by the `-o/--output` flag:

### Table Format (default)
```
┌─────────────┬────────────┐
│ Address     │ IsPinged   │
├─────────────┼────────────┤
│ 8.8.8.8     │ yes        │
│ 1.1.1.1     │ yes        │
│ unreachable │ no         │
└─────────────┴────────────┘
```

### JSON Format
```json
[
  {
    "Address": "8.8.8.8",
    "IsPinged": "yes"
  },
  {
    "Address": "1.1.1.1",
    "IsPinged": "yes"
  }
]
```

### CSV Format
```csv
Address,IsPinged
8.8.8.8,yes
1.1.1.1,yes
```

## 💾 Saving Results

Use the `--save` option to save command output to a file. The format is determined by the `-o/--output` flag:

```bash
# Save as JSON
nadzoring network-base ping-address -o json --save ping_results.json 8.8.8.8

# Save as CSV
nadzoring network-base ping-address -o csv --save ping_results.csv 8.8.8.8

# Save as formatted table
nadzoring network-base ping-address -o table --save ping_results.txt 8.8.8.8
```

## 📝 Logging Levels

Nadzoring provides three logging modes:

- **Normal mode** (no flags): Shows command output and warnings
- **Verbose mode** (`-v/--verbose`): Shows detailed execution information including timing
- **Quiet mode** (`-q/--quiet`): Suppresses all non-error output

## 🔍 Examples

### Complete Network Diagnostics
```bash
# Run comprehensive network diagnostics
nadzoring network-base get-network-params -v
nadzoring network-base get-ip-by-hostname google.com cloudflare.com github.com
nadzoring network-base ping-address 8.8.8.8 1.1.1.1 google.com
nadzoring network-base get-service-by-port 80 443 22 53
```

### Automated Monitoring Script
```bash
#!/bin/bash
# Check critical services and save results with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

nadzoring network-base ping-address \
  -o csv \
  --save "ping_check_${TIMESTAMP}.csv" \
  google.com cloudflare.com github.com

nadzoring network-base get-service-by-port \
  -o json \
  --save "services_${TIMESTAMP}.json" \
  80 443 22 53 3306
```

### Quick Website Block Check
```bash
# Check if a website might be blocked
nadzoring network-base get-ip-by-hostname example.com
nadzoring network-base ping-address example.com
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Key areas for contribution include:
- Additional test cases for thread-local scenarios
- Performance optimization proposals
- Extended version format support
- IDE integration plugins

## License & Support

This project is licensed under **GNU LGPL 2.1 License** - see [LICENSE](https://github.com/alexeev-prog/nadzoring/blob/main/LICENSE). For commercial support and enterprise features, contact [alexeev.dev@mail.ru](mailto:alexeev.dev@mail.ru).

[Explore Documentation](https://alexeev-prog.github.io/nadzoring) |
[Report Issue](https://github.com/alexeev-prog/nadzoring/issues) |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
Copyright © 2025 Alexeev Bronislav. Distributed under GNU GPL v3 license.

