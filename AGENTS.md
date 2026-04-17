---
name: nadzoring-project-custodian
description: |
  This skill defines the operating procedures for AI agents contributing to the Nadzoring project.
  It covers code contribution rules, architectural decision-making, documentation standards,
  and project management workflows. Follow this document strictly when performing any task
  related to the Nadzoring repository.
version: 1.0.0
priority: critical
tags: [python, cli, library, networking, security, open-source, maintainer]
---

# Nadzoring Project Custodian: Agent Operating Procedures

## 1. Core Principles and Project Philosophy

This project is governed by the principles of Clean Architecture, Single Responsibility Principle (SRP), Don't Repeat Yourself (DRY), and Keep It Simple, Stupid (KISS). Every contribution must reflect these values. The project maintains a zero-warnings policy enforced by ruff. Any code that introduces a linting warning is not acceptable. The project aims for 100% test coverage before any new release. All public functions and modules must be fully typed and documented.

## 2. Repository Structure and Critical Files

Before performing any task, understand the repository layout. The root contains `pyproject.toml` which centralizes build configuration and tool settings. `ruff.toml` defines the exact linting rules and is the source of truth for code style. `noxfile.py` controls all automation tasks including testing, linting, and type checking. The `.github/workflows/` directory contains the CI/CD pipelines. The `docs/` directory holds the Sphinx documentation source. The `src/nadzoring/` directory contains the actual package code, with `cli.py` as the main entry point, `commands/` for CLI-specific logic, and domain modules like `dns_lookup/`, `network_base/`, `security/`, and `arp/` for business logic.

## 3. Code Contribution and Development Workflow

### 3.1 Issue Selection and Assignment
When the user asks to work on an issue, first identify its type. Issues labeled `good-first-issue` are suitable for newcomers. Issues have complexity labels: `trivial`, `middle`, `hard`. Always confirm the user's comfort level before assigning a non-trivial task. The most critical open issue is achieving 100% test coverage, which blocks the next release. When working on this, refer to `tests/test_main.py` and the `nox -s test` session to understand the current coverage gaps.

### 3.2 Development Environment Setup
Instruct the user to set up the development environment using uv. The steps are documented in `CONTRIBUTING.md`. Ensure the user runs `uv sync` to install dependencies. Before writing any code, the user must run `nox -s lint` and `nox -s typing` to verify the current state. The agent must not suggest any change that would violate the zero-warnings policy.

### 3.3 Coding Standards Enforcement
The source of truth for code style is `ruff.toml`. Key enforced rules include Google-style docstrings for all public functions, complete type annotations using Python 3.12+ syntax (e.g., `str | None`, `list[str]`), keyword-only arguments for boolean flags, and the use of `dataclass` for structured data. The agent must review any code suggestion against these rules. For example, if the user proposes a function returning `Optional[str]`, the agent must correct it to `str | None` and cite the project standard.

### 3.4 Writing Tests
Any new feature or bug fix must include tests. The project uses pytest. The agent must guide the user to write tests that cover both happy paths and error cases. For domain functions that return structured error dicts (e.g., DNS results with an `error` field), the tests must verify that the error is correctly populated on failure. The agent should remind the user that the goal is 100% coverage and that the `nox -s test` command will report coverage.

### 3.5 Commit Message Convention
The project does not strictly enforce Conventional Commits, but `git-cliff` is used to generate the changelog from commit messages. The agent must ensure commit messages follow patterns that will be correctly parsed. For new features, messages should start with `feat:`, `add:`, or `implement:`. For bug fixes, use `fix:`, `bugfix:`, or `resolve:`. For documentation, use `docs:`. The agent should format the commit message accordingly when assisting the user.

### 3.6 Pull Request Process
Before submitting a PR, the user must run `nox` locally to ensure all sessions pass. The PR description must reference the issue it closes. The agent must check that the PR follows the template in `.github/PULL_REQUEST_TEMPLATE.md`. The CI pipelines will run automatically on PR creation; the agent should monitor them and advise the user to fix any failures.

## 4. Architectural Decision Making

### 4.1 CLI and Domain Separation
When adding a new feature, the agent must enforce the separation between the CLI layer and the domain layer. CLI commands reside in `commands/` and use `@common_cli_options` decorator. They parse user input, call domain functions, and return raw data. Domain functions reside in the appropriate package (`dns_lookup/`, `security/`, etc.), never use `click`, and never print output. They return structured `TypedDict` or `dataclass` objects.

### 4.2 Error Handling Strategy
Domain functions must never raise exceptions for expected failures. All expected error conditions (DNS timeouts, NXDOMAIN, connection refused) must be captured and returned in the result's `error` field. The agent must review new function implementations to ensure they follow this pattern. Only truly unexpected errors (programming mistakes, missing system commands) should be allowed to propagate as exceptions.

### 4.3 Timeout Configuration
All network-bound functions must accept an optional `timeout_config: TimeoutConfig | None = None` parameter. If `None` is passed, the function must create a default `TimeoutConfig()` instance. The `TimeoutConfig` class (from `nadzoring.utils.timeout`) provides three timeout values:

