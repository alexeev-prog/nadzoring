import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("../src/nadzoring"))
sys.path.insert(0, os.path.abspath("src/nadzoring"))

project = "nadzoring"
author = "Alexeev Bronislav"
version = "0.1.4"
release = "0.1"
project_copyright = "2025, Alexeev Bronislaw"

autodoc_default_options: dict[str, bool | str] = {
    "members": True,
    "undoc-members": True,
    "private-members": True,
    "special-members": "__init__",
}

extensions: list[str] = [
    "sphinx.ext.autodoc",  # autodoc from docstrings
    "sphinx.ext.viewcode",  # links to source code
    "sphinx.ext.napoleon",  # support google and numpy docs style
    "sphinx.ext.todo",  # support TODO
    "sphinx.ext.coverage",  # check docs coverage
    "sphinx.ext.ifconfig",  # directives in docs
    "sphinx.ext.autosummary",  # generating summary for code
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx-multiversion"
]

smv_branch_whitelist = r"^main$"
smv_tag_whitelist = r"^v\d+\.\d+.*$"
smv_remote_whitelist = r"^origin$"
smv_released_pattern = r"^refs/tags/.*$"
smv_outputdir_format = "{ref.name}"
smv_prefer_remote_refs = False

pygments_style = "gruvbox-dark"

html_theme = "furo"  # theme
html_static_path: list[str] = ["_static"]  # static dir
todo_include_todos = True  # include todo in docs
auto_doc_default_options: dict[str, bool] = {"autosummary": True}

autodoc_mock_imports = []

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "versioning.html",
        "sidebar/scroll-end.html",
    ]
}

templates_path = ["_templates"]


def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip


def setup(app) -> None:
    app.connect("autodoc-skip-member", skip)
