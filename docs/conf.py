import inspect
import os
import sys
from typing import Literal

from sphinx_polyversion.api import load  # type: ignore

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
version = "0.3.0"
release = "0.3"
project_copyright = "2025, Alexeev Bronislaw"

GITHUB_USER = "alexeev-prog"
GITHUB_REPO = "nadzoring"
GITHUB_BASE_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"

_current_ref: str = "main"
_polyversion_current = globals().get("current")
if _polyversion_current is not None:
    _current_ref = _polyversion_current.name

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
    "sphinx.ext.linkcode",
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


def linkcode_resolve(domain: str, info: dict) -> str | None:
    """Generate a GitHub source URL for a documented Python object.

    Called by sphinx.ext.linkcode for every documented object.
    Returns a URL pointing to the exact file (and line, if resolvable)
    on GitHub at the ref that matches the current polyversion build.

    Args:
        domain: Sphinx domain (e.g. "py", "c", "cpp").
        info:   Dict with keys "module" and "fullname".

    Returns:
        A GitHub URL string, or None if the object cannot be resolved.
    """
    if domain != "py":
        return None

    module_name: str = info.get("module", "")
    fullname: str = info.get("fullname", "")

    if not module_name:
        return None

    try:
        module = sys.modules.get(module_name)
        if module is None:
            return None

        obj = module
        for part in fullname.split("."):
            try:
                obj = getattr(obj, part)
            except AttributeError:
                return None

        obj = inspect.unwrap(obj)  # type: ignore

        source_file: str | None = inspect.getsourcefile(obj)
        if source_file is None:
            return None

        source_file = os.path.realpath(source_file)

        repo_root: str | None = None
        candidate = source_file
        for _ in range(20):
            candidate = os.path.dirname(candidate)
            if os.path.isdir(os.path.join(candidate, ".git")):
                repo_root = candidate
                break

        if repo_root is None:
            return None

        rel_path = os.path.relpath(source_file, repo_root).replace(os.sep, "/")

        try:
            source_lines, start_line = inspect.getsourcelines(obj)
            end_line = start_line + len(source_lines) - 1
            line_fragment = f"#L{start_line}-L{end_line}"
        except (OSError, TypeError):
            line_fragment = ""

        return f"{GITHUB_BASE_URL}/blob/{_current_ref}/{rel_path}{line_fragment}"

    except Exception:  # noqa: BLE001
        return None


def skip(app, what, name, obj, would_skip, options) -> Literal[False] | bool:
    if name == "__init__":
        return False
    return would_skip


def setup(app) -> None:
    app.connect("autodoc-skip-member", skip)
