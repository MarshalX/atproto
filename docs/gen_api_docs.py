"""Generate the nested API reference tree for ``atproto_client.models``."""

import json
import re
import shutil
import typing as t
from pathlib import Path

_REPO_ROOT = Path(__file__).absolute().parent.parent
_LEXICONS_DIR = _REPO_ROOT / 'lexicons'
_MODELS_PKG = _REPO_ROOT / 'packages' / 'atproto_client' / 'models'
_DOCS_SOURCE = _REPO_ROOT / 'docs' / 'source'
_OUTPUT_DIR = _DOCS_SOURCE / 'models'
_STUB_MAP = _DOCS_SOURCE / 'redirects_map.py'

_MODELS_MODULE = 'atproto_client.models'

# Namespaces have no lexicon of their own, so their card copy lives here.
_NAMESPACES: t.Dict[str, t.Tuple[str, str]] = {
    'app': ('apps', 'Application lexicons: everything an app exposes to the people using it.'),
    'app.bsky': ('home', 'The Bluesky microblogging app: profiles, posts, feeds, and the social graph.'),
    'app.bsky.actor': ('person', 'Profiles, preferences, statuses, and actor search.'),
    'app.bsky.ageassurance': ('verified', 'Age assurance flow and its resulting state.'),
    'app.bsky.bookmark': ('bookmark', 'Private bookmarks on records.'),
    'app.bsky.contact': ('mail', 'Contact discovery between actors.'),
    'app.bsky.draft': ('pencil', 'Unpublished post drafts.'),
    'app.bsky.embed': ('image', 'Post embeds: images, video, external links, and quoted records.'),
    'app.bsky.feed': ('rss', 'Posts, likes, reposts, threads, and feed generators.'),
    'app.bsky.graph': ('people', 'Follows, blocks, mutes, lists, and starter packs.'),
    'app.bsky.labeler': ('tag', 'Labeling services and the labels they declare.'),
    'app.bsky.notification': ('bell', 'Notifications, preferences, and push registration.'),
    'app.bsky.richtext': ('typography', 'Rich text facets: mentions, links, and tags.'),
    'app.bsky.unspecced': ('beaker', 'Unstable endpoints that may change or disappear without notice.'),
    'app.bsky.video': ('device-camera-video', 'Video uploads and the status of their processing jobs.'),
    'chat': ('comment-discussion', 'Private messaging lexicons.'),
    'chat.bsky': ('comment-discussion', 'Bluesky direct messages.'),
    'chat.bsky.actor': ('person', 'Chat profiles and account-level actions.'),
    'chat.bsky.convo': ('comment-discussion', 'Conversations, messages, and reactions.'),
    'chat.bsky.embed': ('link', 'Embeds carried inside chat messages.'),
    'chat.bsky.group': ('people', 'Group conversations and their membership.'),
    'chat.bsky.moderation': ('shield', 'Moderation of chat actors and messages.'),
    'chat.bsky.notification': ('bell', 'Chat notification preferences.'),
    'com': ('stack', 'The protocol itself, plus the lexicons of third-party services.'),
    'com.atproto': ('stack', 'Core AT Protocol: identities, repositories, servers, and sync.'),
    'com.atproto.admin': ('gear', 'Account administration for PDS operators.'),
    'com.atproto.identity': ('id-badge', 'Handles, DIDs, and identity resolution.'),
    'com.atproto.label': ('tag', 'Labels and the streams that publish them.'),
    'com.atproto.lexicon': ('file-code', 'Lexicon schemas published as records.'),
    'com.atproto.moderation': ('report', 'Moderation reports submitted by users.'),
    'com.atproto.repo': ('repo', 'Records and blobs: create, read, update, delete, and list.'),
    'com.atproto.server': ('server', 'Accounts, sessions, invites, and app passwords.'),
    'com.atproto.sync': ('sync', 'Repository sync: firehose, blocks, blobs, and checkouts.'),
    'com.atproto.temp': ('hourglass', 'Temporary endpoints that exist until a permanent one lands.'),
    'com.germnetwork': ('broadcast', 'Germ Network lexicons.'),
    'internal': ('lock', 'Internal lexicons that are not part of the public API.'),
    'internal.bsky': ('lock', 'Internal Bluesky lexicons.'),
    'internal.bsky.actor': ('lock', 'Internal actor endpoints.'),
    'network': ('globe', 'Infrastructure services behind the network.'),
    'network.bsky': ('globe', 'Bluesky network infrastructure.'),
    'network.bsky.jetstream': ('broadcast', 'Jetstream: event stream, archive segments, and imports.'),
    'site': ('browser', 'Websites published on atproto.'),
    'site.standard': ('browser', 'The standard website vocabulary.'),
    'site.standard.graph': ('link', 'Links between websites and the accounts behind them.'),
    'site.standard.theme': ('paintbrush', 'Website theming.'),
    'tools': ('tools', 'Tooling for the people who operate the network.'),
    'tools.ozone': ('shield', 'Ozone, the moderation tooling of the network.'),
    'tools.ozone.communication': ('mail', 'Templates for moderator communication.'),
    'tools.ozone.hosting': ('server', 'Account hosting history.'),
    'tools.ozone.moderation': ('shield', 'Moderation events, reports, and subject state.'),
    'tools.ozone.queue': ('list-ordered', 'The moderation queue and its assignments.'),
    'tools.ozone.report': ('report', 'Report intake and handling.'),
    'tools.ozone.safelink': ('link', 'Rules that mark URLs as unsafe.'),
    'tools.ozone.server': ('gear', 'Ozone server configuration.'),
    'tools.ozone.set': ('list-unordered', 'Named value sets that moderation rules match against.'),
    'tools.ozone.setting': ('sliders', 'Ozone instance settings.'),
    'tools.ozone.signature': ('search', 'Account signatures used to find related accounts.'),
    'tools.ozone.team': ('people', 'Ozone team members and their roles.'),
    'tools.ozone.verification': ('verified', 'Verification records issued by trusted verifiers.'),
}

