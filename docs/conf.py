"""Sphinx configuration for the Veeresh Hanni Project learning site."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

project = "Veeresh Hanni Project"
copyright = "Veeresh Hanni"
author = "Veeresh Hanni"
release = "0.1.0"

extensions = ["myst_parser"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_title = "VHP Learning Guide"
html_static_path = ["_static"]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "substitution",
]
