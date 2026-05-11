Architecture
============

Nadzoring is structured in concentric layers following the principles of
**Clean Architecture**, **Single Responsibility (SRP)**, **DRY**, and
**KISS**.  This page explains the layout so that contributors and
integrators know where each concern lives.

----

Package Layout
--------------

.. code-block:: text

   src/nadzoring/
   ├── cli.py                    # Entry-point: registers command groups
   ├── __main__.py               # python -m nadzoring
   │
   ├── commands/                 # CLI layer — Click command groups
   │   ├── dns_commands.py       #   dns group
   │   ├── network_commands.py   #   network-base group
   │   ├── security_commands.py  #   security group
   │   └── arp_commands.py       #   arp group
   │
   ├── dns_lookup/               # Domain layer — DNS
   │
   ├── network_base/             # Domain layer — network diagnostics
   │
   ├── security/                 # Domain layer — security auditing
   │
   ├── arp/                      # Domain layer — ARP security
   │
   ├── plugins/                  # Connector framework (non-CLI integrations)
   │
   └── utils/                    # Cross-cutting utilities
       ├── errors.py             #   Exception hierarchy
       ├── validators.py         #   Input validation functions
       ├── formatters.py         #   Output formatting (table/json/csv/html)
       └── decorators.py         #   @common_cli_options decorator

----

Layer Responsibilities
-----------------------

**CLI layer** (``commands/``)
    Owns *only* Click option parsing, progress bars, and output dispatch.
    Must not contain business logic.  Calls domain-layer functions and
    passes results to formatters.

**Domain layer** (``dns_lookup/``, ``network_base/``, ``security/``, ``arp/``)
    Contains all business logic.  Modules are scoped to a single concern
    (SRP).  Functions return typed dicts or dataclasses; they never print
    or call Click.

**Integrations** (``plugins/``)
    Optional connector classes for Python embedders (monitoring, tests).
    They wrap domain functions and return :class:`nadzoring.plugins.result.ProbeResult`
    objects.  The stock CLI does not depend on this package.

**Cross-cutting** (``utils/``)
    Shared helpers with no dependency on domain modules.  ``errors.py``
    defines the exception hierarchy.  ``validators.py`` contains pure
    functions.  ``formatters.py`` knows only about Python built-ins.

----

Design Principles Applied
--------------------------

SRP — Single Responsibility Principle
    Each module owns exactly one concern.  ``validation.py`` validates
    records; ``health.py`` scores them; ``utils.py`` resolves queries.
    ``check_website_ssl_cert.py`` handles only SSL certificate inspection;
    ``http_headers.py`` handles only header analysis; ``email_security.py``
    handles only SPF/DKIM/DMARC.  Formatting lives in
    ``utils/formatters.py``, not in domain modules.

DRY — Don't Repeat Yourself
    - Empty result dicts are built by factory helpers (``_make_empty_result``,
      ``_make_result``).
    - Record extraction is dispatched through a ``_EXTRACTORS`` map instead
      of a long ``if/elif`` chain.
    - CLI options are injected via the ``@common_cli_options`` decorator.
    - DNS TXT record querying in ``email_security.py`` is abstracted behind
      ``_query_txt()``, which tries ``dnspython``, then ``dig``, then
      ``nslookup`` automatically.

KISS — Keep It Simple
    Complex operations (trace, poisoning detection, subdomain scanning) are
    broken into small private functions with a single clear name.  Public
    functions have one entry point with documented parameters and return
    values.

Error handling
    Domain functions never raise on expected failures (DNS errors, network
    timeouts, missing PTR records, SSL connection errors).  All failures are
    returned as structured data so that CLI and scripting callers can handle
    them uniformly.  Only truly unexpected errors (programming mistakes,
    missing system commands) are allowed to propagate as exceptions.

----

Data Flow
---------

.. code-block:: text

   User / Script
        │
        ▼
   CLI layer (commands/)
        │  Click parses args
        │
        ▼
   Domain layer (dns_lookup / network_base / security / arp)
        │  Business logic, structured results
        │
        ▼
   External systems
        │  dnspython, ping3, requests, scapy, ssl, socket,
        │  system commands (dig, nslookup, whois, traceroute)
        │
        ▼
   Results bubble back up
        │
        ▼
   utils/formatters.py
        │  table / json / csv / html
        │
        ▼
   stdout / file

----

Security Module Data Flow
--------------------------

The ``security/`` domain package follows the same pattern with additional
external dependencies:

.. code-block:: text

   nadzoring security check-ssl example.com
        │
        ▼
   security_commands.py          # parses --days-before, --full, --no-verify
        │
        ▼
   security/check_website_ssl_cert.py
        │  ssl.create_default_context()
        │  socket connection → TLS handshake → certificate parsing
        │  _probe_tls_version() per TLS version (TLSv1.0–TLSv1.3)
        │
        ▼
   Structured result dict → formatters.py → stdout / file

   nadzoring security check-email example.com
        │
        ▼
   security_commands.py
        │
        ▼
   security/email_security.py
        │  _query_txt() → dnspython | dig | nslookup
        │  _analyze_spf() / _analyze_dkim() / _analyze_dmarc()
        │
        ▼
   Structured result dict → formatters.py → stdout / file

   nadzoring security subdomains example.com
        │
        ▼
   security_commands.py
        │
        ▼
   security/subdomain_scan.py
        │  _fetch_ct_subdomains() → crt.sh HTTPS API
        │  ThreadPoolExecutor → _probe_subdomain() → socket.gethostbyname()
        │
        ▼
   List of result dicts → formatters.py → stdout / file

----

Adding a New Feature
--------------------

1. **Create a module** in the appropriate domain package (e.g.
   ``security/myfeature.py`` or ``dns_lookup/myfeature.py``).
2. **Define a public function** with a clear docstring, type hints, and
   error handling that returns structured data.
3. **Export it** from the package ``__init__.py``.
4. **Add a CLI command** in the relevant ``commands/`` file using
   ``@common_cli_options``.
5. **Add a formatter** in ``utils/formatters.py`` if needed.
6. **Write tests** in ``tests/``.
7. **Document it** in a new or existing ``.rst`` file under ``commands/``
   or the API reference.