# Modules that carry no NSID: the machinery the generated models are built on.
_CORE_MODULES: t.Dict[str, t.Tuple[str, str]] = {
    'base': ('package', 'Base classes every generated model inherits from.'),
    'blob_ref': ('file-media', 'References to blobs stored on a PDS.'),
    'common': ('package', 'Types shared across the generated models.'),
    'dot_dict': ('code', 'Dict wrapper that also allows attribute access.'),
    'languages': ('globe', 'ISO language codes used by posts.'),
    'models_loader': ('sync', 'Lazy import of the generated model modules.'),
    'record_registry': ('database', 'Registry mapping record NSIDs to their model.'),
    'string_formats': ('checklist', 'Validation of the AT Protocol string formats.'),
    'type_conversion': ('arrow-switch', 'Conversion between models, dicts, and raw JSON.'),
    'unknown_type': ('question', 'Fallback for records of an unrecognised type.'),
    'unknown_union': ('question', 'Fallback for union members of an unrecognised type.'),
    'utils': ('tools', 'Helpers for working with model instances.'),
}

_TYPE_ICONS: t.Dict[t.Optional[str], str] = {
    'record': 'note',
    'query': 'search',
    'procedure': 'zap',
    'subscription': 'broadcast',
    'object': 'package',
    'permission-set': 'key',
    None: 'code',
}

_GRID = '.. grid:: 1 2 2 3\n   :gutter: 3\n'


class _Page(t.NamedTuple):
    """One generated page: where it lives, what it documents, how its card reads."""

    docname: str
    module: str
    title: str
    description: str
    icon: str
    children: t.List['_Page']


def _to_snake_case(name: str) -> str:
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def _to_sentence(name: str) -> str:
    words = [word.lower() for word in re.sub('([a-z0-9])([A-Z])', r'\1 \2', name).split()]
    return ' '.join(words).capitalize() + '.'


def _escape_rst(text: str) -> str:
    text = re.sub(r'`([^`]+)`', r'``\1``', text)
    text = text.replace('*', r'\*')
    return re.sub(r'(\w)_(?=\s|$)', r'\1\\_', text)


def _first_sentence(text: str) -> str:
    match = re.match(r'^(.*?[.!?])(?:\s|$)', text, re.DOTALL)
    return match.group(1) if match else text


class _Lexicon(t.NamedTuple):
    """The card copy a lexicon file contributes to its module."""

    nsid: str
    description: str
    icon: str


