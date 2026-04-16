<a id="readme-top"></a>

<div align="center">
  <p align="center">
    <img src="https://raw.githubusercontent.com/alexeev-prog/nadzoring/refs/heads/main/docs/nadzoring-long-preview.png">
    <p>An open source tool and python library for detecting website blocks, downdetecting and network analysis</p>
    <a href="https://alexeev-prog.github.io/nadzoring/v0.2.1"><strong>Explore the docs »</strong></a>
  </p>
  <p align="center">
    <a href="#-getting-started">Getting Started</a>
    ·
    <a href="#-basic-usage">Basic Usage</a>
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
    <a href='https://coveralls.io/github/alexeev-prog/nadzoring?branch=main'><img src='https://coveralls.io/repos/github/alexeev-prog/nadzoring/badge.svg?branch=main' alt='Coverage' /></a>
    <img src="https://img.shields.io/coderabbit/prs/github/alexeev-prog/nadzoring?utm_source=oss&utm_medium=github&utm_campaign=alexeev-prog%2Fnadzoring&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews" alt="CodeRabbit Pull Request Reviews">
    <img src="https://sloc.xyz/github/mutating/suby/?category=code" alt="Code lines">
    <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="MyPy Badge">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="ruff badge">
</p>

## Table of Contents

- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running with Docker](#running-with-docker)
  - [Basic Usage](#basic-usage)
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
  - [Documentation](#documentation)
  - [Contributing](#contributing)
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

## Basic Usage

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

**Quick examples:**

```bash
# Resolve a hostname to IP
nadzoring network-base host-to-ip example.com

# Comprehensive domain information
nadzoring network-base domain-info example.com

# Reverse DNS lookup
nadzoring dns reverse 8.8.8.8

# Full DNS health check
nadzoring dns health example.com

# Detect DNS poisoning
nadzoring dns poisoning example.com

# Check SSL/TLS certificate
nadzoring security check-ssl example.com

# Real-time ARP spoofing monitor
nadzoring arp monitor-spoofing --interface eth0
```

For complete command reference, Python API documentation, and advanced examples, see the **[full documentation](https://alexeev-prog.github.io/nadzoring/main)**.

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

The documentation site includes:
- [Complete CLI Command Reference](https://alexeev-prog.github.io/nadzoring/main/commands/all_commands.html) — all commands with options
- [Python API Examples](https://alexeev-prog.github.io/nadzoring/main/api_examples.html) — practical API usage
- [Code Examples](https://alexeev-prog.github.io/nadzoring/main/code_examples.html) — real-world scenarios
- [Error Handling guide](https://alexeev-prog.github.io/nadzoring/main/error_handling.html) — complete reference of all error patterns and return values
- [Architecture overview](https://alexeev-prog.github.io/nadzoring/main/architecture.html) — layer design, SRP/DRY/KISS principles applied
- [DNS monitoring guide](https://alexeev-prog.github.io/nadzoring/main/monitoring_dns.html) — systemd, cron, trend analysis

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

## License & Support

This project is licensed under the **GNU GPL v3 License** — see [LICENSE](https://github.com/alexeev-prog/nadzoring/blob/main/LICENSE) for details.

For commercial support or enterprise features, contact [alexeev.dev@mail.ru](mailto:alexeev.dev@mail.ru).

[📖 Explore Docs](https://alexeev-prog.github.io/nadzoring) · [🐛 Report Issue](https://github.com/alexeev-prog/nadzoring/issues)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
Copyright © 2025 Alexeev Bronislav. Distributed under GNU GPL v3 license.
