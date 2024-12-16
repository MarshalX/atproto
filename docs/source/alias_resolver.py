import typing as t

from sphinx.addnodes import pending_xref
from sphinx.ext.intersphinx import missing_reference

from docs.source.aliases_db import ALIASES_DB

if t.TYPE_CHECKING:
    from docutils.nodes import Element, Node, TextElement
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


# FIXME(MarshalX): I didn't find a fast way to fix aliases resolving after migration to Pydantic.
#  I hope this is temporary and resolving will be on the Sphinx side.

_GLOBAL_ALIASES_DB = {
    'string_formats.validate_at_uri': 'atproto_client.models.string_formats.validate_at_uri',
    'string_formats.validate_cid': 'atproto_client.models.string_formats.validate_cid',
    'string_formats.validate_datetime': 'atproto_client.models.string_formats.validate_datetime',
    'string_formats.validate_did': 'atproto_client.models.string_formats.validate_did',
    'string_formats.validate_handle': 'atproto_client.models.string_formats.validate_handle',
    'string_formats.validate_language': 'atproto_client.models.string_formats.validate_language',
    'string_formats.validate_nsid': 'atproto_client.models.string_formats.validate_nsid',
    'string_formats.validate_record_key': 'atproto_client.models.string_formats.validate_record_key',
    'string_formats.validate_tid': 'atproto_client.models.string_formats.validate_tid',
    'string_formats.validate_uri': 'atproto_client.models.string_formats.validate_uri',
}


def _get_model_alias(alias: str) -> t.Optional[str]:
    # FIXME(MarshalX): Resolving of models.AppBskyGraphDefs ListPurpose is not working.
    alias_split = alias.rsplit('.', maxsplit=1)
    if len(alias_split) < 2:
        return None

    alias_prefix, alias_suffix = alias_split
    if alias_prefix not in ALIASES_DB:
        return None

    return f'{ALIASES_DB[alias_prefix]}.{alias_suffix}'


def get_alias_from_db(alias: str) -> t.Optional[str]:
    model_alias = _get_model_alias(alias)
    if model_alias:
        return model_alias

    return _GLOBAL_ALIASES_DB.get(alias)


# annotate
def resolve_intersphinx_aliases(
    app: 'Sphinx', env: 'BuildEnvironment', node: pending_xref, contnode: 'TextElement'
) -> t.Optional['Element']:
    alias = node.get('reftarget', None)
    if alias is None:
        return None

    resolved_alias = get_alias_from_db(alias)
    if resolved_alias:
        node['reftarget'] = resolved_alias
        return missing_reference(app, env, node, contnode)

    return None


def resolve_internal_aliases(_: 'Sphinx', doctree: 'Node') -> None:
    for node in doctree.traverse(condition=pending_xref):
        alias = node.get('reftarget', None)
        if alias is None:
            continue

        resolved_alias = get_alias_from_db(alias)
        if resolved_alias:
            node['reftarget'] = resolved_alias
