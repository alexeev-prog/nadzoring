import nox

python_versions = ["3.12", "3.13", "3.14"]


@nox.session(python=python_versions, venv_backend="uv")
def test(session):
    """Run tests on specified Python versions."""
    session.run_always(
        "uv", "pip", "install", "--system", "-e", ".[dev]", external=True
    )
    
    session.run(
        "pytest",
        "tests/",
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
    session.run_always("uv", "pip", "install", "--system", "-e", ".[dev]", external=True)
    session.run("ruff", "check", "src/nadzoring/")


@nox.session(venv_backend="uv")
def mypy_typing(session):
    """Run mypy type checking."""
    session.run_always("uv", "pip", "install", "--system", "-e", ".[dev]", external=True)
    session.run("mypy", "src/nadzoring/")


@nox.session(venv_backend="uv")
def mutants(session):
    """Run mutation testing."""
    session.run_always("uv", "pip", "install", "--system", "-e", ".[dev]", external=True)
    session.run("mutmut", "run")


@nox.session(venv_backend="uv")
def ty_typing(session):
    """Run ty type checking."""
    session.run_always("uv", "pip", "install", "--system", "-e", ".[dev]", external=True)
    session.run("ty", "check", "src/nadzoring/")
