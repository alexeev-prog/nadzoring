Contributing
============

Thank you for considering contributing to Nadzoring!  This page covers
the development workflow, code style rules, and submission process.

----

Setting Up the Development Environment
----------------------------------------

.. code-block:: bash

   git clone https://github.com/alexeev-prog/nadzoring.git
   cd nadzoring
   pip install -e ".[dev]"

----

Code Style
----------

Nadzoring uses `ruff <https://docs.astral.sh/ruff/>`_ for linting and
formatting.  Run the full check before committing:

.. code-block:: bash

   ruff check src/
   ruff format src/

Key conventions enforced by the ruff config:

- **Double quotes** for strings
- **Google-style docstrings** (``D`` rules) with examples where relevant
- **isort** import ordering (``I`` rules)
- **PEP 8** naming: ``snake_case`` for functions/variables,
  ``PascalCase`` for classes, ``UPPER_CASE`` for module-level constants
- No ``print()`` in library code — use the :mod:`nadzoring.logger` module
- Boolean keyword-only arguments via ``*`` separator (``FBT`` rules)
- ``BLE001`` (broad exception catch) may be suppressed with a comment where
  intentional — document *why* the broad catch is needed

----

Design Principles
-----------------

Before adding a feature, read :doc:`architecture`.  The short version:

1. **SRP** — one module, one concern.
2. **DRY** — extract repeated patterns into helpers or the ``utils/``
   package.
3. **KISS** — prefer simple, readable code over clever one-liners.
4. **Error handling** — never raise on expected network/DNS/SSL failures;
   return structured error data instead.
5. **Type hints** — all public functions must have complete type
   annotations; use ``TypedDict`` for structured return values.
6. **No comments** — use Google-style docstrings with ``Args``, ``Returns``,
   and ``Examples`` sections instead of inline comments.
7. **Timeout support** — all network-bound functions must accept an optional
   ``timeout_config: TimeoutConfig | None = None`` parameter and respect
   phase-specific timeouts (connect/read) as well as the overall lifetime
   timeout.

----

Adding a Security Check
------------------------

The ``security/`` package follows the same conventions as other domain
packages.  When adding a new security check:

1. Create ``src/nadzoring/security/mycheck.py`` with a single public
   function (SRP).
2. Return a structured dict with an ``"error"`` key set to ``None`` on
   success or a human-readable string on failure.  Never raise.
3. Accept an optional ``timeout_config: TimeoutConfig | None = None``
   parameter and pass it down to any network-bound calls.
4. Export the function from ``src/nadzoring/security/__init__.py``.
5. Add a CLI command in ``src/nadzoring/commands/security_commands.py``
   using ``@common_cli_options(include_timeout=True)``.
6. Add the result shape to ``utils/formatters.py`` if a new formatter is
   needed.
7. Document the command in ``docs/commands/security.rst`` including the
   timeout options.

----

Writing Tests
-------------

Tests live in ``tests/``.  Run them with:

.. code-block:: bash

   pytest tests/

New features require at least:

- A happy-path test
- An error/edge-case test (e.g. domain not found, timeout, SSL error)
- A test verifying timeout configuration is respected (if applicable)

----

Submitting a Pull Request
--------------------------

1. Fork the repository.
2. Create a feature branch: ``git checkout -b feat/my-feature``.
3. Make your changes and add tests.
4. Run ``ruff check`` and ``pytest`` — both must pass.
5. Update the relevant ``.rst`` documentation file (``commands/security.rst``
   for new security commands, ``commands/network.rst`` for new network
   commands, etc.).
6. Open a PR with a clear description of what changed and why.

----

Areas We'd Love Help With
--------------------------

- Additional DNS record type support
- New health check validation rules
- CDN network database expansion
- Performance optimisations
- Additional output formats
- ARP detection heuristics
- New network diagnostic commands
- Extended security auditing: HSTS preload check, certificate transparency
  monitoring, CAA record validation, TLSA/DANE record inspection

----

Reporting Issues
----------------

Open an issue on GitHub at
https://github.com/alexeev-prog/nadzoring/issues.  Please include:

- Nadzoring version (``pip show nadzoring``)
- Python version and OS
- The full command or code snippet that triggered the issue
- The full error output
- If the issue is timeout-related, include the timeout values used
