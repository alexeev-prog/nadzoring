import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("../src/nadzoring"))
sys.path.insert(0, os.path.abspath("src/nadzoring"))

from sphinx_polyversion.api import load

load(globals())

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
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

pygments_style = "gruvbox-dark"

html_theme = "furo"
html_static_path: list[str] = ["_static"]
todo_include_todos = True
auto_doc_default_options: dict[str, bool] = {"autosummary": True}

autodoc_mock_imports = []

templates_path = ["_templates"]

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


def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip


def setup(app) -> None:
    app.connect("autodoc-skip-member", skip)
