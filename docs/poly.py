from datetime import datetime
from pathlib import Path

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.driver import DefaultDriver
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate
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
SPHINX_ARGS = "-a -v".split()

#: Mock data used for building local version (for local testing)
MOCK_DATA = {
    "revisions": [
        GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0)),
    ],
    "current": GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0)),
}

#: Whether to build using only local files and mock data
MOCK = False

#: Whether to run the builds sequentially
SEQUENTIAL = False

# Load overrides read from commandline to global scope
apply_overrides(globals())

# Determine repository root directory
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
    template_dir=root / "docs/_templates",
    static_dir=root / "docs/_static",
    mock=MOCK_DATA,
).run(MOCK, SEQUENTIAL)
