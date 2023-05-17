# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

master_doc = 'index'

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Project information -----------------------------------------------------

project = 'The AT Protocol SDK'
copyright = '2023 Ilya (Marshal) <https://github.com/MarshalX>'
author = 'Ilya (Marshal)'

language = 'en'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinxext.opengraph',
    'sphinx_copybutton',
    'sphinx_favicon',
    'myst_parser',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# myst

myst_heading_anchors = 4
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html?highlight=header-anchors#code-fences-using-colons
myst_enable_extensions = ['colon_fence']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# These folders are copied to the documentation's HTML output
html_static_path = ['_static']

html_search_language = 'en'

html_title = 'The AT Protocol SDK'
html_theme = 'furo'
html_logo = '_static/img/logo.png'

html_css_files = [
    'css/custom.css',
]

html_theme_options = {
    'navigation_with_keys': True,
}

# Favicons
favicons = [
    {
        'rel': 'icon',
        'static-file': 'img/logo.png',
        'type': 'image/png',
    },
    {
        'rel': 'icon',
        'sizes': '16x16',
        'static-file': 'img/favicon-16x16.png',
        'type': 'image/png',
    },
    {
        'rel': 'icon',
        'sizes': '32x32',
        'static-file': 'img/favicon-32x32.png',
        'type': 'image/png',
    },
    {
        'rel': 'apple-touch-icon',
        'sizes': '180x180',
        'static-file': 'img/apple-touch-icon-180x180.png',
        'type': 'image/png',
    },
]


# OpenGraph
ogp_site_url = 'https://atproto.blue/'
# Social preview of GitHub Repo. I guess it's lifetime link until edit/delete action,
ogp_image = 'https://repository-images.githubusercontent.com/569485568/9d743322-10a2-4290-9a05-a88348cce2b6'
ogp_type = 'article'
ogp_enable_meta_description = True
