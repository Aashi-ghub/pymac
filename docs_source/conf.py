# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

project = "Py2Mac"
copyright = "2024, Rafal Wytrykus"
author = "Rafal Wytrykus"

version = "0.1"
release = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Enables Google-style docstring support
    "sphinx_autodoc_typehints",  # Automatically includes type hints
    "sphinx_github_style",
    "myst_parser",
]

napoleon_include_private_with_doc = False

# Set the theme
templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_context = {
    "github_user": "rafalwytrykus",
    "github_repo": "py2mac",
    "github_version": "master",
}

sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))
