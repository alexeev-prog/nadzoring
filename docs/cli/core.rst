Package management and diagnostics (core)
============================================

All ``core`` commands support ``--format table|json|yaml`` (also
``--output``/``-o``), ``--save``, ``--quiet`` and ``--no-color``. The last
two flags may also precede the subcommand. Quiet mode suppresses logging,
not result data. No command elevates privileges.

Commands
--------

.. code-block:: console

   nadzoring core doctor --format json
   nadzoring core check-deps --strict
   nadzoring core check-permissions --verbose
   nadzoring core check-network --target pypi.org --timeout 15
   nadzoring core version --check
   nadzoring core changelog --version 0.2.2
   nadzoring core update --dry-run --installer pip
   nadzoring core update --yes --installer uv

``doctor`` aggregates Python compatibility, dependencies, permissions, network
and optional ``ping``, ``traceroute``, ``whois`` and ``uv`` availability. Its
summary gives the fraction and percentage of successful observations.
Missing optional tools and raw-socket privileges are recoverable warnings.

``check-deps`` validates installed distribution requirements generated from
``pyproject.toml``. It works outside a source checkout and handles version
constraints, environment markers, transitive requirements and requested
dependency extras. Missing/incompatible versions are errors. Unrelated
packages, including development tools, are informational unless ``--strict``
is supplied, when they become warnings. Optional application extras are not
required. This checks compatibility, not each dependency's latest release.

``check-permissions`` probes config/cache directories (XDG on Linux, Library
on macOS, APPDATA/LOCALAPPDATA on Windows), or their nearest existing parent.
It uses automatically removed temporary write probes and does not create
missing application directories. It also checks interpreter executability
and TCP/raw ICMP socket creation. ``--verbose`` includes directory paths.

``check-network`` accepts hostnames and IPv4/IPv6 literals, not URLs. It
checks DNS (not needed for IP literals), certificate-verified HTTPS on port
443 and optional ICMP, reporting latency in milliseconds. An IP address such
as 8.8.8.8 may answer ICMP but fail HTTPS certificate verification; that is
not evidence that all networking is unavailable. ICMP filtering or missing
permissions produce warnings, while DNS/HTTPS failures are errors.

Network commands accept ``--timeout``, ``--connect-timeout`` and
``--read-timeout``. Phase-specific values override ``--timeout``. Lifetime
enforcement uses the existing ``timeout_context`` implementation (SIGALRM on
Unix, underlying call timeouts on Windows). ``doctor`` applies the network
lifetime to its network checks.

Release information and updates
-------------------------------

``version`` is offline unless ``--check`` is supplied, which compares the
installed version with PyPI using PEP 440 ordering. ``changelog`` defaults
to the installed version, preferring GitHub Releases and falling back to
the matching section of ``CHANGELOG.md`` via the GitHub Contents API.
Successful API objects are cached for one hour in the native application
cache. Corrupt, expired or future-dated entries are ignored. Writes are
atomic and best-effort; an unwritable cache does not hide fresh results.

``update`` prefers ``uv`` when available, otherwise ``python -m pip``.
``--installer pip|uv|auto`` selects explicitly. Both paths target the running
interpreter, never use a shell and never elevate privileges. Actual updates
require ``--yes``. ``--dry-run`` reports the exact JSON-encoded argument vector
without running a subprocess. Failures and timeouts are errors; rollback is
not supported. Externally managed environments, uv tool installations or
project-managed environments may require their original management command
instead if this scoped installer refuses to update them.

Machine-readable schema
-----------------------

JSON/YAML output is an array with the following fields on every row:

.. code-block:: json

   [{"check": "version", "status": "ok", "detail": "0.3.0", "error": null}]

``check`` and ``detail`` are strings. ``status`` is ``ok``, ``warning``,
``error`` or ``update-available``. ``error`` contains a string for warnings
and errors, otherwise null. Parse ``check``/``status``, not the human-readable
``detail``. Verbose machine output remains valid JSON/YAML.

Exit codes: 0 = OK, 1 = recoverable warning, 2 = blocking error (or invalid
usage), 3 = update available. Errors take precedence over warnings, which
take precedence over update notifications. Results are emitted before exit.

Completion
----------

Existing ``nadzoring completion bash|zsh|fish|powershell`` scripts and the
interactive shell discover these commands from the command tree. No static
completion lists need regeneration.
