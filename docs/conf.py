import os
import tomllib
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("src"))

docs_type = os.environ.get("NADZORING_DOCS_TYPE", "latest")

project = "nadzoring"
author = "Alexeev Bronislav"
copyright = f"{datetime.now().year}, Alexeev Bronislav"

if docs_type == "stable":
    try:
        with open("../pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            version = data["project"]["version"]
    except:
        version = "unknown"
else:
    version = "latest (development)"

release = version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx.ext.extlinks",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True,
    "special-members": "__init__",
    "show-inheritance": True,
}

autodoc_mock_imports = []

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True

html_theme = "furo"
html_static_path = ["_static"]
html_title = f"Nadzoring {version}"

html_context = {
    "docs_type": docs_type,
    "version": version,
    "versions": [
        ("stable", "/nadzoring/"),
        ("latest", "/nadzoring/latest/"),
    ],
    "current_version": docs_type,
}

html_theme_options = {
    "footer_content": f"Documentation version: {version} ({docs_type}) | "
                     f"<a href='/'>Stable</a> | "
                     f"<a href='/latest/'>Latest</a>",
}



todo_include_todos = True

autosummary_generate = True

source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip

def setup(app):
    app.connect("autodoc-skip-member", skip)
    app.connect("html-page-context", add_docs_type)

def add_docs_type(app, pagename, templatename, context, doctree):
    context["docs_type"] = docs_type
