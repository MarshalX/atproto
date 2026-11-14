import importlib
import typing as t
from functools import lru_cache
from pathlib import Path

from atproto_core.nsid import NSID
from atproto_lexicon import models
from atproto_lexicon.exceptions import LexiconParsingError
from atproto_lexicon.parser import lexicon_parse_dir

from atproto_codegen.config import CodegenConfig, get_config
from atproto_codegen.diagnostics import warn
from atproto_codegen.exceptions import LexiconsNotFoundError

_D = t.TypeVar('_D')


def _report_skipped_lexicon(path: Path, error: LexiconParsingError) -> None:
    warn(f'Skipped {path.name}: {str(error).split(": ", 1)[-1]}')


def _parse_dirs(dirs: t.Tuple[Path, ...], *, skip_invalid: bool) -> t.List[models.LexiconDoc]:
    on_error = _report_skipped_lexicon if skip_invalid else None
    return [lexicon for lexicon_dir in dirs for lexicon in lexicon_parse_dir(lexicon_dir, on_error=on_error)]


@lru_cache(maxsize=16)
def parse_lexicons(config: CodegenConfig) -> t.Tuple[models.LexiconDoc, ...]:
    """Parse the lexicons to generate code for.

    Raises:
        LexiconsNotFoundError: A lexicon directory does not exist or holds no lexicons.
    """
    for lexicon_dir in config.emit_lexicon_dirs:
        if not lexicon_dir.is_dir():
            raise LexiconsNotFoundError(f'Lexicon directory does not exist: {lexicon_dir}')

    lexicons = tuple(_parse_dirs(config.emit_lexicon_dirs, skip_invalid=config.skip_invalid))
    if not lexicons:
        dirs = ', '.join(str(d) for d in config.emit_lexicon_dirs)
        if config.skip_invalid and any(
            next(lexicon_dir.rglob('*.json'), None) for lexicon_dir in config.emit_lexicon_dirs
        ):
            raise LexiconsNotFoundError(f'None of the .json lexicons could be parsed in: {dirs}')
        raise LexiconsNotFoundError(f'No .json lexicons found in: {dirs}')

    return lexicons


@lru_cache(maxsize=16)
def emitted_nsids(config: CodegenConfig) -> t.FrozenSet[NSID]:
    return frozenset(NSID.from_str(lexicon.id) for lexicon in parse_lexicons(config))


def reference_model_exists(nsid: NSID, alias: str, model_name: str, config: t.Optional[CodegenConfig] = None) -> bool:
    """Return whether a referenced model is being generated or exists in the package the run falls back to.

    Definitions of the emitted lexicons are taken as present; a wrong ``#name`` inside them fails on import
    of the generated code. Foreign references are looked up in the installed base package.
    """
    if config is None:
        config = get_config()

    if nsid in emitted_nsids(config):
        return True
    if config.is_self_gen:
        return False

    models_module = importlib.import_module(f'{config.base_package}.models')
    try:
        module = getattr(models_module, alias)
    except AttributeError:
        return False

    return hasattr(module, model_name)


@lru_cache(maxsize=16)
def reference_record_types(config: CodegenConfig) -> t.FrozenSet[str]:
    """Return the NSIDs of the records a reference out of the emitted code may name without emitting them.

    They are read from the record table of the package the generated models fall back to at runtime,
    so a reference can only name a record the installed package resolves.
    """
    if config.is_self_gen:
        return frozenset()

    type_conversion = importlib.import_module(f'{config.base_package}.models.type_conversion')
    return frozenset(type_conversion.RECORD_TYPES)


@lru_cache(maxsize=16)
def _emitted_defs(config: CodegenConfig) -> t.Dict[NSID, t.Dict[str, models.LexDefinition]]:
    return {NSID.from_str(lexicon.id): lexicon.defs for lexicon in parse_lexicons(config)}


@lru_cache(maxsize=16)
def _emitted_aliases(config: CodegenConfig) -> t.Dict[NSID, str]:
    from atproto_codegen.utils import build_aliases

    return build_aliases(emitted_nsids(config))


def get_alias(nsid: NSID, config: t.Optional[CodegenConfig] = None) -> t.Optional[str]:
    """Return the name the model module of an emitted lexicon is exposed under."""
    return _emitted_aliases(config or get_config()).get(nsid)


def get_defs(nsid: NSID, config: t.Optional[CodegenConfig] = None) -> t.Dict[str, models.LexDefinition]:
    """Return the definitions of an emitted lexicon. Empty for a lexicon that is not emitted."""
    return _emitted_defs(config or get_config()).get(nsid, {})


def is_token(nsid: NSID, def_name: str, alias: str, model_name: str, config: t.Optional[CodegenConfig] = None) -> bool:
    """Return whether a definition is a token, in the emitted lexicons or the referenced package."""
    if config is None:
        config = get_config()

    if nsid in emitted_nsids(config):
        return isinstance(get_defs(nsid, config).get(def_name), models.LexToken)

    return reference_model_exists(nsid, alias, model_name, config)


