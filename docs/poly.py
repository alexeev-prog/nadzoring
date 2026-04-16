from datetime import UTC, datetime
from pathlib import Path

from sphinx_polyversion.api import apply_overrides  # type: ignore
from sphinx_polyversion.driver import DefaultDriver  # type: ignore
from sphinx_polyversion.git import (
    Git,
    GitRef,
    GitRefType,  # type: ignore
    file_predicate,
)
from sphinx_polyversion.pyvenv import Pip, VenvWrapper  # type: ignore
from sphinx_polyversion.sphinx import SphinxBuilder  # type: ignore

BRANCH_REGEX = r"^main$"
TAG_REGEX = r"^v\d+\.\d+.*$"

OUTPUT_DIR = "docs/_build/html"
SOURCE_DIR = "docs"

SPHINX_ARGS: list[str] = ["-a", "-v"]

PIP_ARGS: list[str] = ["-e", ".[dev]", "sphinx", "furo", "sphinx-polyversion"]

MOCK_DATA: dict[str, list[GitRef]] = {
    "revisions": [
        GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0, tz=UTC)),
    ],
    "current": GitRef(
        "main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0, tz=UTC)
    ),
}

MOCK = False
SEQUENTIAL = False

apply_overrides(globals())

root = Git.root(Path(__file__).parent)
src = Path(SOURCE_DIR)

DefaultDriver(
    root,
    OUTPUT_DIR,
    vcs=Git(
        branch_regex=BRANCH_REGEX,
        tag_regex=TAG_REGEX,
        buffer_size=1 * 10**9,
        predicate=file_predicate([src]),
    ),
    builder=SphinxBuilder(src, args=SPHINX_ARGS),
    env=Pip.factory(
        venv=Path(".venv"),
        args=PIP_ARGS,
        creator=VenvWrapper(),
        temporary=True,
    ),
    template_dir=root / "docs/_templates",
    static_dir=root / "docs/_static",
    mock=MOCK_DATA,
).run(MOCK, SEQUENTIAL)