def _read_lexicons() -> t.Dict[str, _Lexicon]:
    """Map the dotted module path of every lexicon to its NSID, description, and icon."""
    lexicons = {}
    for path in sorted(_LEXICONS_DIR.glob('*.json')):
        nsid = path.stem
        segments = nsid.split('.')
        module = '.'.join([*segments[:-1], _to_snake_case(segments[-1])])

        main = json.loads(path.read_text(encoding='UTF-8')).get('defs', {}).get('main') or {}
        description = main.get('description')
        if not description:
            description = 'Shared type definitions.' if segments[-1] == 'defs' else _to_sentence(segments[-1])

        lexicons[module] = _Lexicon(nsid, description, _TYPE_ICONS.get(main.get('type'), 'file-code'))

    return lexicons


def _collect(directory: Path, prefix: str, lexicons: t.Dict[str, _Lexicon]) -> t.List[_Page]:
    """Build the page tree for one package directory, sorted namespaces first."""
    namespaces, modules = [], []

    for path in sorted(directory.iterdir()):
        if path.is_dir() and (path / '__init__.py').exists():
            dotted = f'{prefix}{path.name}'
            icon, description = _NAMESPACES.get(dotted, ('file-directory', _to_sentence(path.name)))
            namespaces.append(
                _Page(
                    docname=f'models/{dotted.replace(".", "/")}/index',
                    module=f'{_MODELS_MODULE}.{dotted}',
                    title=dotted,
                    description=description,
                    icon=icon,
                    children=_collect(path, f'{dotted}.', lexicons),
                )
            )
        elif path.suffix == '.py' and path.name != '__init__.py':
            dotted = f'{prefix}{path.stem}'
            lexicon = lexicons.get(dotted)
            if lexicon:
                name, title, description, icon = (
                    lexicon.nsid.rsplit('.', 1)[-1],
                    lexicon.nsid,
                    lexicon.description,
                    lexicon.icon,
                )
            else:
                icon, description = _CORE_MODULES.get(path.stem, ('file-code', _to_sentence(path.stem)))
                name, title = path.stem, dotted
            modules.append(
                _Page(
                    docname=f'models/{"/".join([*dotted.split(".")[:-1], name])}',
                    module=f'{_MODELS_MODULE}.{dotted}',
                    title=title,
                    description=description,
                    icon=icon,
                    children=[],
                )
            )

    return namespaces + modules


def _short(page: _Page) -> str:
    """The page's own NSID segment; the surrounding tree already carries the prefix."""
    return page.title.rsplit('.', 1)[-1]


def _toctree_entries(pages: t.List[_Page]) -> str:
    return '\n'.join(f'   {_short(page)} </{page.docname}>' for page in pages)


def _render_cards(pages: t.List[_Page]) -> str:
    cards = [_GRID]
    for page in pages:
        cards.append(
            f'\n   .. grid-item-card:: :octicon:`{page.icon};1em;sd-mr-1` {_short(page)}\n'
            f'      :link: /{page.docname}\n'
            f'      :link-type: doc\n'
            f'\n'
            f'      {_escape_rst(_first_sentence(page.description))}\n'
        )
    return ''.join(cards)


_GROUPS = (
    ('lexicons', 'Lexicons', 'One page per NSID, generated from the lexicons the network publishes.'),
    ('core', 'Core', 'The hand-written machinery every generated model is built on.'),
)


def _render_section(heading: str, blurb: str, pages: t.List[_Page]) -> str:
    return f'\n{heading}\n{"-" * len(heading)}\n\n{blurb}\n\n{_render_cards(pages)}'


def _render_page(page: _Page) -> str:
    orphan = ':orphan:\n\n' if page.docname == 'models/index' else ''
    parts = [f'{orphan}{page.title}\n{"=" * len(page.title)}\n\n{_escape_rst(page.description)}\n']
    parts.append(f'\n.. automodule:: {page.module}\n   :members:\n   :show-inheritance:\n   :undoc-members:\n')

    if not page.children:
        return ''.join(parts)

    # The root mixes two unrelated things: authorities generated from lexicons/, and the
    # hand-written machinery those models are built on. Split them so the list reads.
    if page.docname == 'models/index':
        namespaces = [child for child in page.children if child.children]
        modules = [child for child in page.children if not child.children]
        for (_, heading, blurb), group in zip(_GROUPS, (namespaces, modules)):
            parts.append(_render_section(heading, blurb, group))
        return ''.join(parts)

    parts.append(f'\n{_render_cards(page.children)}')
    parts.append(f'\n.. toctree::\n   :hidden:\n   :maxdepth: 1\n\n{_toctree_entries(page.children)}\n')

    return ''.join(parts)


