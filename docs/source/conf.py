# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
import typing as t

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath('../..'))

master_doc = 'index'

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Project information -----------------------------------------------------

project = 'The AT Protocol SDK'
copyright = '2024 Ilya (Marshal) <https://github.com/MarshalX>'
author = 'Ilya (Marshal)'

language = 'en'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosectionlabel',
    'sphinxext.opengraph',
    'sphinx_copybutton',
    'sphinx_favicon',
    'myst_parser',
    'sphinxcontrib.autodoc_pydantic',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- MyST-Parser ---------------------------------------------------

myst_heading_anchors = 4
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html?highlight=header-anchors#code-fences-using-colons
myst_enable_extensions = ['colon_fence']

# -- Options for HTML output -------------------------------------------------

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
    'source_repository': 'https://github.com/MarshalX/atproto/',
    'source_branch': 'main',
    'source_directory': 'docs/source/',
}

# -- Favicons ---------------------------------------------------
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

# -- Read The docs ---------------------------------------------------

# Define the canonical URL if you are using a custom domain on Read the Docs
html_baseurl = os.environ.get('READTHEDOCS_CANONICAL_URL', '')

# Tell Jinja2 templates the build is running on Read the Docs
if os.environ.get('READTHEDOCS', '') == 'True':
    if 'html_context' not in globals():
        html_context = {}
    html_context['READTHEDOCS'] = True

# -- OpenGraph ---------------------------------------------------
ogp_site_url = 'https://atproto.blue/'
# Social preview of GitHub Repo. I guess it's lifetime link until edit/delete action,
ogp_image = 'https://repository-images.githubusercontent.com/569485568/9d743322-10a2-4290-9a05-a88348cce2b6'
ogp_type = 'article'
ogp_enable_meta_description = True

# -- Pydantic models ---------------------------------------------------
autodoc_pydantic_model_undoc_members = True
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_signature_prefix = 'class'
autodoc_pydantic_field_list_validators = False
autodoc_pydantic_field_show_alias = False
autodoc_pydantic_settings_show_json = False

autosectionlabel_prefix_document = True


def setup(app: 'Sphinx') -> None:
    from docs.source.alias_resolver import resolve_internal_aliases, resolve_intersphinx_aliases

    app.connect('doctree-read', resolve_internal_aliases)
    app.connect('missing-reference', resolve_intersphinx_aliases)