- `connect: float` — timeout for establishing connections (default: 5.0)
- `read: float` — timeout for read operations after connection (default: 10.0)
- `lifetime: float` — total operation duration limit (default: 120.0)

**Resolution order:** Phase-specific values take precedence over the generic `lifetime` value when both are provided.

**CLI exposure:** Use `include_timeout=True` in `@common_cli_options` to automatically expose `--timeout`, `--connect-timeout`, and `--read-timeout` flags.

**Lifetime enforcement:** Use `with timeout_context(timeout_config):` around the entire operation. On Unix systems this uses SIGALRM to interrupt blocking calls; on Windows it provides a best-effort post-check.

**Socket configuration:** Use `timeout_config.apply_to_socket(sock)` to set the read timeout, or `configure_socket_with_timeouts(sock, config, connect_mode=True/False)` for phase-specific control.

**Timeout exceptions:** The `OperationTimeoutError` exception is raised when the lifetime timeout is exceeded. This is an expected failure and should be caught and converted to an error field in the result dict.

### 4.4 Adding a New CLI Command
The procedure for adding a new command is documented in `architecture.rst`. The agent should follow it step by step: create a new module in the appropriate domain package, define a public function with docstring and types, export it in the package `__init__.py`, add a CLI command in the relevant `commands/` file using `@common_cli_options(include_timeout=True)` for network-bound commands, and add a formatter in `formatters.py` if needed. The agent must verify each step is completed.

### 4.5 Documentation Updates
Any change to the public API or command behavior must be reflected in the documentation. The documentation source is in `docs/`. The agent must guide the user to update the relevant `.rst` files. If a new module is added, the `genapidoc.sh` script must be re-run to update the API reference. The agent should remind the user that the documentation is versioned and that changes to the `main` branch will be reflected in the "latest" documentation after the next docs build.

## 5. Project Management and Releases

### 5.1 Issue Triage
When the user reports a new issue, the agent must help categorize it. Determine if it's a bug, feature request, or question. If it's a bug, check if it's reproducible and request necessary environment details (OS, Python version, Nadzoring version). If it's a feature request, assess its complexity and suggest appropriate labels (`trivial`, `middle`, `hard`) and thematic labels (`ui/ux`, `testing`, `security`).

### 5.2 Release Process
The release process is triggered by creating a Git tag. The agent must inform the user that before tagging, the test coverage must be at 100% and all CI checks must pass. The `git-cliff` configuration in `cliff.toml` will generate the changelog based on commit messages. After tagging, the GitHub Actions workflow will build and publish the package to PyPI and update the versioned documentation on GitHub Pages. The agent must also remind the user to update `SECURITY.md` to mark the new version as supported.

### 5.3 Security Vulnerability Handling
If a security vulnerability is reported, the agent must direct the user to follow the process in `SECURITY.md`. This means reporting it via the appropriate channel (likely email), not creating a public issue. The agent must assist in drafting a clear, non-public description of the vulnerability, its impact, and a proposed fix. The fix should be developed in a private fork or branch, and only merged and released once the vulnerability is publicly disclosed.

## 6. Agent Communication Style and Tools

### 6.1 Language and Tone
All communication must be in clear, professional English. Avoid emojis and informal slang. Be concise but complete. When explaining technical concepts, assume the user has a basic understanding of Python and networking but may not be familiar with the project's specific conventions. Always provide actionable steps.

### 6.2 Using References
When citing a rule or standard, refer to the specific file in the repository. For example, instead of saying "follow the docstring style," say "refer to the docstring examples in `CONTRIBUTING.md` and the Google style convention set in `ruff.toml`." This grounds the instruction in the project's source of truth.

### 6.3 Tool Invocation
The agent can invoke tools to interact with the repository. This includes reading files (`read_file`), searching for patterns (`search_files`), and listing directories (`list_dir`). Before suggesting a change, the agent should verify the current state of the relevant files. After suggesting a change, the agent may propose using a tool to write the change, but must always present the diff for the user to review.

### 6.4 Handling Ambiguity
If the user's request is ambiguous, the agent must ask clarifying questions. For example, if the user asks "add a new security check," the agent should ask: "What type of security check? Should it be placed in `security/`? Does it need a CLI command? What should it return? Does it need timeout support?" The agent should then reference the appropriate sections of this document to guide the user.

## 7. Final Verifications

Before any task is marked as complete, the agent must perform the following checks:

1.  **Linting**: Has `nox -s lint` been run and passed?
2.  **Typing**: Has `nox -s typing` been run and passed?
3.  **Tests**: Have new tests been added for the change? Does `nox -s test` pass with 100% coverage?
4.  **Timeout Support**: If the change involves network I/O, does it accept `timeout_config` and use `timeout_context` appropriately?
5.  **Documentation**: Have relevant `.rst` files been updated? If new public APIs were added, was `genapidoc.sh` run? Have timeout options been documented?
6.  **Commit Hygiene**: Are commit messages clear and follow patterns that `git-cliff` will parse?
7.  **PR Ready**: If this is for a PR, is the description filled out and linked to the correct issue?

Only when all these checks pass should the agent confirm the task as complete.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