def _write(docname: str, content: str) -> None:
    path = _DOCS_SOURCE / f'{docname}.rst'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='UTF-8', newline='\n')


def _walk(pages: t.List[_Page]) -> t.Iterator[_Page]:
    for page in pages:
        yield page
        yield from _walk(page.children)


def _new_url(docname: str) -> str:
    """The path the page is served at after the restructure, as a site-absolute path."""
    return '/' + f'{docname.removesuffix("/index").removesuffix("index")}'.strip('/') + '/'


_MOVED_DOCNAMES: t.Dict[str, str] = {
    'readme': 'getting-started/quickstart',
    'readme.content': 'getting-started/quickstart',
    'dm': 'guides/direct-messages',
    'atproto_client/auth': 'guides/authentication',
    'atproto_client/timeouts': 'guides/error-handling',
    'atproto_client/string_formats': 'guides/string-formats',
}


def _moved_pages(pages: t.List[_Page]) -> t.Dict[str, str]:
    """Map every old page path to its new one, as site-absolute paths."""
    moves = {'atproto_client/models.html': _new_url('models/index')}

    for old, new in _MOVED_DOCNAMES.items():
        moves[old] = _new_url(new)
        moves[f'{old}.html'] = _new_url(new)
    for page in _walk(pages):
        if page.docname != 'models/index':  # the flat atproto_client.models page was never published
            moves[f'atproto/{page.module}.html'] = _new_url(page.docname)

    for path in sorted(_DOCS_SOURCE.rglob('*')):
        if path.suffix not in ('.rst', '.md') or path.is_relative_to(_OUTPUT_DIR):
            continue
        docname = path.relative_to(_DOCS_SOURCE).with_suffix('').as_posix()
        # dirhtml writes `<dir>/index.html`, which is the old path already: a stub there would
        # overwrite the real page.
        if docname == 'index' or docname.endswith('/index'):
            continue
        moves[f'{docname}.html'] = _new_url(docname)

    return dict(sorted(moves.items()))


def _write_group_pages(children: t.List[_Page]) -> None:
    """Write the two pages the sidebar hangs the models tree from.

    A toctree entry only collapses when it points at a document, so the split between generated
    and hand-written models needs a page on each side rather than a caption.
    """
    grouped = ([child for child in children if child.children], [child for child in children if not child.children])
    for (name, title, blurb), pages in zip(_GROUPS, grouped):
        _write(
            f'models/{name}',
            f'{title}\n{"=" * len(title)}\n\n{blurb}\n'
            f'\n{_render_cards(pages)}'
            f'\n.. toctree::\n   :hidden:\n   :maxdepth: 3\n\n{_toctree_entries(pages)}\n',
        )


def _write_stub_map(pages: t.List[_Page]) -> None:
    """Write the old-to-new map that sphinx-reredirects turns into stub pages at the old paths."""
    entries = ''.join(f'    {old!r}: {new!r},\n' for old, new in _moved_pages(pages).items())
    _STUB_MAP.write_text(
        f'"""Old-to-new page map for sphinx-reredirects. Generated by gen_api_docs.py."""\n\n'
        f'REDIRECTS = {{\n{entries}}}\n',
        encoding='UTF-8',
        newline='\n',
    )


def main() -> None:
    lexicons = _read_lexicons()
    children = _collect(_MODELS_PKG, '', lexicons)
    root = _Page(
        docname='models/index',
        module=_MODELS_MODULE,
        title='Models',
        description=(
            'Every lexicon of the network, generated as a Pydantic model. '
            'Browse by NSID: the authority, then the namespace, then the record or method.'
        ),
        icon='package',
        children=children,
    )

    shutil.rmtree(_OUTPUT_DIR, ignore_errors=True)
    for page in _walk([root]):
        _write(page.docname, _render_page(page))

    _write_group_pages(children)
    _write_stub_map([root])


if __name__ == '__main__':
    main()
