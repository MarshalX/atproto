import importlib
import typing as t
from functools import lru_cache
from pathlib import Path

from atproto_core.nsid import NSID
from atproto_lexicon import models
from atproto_lexicon.parser import lexicon_parse_dir

from atproto_codegen.config import CodegenConfig, get_config

LexDefs = t.Dict[
    str,
    t.Any,
]
LexDB = t.Dict[NSID, LexDefs]


def _parse_dirs(dirs: t.Tuple[Path, ...]) -> t.List[models.LexiconDoc]:
    return [lexicon for lexicon_dir in dirs for lexicon in lexicon_parse_dir(lexicon_dir)]


@lru_cache(maxsize=16)
def parse_lexicons(config: CodegenConfig) -> t.Tuple[models.LexiconDoc, ...]:
    return tuple(_parse_dirs(config.emit_lexicon_dirs))


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


def is_record(nsid: NSID, config: t.Optional[CodegenConfig] = None) -> bool:
    """Return whether ``#main`` of a lexicon is a record, in the emitted lexicons or the referenced package."""
    if config is None:
        config = get_config()

    if 'main' in build_record_models(config).get(nsid, {}):
        return True

    return str(nsid) in reference_record_types(config)


def _filter_defs_by_type(defs: t.Dict[str, models.LexDefinition], def_types: t.AbstractSet[str]) -> LexDefs:
    return {k: v for k, v in defs.items() if v.type in def_types}


def _build_nsid_to_defs_map(lexicons: t.Sequence[models.LexiconDoc], def_types: t.AbstractSet[str]) -> LexDB:
    result = {}

    for lexicon in lexicons:
        nsid = NSID.from_str(lexicon.id)
        defs = _filter_defs_by_type(lexicon.defs, def_types)
        if defs:
            result[nsid] = defs

    return result


def _build(def_types: t.AbstractSet[str], config: t.Optional[CodegenConfig]) -> LexDB:
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

_LEX_DEF_TYPES_FOR_PARAMS = {
    models.LexDefinitionType.QUERY,
    models.LexDefinitionType.PROCEDURE,
    models.LexDefinitionType.SUBSCRIPTION,
}


def build_params_models(config: t.Optional[CodegenConfig] = None) -> BuiltParamsModels:
    return _build(_LEX_DEF_TYPES_FOR_PARAMS, config)


BuiltDataModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexXrpcProcedure]]]

_LEX_DEF_TYPES_FOR_DATA = {models.LexDefinitionType.PROCEDURE}


def build_data_models(config: t.Optional[CodegenConfig] = None) -> BuiltDataModels:
    return _build(_LEX_DEF_TYPES_FOR_DATA, config)


BuiltResponseModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexXrpcQuery, models.LexXrpcProcedure]]]

_LEX_DEF_TYPES_FOR_RESPONSES = {models.LexDefinitionType.QUERY, models.LexDefinitionType.PROCEDURE}


def build_response_models(config: t.Optional[CodegenConfig] = None) -> BuiltResponseModels:
    return _build(_LEX_DEF_TYPES_FOR_RESPONSES, config)


BuiltDefModels = t.Dict[
    NSID, t.Dict[str, t.Union[models.LexObject, models.LexString, models.LexToken, models.LexArray]]
]

_LEX_DEF_TYPES_FOR_DEF = {
    models.LexDefinitionType.OBJECT,
    models.LexPrimitiveType.STRING,
    models.LexDefinitionType.TOKEN,
    models.LexDefinitionType.ARRAY,
}


def build_def_models(config: t.Optional[CodegenConfig] = None) -> BuiltDefModels:
    return _build(_LEX_DEF_TYPES_FOR_DEF, config)


BuiltRecordModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexRecord]]]

_LEX_DEF_TYPES_FOR_RECORDS = {models.LexDefinitionType.RECORD}


def build_record_models(config: t.Optional[CodegenConfig] = None) -> BuiltRecordModels:
    return _build(_LEX_DEF_TYPES_FOR_RECORDS, config)


BuiltSubscriptions = t.Dict[NSID, t.Dict[str, models.LexSubscription]]

_LEX_DEF_TYPES_FOR_SUBSCRIPTIONS = {models.LexDefinitionType.SUBSCRIPTION}


def build_subscriptions(config: t.Optional[CodegenConfig] = None) -> BuiltSubscriptions:
    return _build(_LEX_DEF_TYPES_FOR_SUBSCRIPTIONS, config)
