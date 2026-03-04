# Contributing to Nadzoring

Thank you for your interest in contributing! Please read this guide carefully before submitting anything.

---

## Table of Contents

- [Contributing to Nadzoring](#contributing-to-nadzoring)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [Reporting Issues](#reporting-issues)
  - [Feature Requests](#feature-requests)
  - [Development Setup](#development-setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running Tests](#running-tests)
    - [Linting \& Formatting](#linting--formatting)
  - [Code Style](#code-style)
    - [Python Version \& Typing](#python-version--typing)
    - [Docstrings](#docstrings)
    - [Keyword-Only Arguments](#keyword-only-arguments)
    - [Dataclasses](#dataclasses)
    - [Logging](#logging)
    - [Error Handling](#error-handling)
    - [`noqa` Comments](#noqa-comments)
    - [CLI Commands](#cli-commands)
    - [Module Structure](#module-structure)
  - [Writing Tests](#writing-tests)
  - [Pull Request Guidelines](#pull-request-guidelines)
  - [Review Process](#review-process)
  - [License](#license)

---

## Code of Conduct

All contributors must adhere to our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Please read it before participating.

---

## Reporting Issues

- Search existing issues before opening a new one
- Include your Python version, OS, and full error output
- Provide minimal reproduction steps

---

## Feature Requests

- Clearly describe the problem and your proposed solution
- Include concrete use cases
- Mention alternatives you considered

---

## Development Setup

### Prerequisites

- Python **3.12+**
- [`uv`](https://github.com/astral-sh/uv) (strongly recommended over pip)

### Installation

```bash
git clone https://github.com/alexeev-prog/nadzoring.git
cd nadzoring

uv venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows

uv sync
```

### Running Tests

```bash
pytest --cov=nadzoring --cov-report=term-missing
```

100% test coverage is required for all new code.

### Linting & Formatting

```bash
# Lint with ruff
ruff check src/nadzoring
```

Both must pass with no errors before submitting a PR. Zero-warning policy.

---

## Code Style

The codebase follows strict conventions — study the existing source before writing new code.

### Python Version & Typing

- Target **Python 3.12+**
- Use modern union syntax everywhere: `str | None`, not `Optional[str]`
- Annotate **all** function parameters and return types, including `-> None`
- Use built-in generics: `list[str]`, `dict[str, Any]`, `tuple[str, ...]` — not `List`, `Dict`, `Tuple` from `typing`

```python
# ✅ correct
def resolve_hostname(hostname: str) -> str | None: ...

# ❌ wrong
from typing import Optional
def resolve_hostname(hostname: str) -> Optional[str]: ...
```

### Docstrings

All public functions, classes, and modules must have docstrings. Use Google-style with `Args:`, `Returns:`, and `Examples:` sections:

```python
def traceroute(
    target: str,
    *,
    max_hops: int = 30,
    timeout: float = 5.0,
) -> list[TraceHop]:
    """
    Perform a traceroute to the specified target host.

    Uses 'traceroute' (with 'tracepath' fallback) on Linux and 'tracert'
    on Windows. Results include per-hop RTT measurements.

    Args:
        target: Hostname or IP address to trace.
        max_hops: Maximum number of hops before stopping. Defaults to 30.
        timeout: Per-hop timeout in seconds. Defaults to 5.0.

    Returns:
        List of TraceHop objects. Unreachable hops have None values for
        host/ip and rtt_ms contains [None].

    Examples:
        >>> hops = traceroute("8.8.8.8", max_hops=10)
        >>> hops[0].hop
        1

    """
```

### Keyword-Only Arguments

Boolean flags and optional parameters must be keyword-only (after `*`):

```python
# ✅ correct
def run(target: str, *, max_hops: int = 30, timeout: float = 5.0) -> list[TraceHop]: ...

# ❌ wrong
def run(target: str, max_hops: int = 30, timeout: float = 5.0) -> list[TraceHop]: ...
```

### Dataclasses

Use `@dataclass` for structured data. Use `field(default_factory=...)` for mutable defaults:

```python
@dataclass
class TraceHop:
    """Represents a single hop in a traceroute."""

    hop: int
    host: str | None
    ip: str | None
    rtt_ms: list[float | None] = field(default_factory=list)
```

### Logging

Use the project logger, never `print()` for internal output:

```python
from logging import Logger
from nadzoring.logger import get_logger

logger: Logger = get_logger(__name__)

logger.warning("Unsupported OS for traceroute: %s", os_name)
logger.exception("traceroute timed out for %s", target)
```

### Error Handling

- Use `logger.exception(...)` inside `except` blocks — it automatically captures the traceback
- Never swallow exceptions silently; always log or re-raise
- Return empty collections (`[]`) rather than `None` for failed operations that return lists

```python
try:
    raw = check_output("ip route", shell=True, stderr=PIPE).decode(errors="replace")
except (CalledProcessError, FileNotFoundError):
    logger.exception("Failed to retrieve routing table on Linux")
    return []
```

### `noqa` Comments

Suppress ruff rules only where unavoidable, always with an inline comment explaining the rule code:

```python
raw = check_output(  # noqa: S602
    "ip route",     # noqa: S607
    shell=True,
    stderr=PIPE,
)
```

### CLI Commands

All CLI commands use the `@common_cli_options` decorator from `nadzoring.utils.decorators`. Commands return plain `list[dict]` — formatting and saving are handled by the decorator automatically:

```python
@dns.command(name="resolve")
@common_cli_options(include_quiet=True)
@click.argument("domains", nargs=-1, required=True)
def resolve_command(
    domains: tuple[str, ...],
    *,
    quiet: bool,
) -> list[dict]:
    """Resolve DNS records for one or more domains."""
    ...
    return results
```

- Never call `click.echo` for result data inside commands — only use it for progress hints to `err=True`
- Use `tqdm` for progress bars; respect the `quiet` flag to suppress them
- Pass `progress_callback` into library functions rather than coupling tqdm to business logic

### Module Structure

Each module must start with a one-line module docstring:

```python
"""DNS-related CLI commands."""
```

Group imports in standard order (stdlib → third-party → local), separated by blank lines. Use `from __future__ import annotations` only if needed for forward references — the project targets 3.12 where it is rarely necessary.

---

## Writing Tests

- Cover all new functions and branches
- Use `pytest`; no `unittest` classes
- Mock external calls (DNS, subprocesses, network) — tests must not make real network requests
- Name tests descriptively: `test_parse_linux_ip_route_timeout_hop`, not `test_parse`

---

## Pull Request Guidelines

1. Fork the repository and create a branch: `git checkout -b feature/your-feature`
2. Implement your changes following the code style above
3. Add tests — 100% coverage required
4. Run `ruff check` and `black .` — both must be clean
5. Commit with clear, atomic messages: `fix: handle tracepath fallback on missing traceroute`
6. Open a PR and reference any related issues

---

## Review Process

- Maintainers aim to review within **3 business days**
- Be responsive to requested changes
- All CI checks (lint, tests, coverage) must pass before merge

---

## License

By contributing, you agree your contributions will be licensed under the project's **GNU GPL v3** license.
