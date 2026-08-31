import typing as t

import pytest

pytest.importorskip('sphinx', reason='the docs dependency group is installed on Python 3.12+ only')

from docs.source.alias_resolver import get_alias_from_db

_RESOLVED = [
    # a lexicon NSID, as lexicon prose names it. Codegen snake-cases the last segment
    ('app.bsky.actor.getProfile', 'atproto_client.models.app.bsky.actor.get_profile'),
    ('app.bsky.actor.defs', 'atproto_client.models.app.bsky.actor.defs'),
    (
        'app.bsky.actor.contentVisibilityDeclaration',
        'atproto_client.models.app.bsky.actor.content_visibility_declaration',
    ),
    ('com.atproto.repo.putRecord', 'atproto_client.models.com.atproto.repo.put_record'),
    # an exception, as docstrings name it: the path it is imported from, not the one it is documented at
    ('atproto.exceptions.AtProtocolError', 'atproto_core.exceptions.AtProtocolError'),
    ('atproto.exceptions.JetstreamDecodingError', 'atproto_jetstream.exceptions.JetstreamDecodingError'),
    # a model attribute, through the import alias the generated models are annotated with
    ('models.AppBskyActorDefs.ProfileView', 'atproto_client.models.app.bsky.actor.defs.ProfileView'),
    ('DotDict', 'atproto_client.models.dot_dict.DotDict'),
]

_UNTOUCHED = [
    'pathlib.Path',
    'enum.Enum',
    'typing.Optional',
    't.Literal',
    'self',
    'DEPRECATED',
    'atproto.exceptions.NotAnError',
]


@pytest.mark.parametrize(('alias', 'expected'), _RESOLVED)
def test_alias_resolves_to_its_documented_path(alias: str, expected: str) -> None:
    assert get_alias_from_db(alias) == expected


@pytest.mark.parametrize('alias', _UNTOUCHED)
def test_unrelated_target_is_left_alone(alias: str) -> None:
    """Rewriting a target that is not ours would point the reader at a page that does not exist."""
    assert get_alias_from_db(alias) is None


def test_every_model_module_is_reachable_by_its_nsid() -> None:
    """Every generated model module must be reachable from the NSID its lexicon is named by.

    Nothing else catches a break here: the docs build is not nitpicky, so an alias that stops resolving
    renders as plain text instead of a link, silently.
    """
    from docs.source.aliases_db import ALIASES_DB

    prefix = 'atproto_client.models.'
    modules = {module for module in ALIASES_DB.values() if module.startswith(prefix)}
    unreachable: t.List[str] = []

    for module in modules:
        *namespace, name = module[len(prefix) :].split('.')
        nsid = '.'.join([*namespace, name])
        if get_alias_from_db(nsid) != module and get_alias_from_db(_to_camel(nsid)) != module:
            unreachable.append(module)

    assert not unreachable, f'model modules with no NSID alias: {sorted(unreachable)[:10]}'


def _to_camel(nsid: str) -> str:
    *namespace, name = nsid.split('.')
    head, *tail = name.split('_')
    return '.'.join([*namespace, head + ''.join(part.title() for part in tail)])
