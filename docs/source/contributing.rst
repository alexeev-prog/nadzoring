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

----

Design Principles
-----------------

Before adding a feature, read :doc:`architecture`.  The short version:

1. **SRP** — one module, one concern.
2. **DRY** — extract repeated patterns into helpers or the ``utils/``
   package.
3. **KISS** — prefer simple, readable code over clever one-liners.
4. **Error handling** — never raise on expected network/DNS failures;
   return structured error data instead.
5. **Type hints** — all public functions must have complete type
   annotations; use ``TypedDict`` for structured return values.

----

Writing Tests
-------------

Tests live in ``tests/``.  Run them with:

.. code-block:: bash

   pytest tests/

New features require at least:

- A happy-path test
- An error/edge-case test (e.g. domain not found, timeout)

----

Submitting a Pull Request
--------------------------

1. Fork the repository.
2. Create a feature branch: ``git checkout -b feat/my-feature``.
3. Make your changes and add tests.
4. Run ``ruff check`` and ``pytest`` — both must pass.
5. Update the relevant ``.rst`` documentation file.
6. Open a PR with a clear description of what changed and why.

----

Reporting Issues
----------------

Open an issue on GitHub at
https://github.com/alexeev-prog/nadzoring/issues.  Please include:

- Nadzoring version (``pip show nadzoring``)
- Python version and OS
- The full command or code snippet that triggered the issue
- The full error output
