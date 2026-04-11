import nox


@nox.session(venv_backend="uv")
def test(session):
    """Run tests on specified Python versions with coverage."""
    session.run_always("uv", "sync", "--all-groups", external=True)
    session.run(
        "uv",
        "run",
        "pytest",
        "tests/",
        "--cov=src/nadzoring/",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "--cov-fail-under=0",
        "-v",
        "-s",
        "--tb=short",
        "--strict-markers",
        "-n",
        "auto",
        *session.posargs,
    )


@nox.session(venv_backend="uv")
def lint(session):
    """Run ruff linter."""
    session.run_always("uv", "sync", "--all-groups", external=True)
    session.run("uv", "run", "ruff", "check", "src/nadzoring/")


@nox.session(venv_backend="uv")
def mypy_typing(session):
    """Run mypy type checking."""
    session.run_always("uv", "sync", "--all-groups", external=True)
    session.run("uv", "run", "mypy", "src/nadzoring/")
