from datetime import datetime
from pathlib import Path

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.driver import DefaultDriver
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate
from sphinx_polyversion.pyvenv import Pip
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

#: Mock data used for building local version (for local testing)
MOCK_DATA = {
    "revisions": [
        GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0)),
    ],
    "current": GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0)),
}

#: Pip dependencies to install for building docs
PIP_PACKAGES = [
    "sphinx",
    "furo",
    "sphinx-polyversion",
]

apply_overrides(globals())

DefaultDriver(
    cwd=Path(),
    output=Path(OUTPUT_DIR),
    vcs=Git(
        branch_regex=BRANCH_REGEX,
        tag_regex=TAG_REGEX,
        buffer_size=1 * 10**9,
        predicate=file_predicate(["docs", "src"]),
    ),
    builder=SphinxBuilder(
        source=Path(SOURCE_DIR),
        args=SPHINX_ARGS,
    ),
    env=Pip(
        packages=PIP_PACKAGES,
    ),
    template_dir=Path("docs/_templates"),
    static_dir=Path("docs/_static"),
).run(MOCK_DATA)