def clear_caches() -> None:
    """Forget parsed lexicons so that a new run sees lexicons edited since the previous one in this process."""
    parse_lexicons.cache_clear()
    emitted_nsids.cache_clear()
    _emitted_defs.cache_clear()
    _emitted_aliases.cache_clear()
    reference_record_types.cache_clear()


def is_record(nsid: NSID, config: t.Optional[CodegenConfig] = None) -> bool:
    """Return whether ``#main`` of a lexicon is a record, in the emitted lexicons or the referenced package."""
    if config is None:
        config = get_config()

    if 'main' in build_record_models(config).get(nsid, {}):
        return True

    return str(nsid) in reference_record_types(config)


def _filter_defs_by_type(
    defs: t.Dict[str, models.LexDefinition], def_types: t.Tuple[t.Type[_D], ...]
) -> t.Dict[str, _D]:
    return {k: v for k, v in defs.items() if isinstance(v, def_types)}


def _build_nsid_to_defs_map(
    lexicons: t.Sequence[models.LexiconDoc], def_types: t.Tuple[t.Type[_D], ...]
) -> t.Dict[NSID, t.Dict[str, _D]]:
    result = {}

    for lexicon in lexicons:
        nsid = NSID.from_str(lexicon.id)
        defs = _filter_defs_by_type(lexicon.defs, def_types)
        if defs:
            result[nsid] = defs

    return result


def _build(def_types: t.Tuple[t.Type[_D], ...], config: t.Optional[CodegenConfig]) -> t.Dict[NSID, t.Dict[str, _D]]:
    if config is None:
        config = get_config()

    return _build_nsid_to_defs_map(parse_lexicons(config), def_types)


BuiltParamsModels = t.Dict[
    NSID,
    t.Dict[
        str,
        t.Union[
            models.LexXrpcQuery,
            models.LexXrpcProcedure,
            models.LexSubscription,
        ],
    ],
]

_LEX_DEF_TYPES_FOR_PARAMS = (models.LexXrpcQuery, models.LexXrpcProcedure, models.LexSubscription)


def build_params_models(config: t.Optional[CodegenConfig] = None) -> BuiltParamsModels:
    return _build(_LEX_DEF_TYPES_FOR_PARAMS, config)


BuiltDataModels = t.Dict[NSID, t.Dict[str, models.LexXrpcProcedure]]

_LEX_DEF_TYPES_FOR_DATA = (models.LexXrpcProcedure,)


def build_data_models(config: t.Optional[CodegenConfig] = None) -> BuiltDataModels:
    return _build(_LEX_DEF_TYPES_FOR_DATA, config)


BuiltResponseModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexXrpcQuery, models.LexXrpcProcedure]]]

_LEX_DEF_TYPES_FOR_RESPONSES = (models.LexXrpcQuery, models.LexXrpcProcedure)


def build_response_models(config: t.Optional[CodegenConfig] = None) -> BuiltResponseModels:
    return _build(_LEX_DEF_TYPES_FOR_RESPONSES, config)


BuiltDefModels = t.Dict[
    NSID,
    t.Dict[
        str,
        t.Union[
            models.LexObject,
            models.LexToken,
            models.LexArray,
            models.LexBlob,
            models.LexBoolean,
            models.LexBytes,
            models.LexCidLink,
            models.LexInteger,
            models.LexString,
        ],
    ],
]

_LEX_DEF_TYPES_FOR_DEF = (
    models.LexObject,
    models.LexToken,
    models.LexArray,
    models.LexBlob,
    models.LexBoolean,
    models.LexBytes,
    models.LexCidLink,
    models.LexInteger,
    models.LexString,
)


def build_def_models(config: t.Optional[CodegenConfig] = None) -> BuiltDefModels:
    return _build(_LEX_DEF_TYPES_FOR_DEF, config)


BuiltRecordModels = t.Dict[NSID, t.Dict[str, models.LexRecord]]

_LEX_DEF_TYPES_FOR_RECORDS = (models.LexRecord,)


def build_record_models(config: t.Optional[CodegenConfig] = None) -> BuiltRecordModels:
    return _build(_LEX_DEF_TYPES_FOR_RECORDS, config)


BuiltPermissionSets = t.Dict[NSID, t.Dict[str, models.LexPermissionSet]]

_LEX_DEF_TYPES_FOR_PERMISSION_SETS = (models.LexPermissionSet,)


def build_permission_sets(config: t.Optional[CodegenConfig] = None) -> BuiltPermissionSets:
    return _build(_LEX_DEF_TYPES_FOR_PERMISSION_SETS, config)


BuiltSubscriptions = t.Dict[NSID, t.Dict[str, models.LexSubscription]]

_LEX_DEF_TYPES_FOR_SUBSCRIPTIONS = (models.LexSubscription,)


def build_subscriptions(config: t.Optional[CodegenConfig] = None) -> BuiltSubscriptions:
    return _build(_LEX_DEF_TYPES_FOR_SUBSCRIPTIONS, config)
