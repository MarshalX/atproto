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
from pathlib import Path

from sphinxawesome_theme.postprocess import Icons

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
copyright = '2023-2026 Ilya (Marshal) 🦁'
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
    'sphinx_design',
    'sphinx_sitemap',
    'sphinx_reredirects',
    'sphinx_favicon',
    'myst_parser',
    'sphinxcontrib.autodoc_pydantic',
    'sphinxcontrib.googleanalytics',
]

# Stubs at the pre-restructure paths, so old links resolve without edge configuration.
from docs.source.redirects_map import REDIRECTS  # noqa: E402

redirects = REDIRECTS
# The default stub template has no canonical link, which leaves the old and new URLs
# competing in search results. No noindex: these are the pages whose ranking we are keeping.
redirect_html_template_file = '_templates/redirect_stub.html'

# DocSearch is credentialed; without the credentials the built-in Sphinx search is used.
DOCSEARCH_APP_ID = os.environ.get('DOCSEARCH_APP_ID')
DOCSEARCH_API_KEY = os.environ.get('DOCSEARCH_API_KEY')
DOCSEARCH_INDEX_NAME = os.environ.get('DOCSEARCH_INDEX_NAME')

if DOCSEARCH_APP_ID and DOCSEARCH_API_KEY and DOCSEARCH_INDEX_NAME:
    extensions.append('sphinx_docsearch')
    docsearch_app_id = DOCSEARCH_APP_ID
    docsearch_api_key = DOCSEARCH_API_KEY
    docsearch_index_name = DOCSEARCH_INDEX_NAME
    docsearch_placeholder = 'Search the docs'
    docsearch_missing_results_url = 'https://github.com/MarshalX/atproto/discussions/new?category=q-a&title=${query}'
else:
    print(
        '[conf.py] DocSearch env vars missing - the built-in Sphinx search will be used',
        file=sys.stderr,
    )


# Headings and labels of the included README.md, and names shared by many modules.
suppress_warnings = ['myst.header', 'autosectionlabel.*', 'ref.python']

# -- Pygments ---------------------------------------------------
pygments_style = 'friendly'
pygments_style_dark = 'monokai'

# -- MyST-Parser ---------------------------------------------------

myst_heading_anchors = 4
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html?highlight=header-anchors#code-fences-using-colons
myst_enable_extensions = ['colon_fence']

# -- Options for HTML output -------------------------------------------------

# These folders are copied to the documentation's HTML output
html_static_path = ['_static']

html_search_language = 'en'

html_title = 'The AT Protocol SDK'
html_theme = 'sphinxawesome_theme'
html_domain_indices = False
html_copy_source = False
html_show_sourcelink = False
html_show_sphinx = False
html_permalinks_icon = Icons.permalinks_icon

html_css_files = [
    'css/custom.css',
]

