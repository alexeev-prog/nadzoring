import os
import sys
from typing import Literal

from sphinx_polyversion.api import load

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("../src/nadzoring"))
sys.path.insert(0, os.path.abspath("src/nadzoring"))


load(globals())

project = "nadzoring"
author = "Alexeev Bronislav"
version = "0.1.7"
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

html_js_files: list[tuple[str, dict[str, str]]] = [
    (
        "https://context7.com/widget.js",
        {
            "data-library": "/alexeev-prog/nadzoring",
            "data-color": "#059669",
            "data-position": "bottom-right",
            "data-placeholder": "Ask about nadzoring...",
            "async": "async",
        },
    ),
]
todo_include_todos = True
auto_doc_default_options: dict[str, bool] = {"autosummary": True}

autodoc_mock_imports: list = []

templates_path: list[str] = ["_templates"]

html_sidebars: dict[str, list[str]] = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "versioning.html",
        "sidebar/scroll-end.html",
    ]
}


def skip(app, what, name, obj, would_skip, options) -> Literal[False] | bool:
    if name == "__init__":
        return False
    return would_skip


def setup(app) -> None:
    app.connect("autodoc-skip-member", skip)
