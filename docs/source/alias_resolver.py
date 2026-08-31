import types
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
    'AtprotoData': 'atproto_identity.did.atproto_data.AtprotoData',
    'CachedDidResult': 'atproto_identity.cache.models.CachedDidResult',
    'DidDocument': 'atproto_core.did_doc.DidDocument',
    # external types named bare in docstrings, resolved through intersphinx
    'FieldInfo': 'pydantic.fields.FieldInfo',
    'ModuleType': 'types.ModuleType',
    'NoneType': 'types.NoneType',
    'DotDict': 'atproto_client.models.dot_dict.DotDict',
    'SubscribeEventsMessage': 'atproto_jetstream.models.SubscribeEventsMessage',
    'atproto.CAR': 'atproto_core.car.CAR',
    'atproto.xrpc_client.models.base.DotDict': 'atproto_client.models.dot_dict.DotDict',
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


_MODELS_MODULE_PREFIX = 'atproto_client.models.'


def _to_camel_case(name: str) -> str:
    head, *tail = name.split('_')
    return head + ''.join(part.title() for part in tail)


def _build_nsid_aliases_db() -> t.Dict[str, str]:
    """Index the generated model modules by the lexicon NSID each one was generated from.

    Lexicon descriptions name other lexicons by NSID, and every such mention is a reference target that
    resolves to nothing on its own. Codegen snake-cases the last segment, so ``app.bsky.actor.getProfile``
    is documented as ``atproto_client.models.app.bsky.actor.get_profile``.

    Returns:
        NSID to module path.
    """
    nsid_aliases_db = {}
    for module in ALIASES_DB.values():
        if not module.startswith(_MODELS_MODULE_PREFIX):
            continue

        *namespace, name = module[len(_MODELS_MODULE_PREFIX) :].split('.')
        nsid_aliases_db['.'.join([*namespace, _to_camel_case(name)])] = module

    return nsid_aliases_db


_NSID_ALIASES_DB = _build_nsid_aliases_db()


def _build_exception_aliases_db() -> t.Dict[str, str]:
    """Index every exception re-exported by ``atproto.exceptions`` under the path it is documented at.

    Docstrings name exceptions by the import path users write, while each one is documented under the
    package that defines it.

    Returns:
        Re-exported path to documented path.
    """
    import atproto.exceptions

    return {
        f'atproto.exceptions.{name}': f'{obj.__module__}.{name}'
        for name, obj in vars(atproto.exceptions).items()
        if isinstance(obj, type) and issubclass(obj, BaseException)
    }


_EXCEPTION_ALIASES_DB = _build_exception_aliases_db()


def _get_model_alias(alias: str) -> t.Optional[str]:
    # FIXME(MarshalX): Resolving of models.AppBskyGraphDefs ListPurpose is not working.
    alias_split = alias.rsplit('.', maxsplit=1)
    if len(alias_split) < 2:
        return None

    alias_prefix, alias_suffix = alias_split
    if alias_prefix not in ALIASES_DB:
        return None

    return f'{ALIASES_DB[alias_prefix]}.{alias_suffix}'


def _build_module_prefixes() -> t.Dict[str, str]:
    """Map the module paths docstrings use onto the ones the modules are documented under.

    ``atproto`` re-exports whole modules under shorter names, and the client package was once called
    ``atproto.xrpc_client``.

    Returns:
        Prefix as written to prefix as documented.
    """
    import atproto

    prefixes = {'atproto.xrpc_client.': 'atproto_client.'}
    for name, obj in vars(atproto).items():
        if not isinstance(obj, types.ModuleType) or name.startswith('_'):
            continue

        prefix, target = f'atproto.{name}.', f'{obj.__name__}.'
        if prefix != target:
            prefixes[prefix] = target

    return prefixes


_RENAMED_MODULE_PREFIXES = _build_module_prefixes()


def _get_renamed_module_alias(alias: str) -> t.Optional[str]:
    """Rewrite a path that a docstring still spells with a package's former name."""
    for old_prefix, new_prefix in _RENAMED_MODULE_PREFIXES.items():
        if alias.startswith(old_prefix):
            return f'{new_prefix}{alias[len(old_prefix) :]}'

    return None


def get_alias_from_db(alias: str) -> t.Optional[str]:
    model_alias = _get_model_alias(alias)
    if model_alias:
        return model_alias

    nsid_alias = _NSID_ALIASES_DB.get(alias)
    if nsid_alias:
        return nsid_alias

    exception_alias = _EXCEPTION_ALIASES_DB.get(alias)
    if exception_alias:
        return exception_alias

    global_alias = _GLOBAL_ALIASES_DB.get(alias)
    if global_alias:
        return global_alias

    return _get_renamed_module_alias(alias)


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
