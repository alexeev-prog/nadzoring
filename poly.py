from datetime import datetime
from pathlib import Path

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.driver import DefaultDriver
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate
from sphinx_polyversion.sphinx import SphinxBuilder

BRANCH_REGEX = r"^main$"

TAG_REGEX = r"^v\d+\.\d+.*$"

OUTPUT_DIR = "docs/_build/html"

SOURCE_DIR = "docs"

SPHINX_ARGS = ["-a", "-v"]

MOCK_DATA = {
    "revisions": [
        GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0)),
    ],
    "current": GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(0)),
}

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
).run(MOCK_DATA)
