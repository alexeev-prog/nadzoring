from datetime import datetime
from pathlib import Path

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.driver import DefaultDriver
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate
from sphinx_polyversion.pyvenv import Pip, VenvWrapper
from sphinx_polyversion.sphinx import SphinxBuilder

#: Regex matching the branches to build docs for
BRANCH_REGEX = r"^main$"

#: Regex matching the tags to build docs for
TAG_REGEX = r"^v\d+\.\d+.*$"

#: Output dir relative to project root
OUTPUT_DIR = "docs/_build/html"

#: Source directory relative to project root
SOURCE_DIR = "docs"

#: Arguments to pass to `sphinx-build`
SPHINX_ARGS = ["-a", "-v"]

#: Pip packages to install in each version's venv
PIP_ARGS = ["-e", ".", "sphinx", "furo", "sphinx-polyversion"]

#: Mock data used for building local version (for local testing)
MOCK_DATA = {
    "revisions": [
        GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0)),
    ],
    "current": GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0)),
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