html_theme_options = {
    'show_prev_next': True,
    'awesome_external_links': True,
    'show_breadcrumbs': True,
    'show_scrolltop': True,
    'main_nav_links': {
        'Getting started': 'readme',
        'Client': 'atproto_client/client',
        'Models': 'models/index',
        'Firehose': 'atproto_firehose/index',
        'Changelog': 'change_log',
    },
    'logo_light': '_static/img/logo.png',
    'logo_dark': '_static/img/logo.png',
    'extra_header_link_icons': {
        'repository on GitHub': {
            'link': 'https://github.com/MarshalX/atproto',
            'icon': (
                '<svg height="16px" style="margin-top:-2px;display:inline" viewBox="0 0 45 44" '
                'fill="currentColor" xmlns="http://www.w3.org/2000/svg">'
                '<path fill-rule="evenodd" clip-rule="evenodd" '
                'd="M22.477.927C10.485.927.76 10.65.76 22.647c0 9.596 6.223 17.736 '
                '14.853 20.608 1.087.2 1.483-.47 1.483-1.047 '
                '0-.516-.019-1.881-.03-3.693-6.04 '
                '1.312-7.315-2.912-7.315-2.912-.988-2.51-2.412-3.178-2.412-3.178-1.972-1.346.149-1.32.149-1.32 '
                '2.18.154 3.327 2.24 3.327 2.24 1.937 3.318 5.084 2.36 6.321 '
                '1.803.197-1.403.759-2.36 '
                '1.379-2.903-4.823-.548-9.894-2.412-9.894-10.734 '
                '0-2.37.847-4.31 2.236-5.828-.224-.55-.969-2.759.214-5.748 0 0 '
                '1.822-.584 5.972 2.226 '
                '1.732-.482 3.59-.722 5.437-.732 1.845.01 3.703.25 5.437.732 '
                '4.147-2.81 5.967-2.226 '
                '5.967-2.226 1.185 2.99.44 5.198.217 5.748 1.392 1.517 2.232 3.457 '
                '2.232 5.828 0 '
                '8.344-5.078 10.18-9.916 10.717.779.67 1.474 1.996 1.474 4.021 0 '
                '2.904-.027 5.247-.027 '
                '5.96 0 .58.392 1.256 1.493 1.044C37.981 40.375 44.2 32.24 44.2 '
                '22.647c0-11.996-9.726-21.72-21.722-21.72" fill="currentColor"/></svg>'
            ),
        },
        'package on PyPI': {
            'link': 'https://pypi.org/project/atproto/',
            'icon': (
                '<svg height="16px" style="margin-top:-2px;display:inline" viewBox="0 0 24 24" '
                'fill="currentColor" xmlns="http://www.w3.org/2000/svg">'
                '<path d="M11.885.002c-.98.004-1.918.088-2.744.234-2.433.43-2.875 1.33-2.875 '
                '2.99v2.193h5.75v.73H4.108c-1.672 0-3.136 1.005-3.594 2.917-.528 2.19-.552 '
                '3.558 0 5.846.41 '
                '1.703 1.386 2.916 3.058 2.916h1.977v-2.628c0-1.9 1.644-3.574 3.594-3.574h5.746c1.6 '
                '0 2.875-1.315 2.875-2.92V3.226c0-1.558-1.314-2.728-2.875-2.988A17.99 17.99 0 0 0 '
                '11.885.002zM8.775 1.762c.595 0 1.08.492 1.08 1.097 0 .603-.485 1.09-1.08 '
                '1.09-.596 0-1.08-.487-1.08-1.09-.001-.606.484-1.097 1.08-1.097z"/>'
                '<path d="M19.132 6.149v2.556c0 1.982-1.68 3.651-3.595 3.651H9.79c-1.574 '
                '0-2.876 1.347-2.876 '
                '2.922v5.478c0 1.56 1.356 2.475 2.876 2.922 1.822.535 3.567.632 5.747 0 '
                '1.447-.419 2.875-1.263 '
                '2.875-2.922v-2.193H12.67v-.73h8.617c1.672 0 2.295-1.165 2.876-2.917.6-1.804.575-3.54 '
                '0-5.846-.414-1.664-1.201-2.917-2.876-2.917h-2.156zm-3.232 13.876c.596 0 1.08.486 '
                '1.08 1.09 0 .606-.484 '
                '1.097-1.08 1.097-.595 0-1.08-.491-1.08-1.097.001-.604.485-1.09 1.08-1.09z"/></svg>'
            ),
        },
    },
}

# -- Sitemap ---------------------------------------------------
sitemap_locales = [None]
sitemap_url_scheme = '{link}'

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
html_baseurl = os.environ.get('READTHEDOCS_CANONICAL_URL', 'https://atproto.blue/')

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

# -- Google Analytics ---------------------------------------------------
googleanalytics_id = 'G-07PYQCJ0XP'
googleanalytics_enabled = True

autodoc_default_options = {'exclude-members': 'py_type'}

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


def prepare_model_modules(_app: 'Sphinx') -> None:
    """Resolve every model module through the lazy accessor so its forward references are injected."""
    from atproto_client import models

    for alias in dir(models):
        getattr(models, alias, None)


def scope_pygments_to_theme(app: 'Sphinx', exception: t.Optional[Exception]) -> None:
    """Rewrite the Pygments stylesheet so both palettes follow the theme toggle.

    The theme emits its dark palette inside ``@media (prefers-color-scheme: dark)`` while
    switching the page on an ``html.dark`` class. A reader whose system preference disagrees
    with the toggle then gets tokens from one palette over the other palette's background, and
    tokens only one palette defines leak across. Scoping both to the class removes the coupling.

    The palettes' own container background is dropped: the theme renders code on the page
    background, not in a box.
    """
    if exception is not None or app.builder.name not in ('html', 'dirhtml'):
        return

    from pygments.formatters import HtmlFormatter

    blocks = []
    for style, selector in (
        (app.config.pygments_style, 'html:not(.dark) .highlight'),
        (app.config.pygments_style_dark, 'html.dark .highlight'),
    ):
        defs = HtmlFormatter(style=style).get_style_defs(selector)
        blocks.append('\n'.join(line for line in defs.splitlines() if not line.startswith(f'{selector} {{')))

    (Path(app.outdir) / '_static' / 'pygments.css').write_text('\n'.join(blocks), encoding='UTF-8')


def setup(app: 'Sphinx') -> None:
    from docs.source.alias_resolver import resolve_internal_aliases, resolve_intersphinx_aliases

    app.connect('builder-inited', prepare_model_modules)
    app.connect('build-finished', scope_pygments_to_theme)
    app.connect('doctree-read', resolve_internal_aliases)
    app.connect('missing-reference', resolve_intersphinx_aliases)
