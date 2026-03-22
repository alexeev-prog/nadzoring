import nox

python_versions = ["3.12", "3.13", "3.14"]


def install_with_dev(session):
    """Install project with dev dependencies."""
    session.run_always("uv", "pip", "install", "--system", "-e", ".[dev]", external=True)


@nox.session(python=python_versions, venv_backend="uv")
def test(session):
    """Run tests on specified Python versions."""
    install_with_dev(session)

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
    install_with_dev(session)
    session.run("ruff", "check", "src/nadzoring/", external=False)


@nox.session(venv_backend="uv")
def mypy_typing(session):
    """Run mypy type checking."""
    install_with_dev(session)
    session.run("mypy", "src/nadzoring/", external=False)