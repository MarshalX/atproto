import typing as t
from enum import Enum
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


class Scope(Enum):
    """Which lexicons a database is built from."""

    EMIT = 'emit'
    """Only the lexicons code is generated for."""

    ALL = 'all'
    """The emitted lexicons plus the ones parsed to resolve references into."""


def _parse_dirs(dirs: t.Tuple[Path, ...]) -> t.List[models.LexiconDoc]:
    return [lexicon for lexicon_dir in dirs for lexicon in lexicon_parse_dir(lexicon_dir)]


@lru_cache(maxsize=16)
def parse_lexicons(config: CodegenConfig, scope: Scope) -> t.Tuple[models.LexiconDoc, ...]:
    emitted = _parse_dirs(config.emit_lexicon_dirs)
    if scope is Scope.EMIT:
        return tuple(emitted)

    # references first so that an emitted lexicon wins over a reference one with the same ID
    by_id = {lexicon.id: lexicon for lexicon in (*_parse_dirs(config.ref_lexicon_dirs), *emitted)}
    return tuple(by_id.values())


def _filter_defs_by_type(
    defs: t.Dict[str, models.LexDefinition], def_types: t.Union[t.Set['models.LexDefinitionType'], t.Set['Enum']]
) -> LexDefs:
    return {k: v for k, v in defs.items() if v.type in def_types}


def _build_nsid_to_defs_map(
    lexicons: t.Sequence[models.LexiconDoc], def_types: t.Union[t.Set['models.LexDefinitionType'], t.Set['Enum']]
) -> LexDB:
    result = {}

    for lexicon in lexicons:
        nsid = NSID.from_str(lexicon.id)
        defs = _filter_defs_by_type(lexicon.defs, def_types)
        if defs:
            result[nsid] = defs

    return result


def _build(
    def_types: t.Union[t.Set['models.LexDefinitionType'], t.Set['Enum']],
    config: t.Optional[CodegenConfig],
    scope: Scope,
) -> LexDB:
    if config is None:
        config = get_config()

    return _build_nsid_to_defs_map(parse_lexicons(config, scope), def_types)


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


def build_params_models(config: t.Optional[CodegenConfig] = None, scope: Scope = Scope.EMIT) -> BuiltParamsModels:
    return _build(_LEX_DEF_TYPES_FOR_PARAMS, config, scope)


BuiltDataModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexXrpcProcedure]]]

_LEX_DEF_TYPES_FOR_DATA = {models.LexDefinitionType.PROCEDURE}


def build_data_models(config: t.Optional[CodegenConfig] = None, scope: Scope = Scope.EMIT) -> BuiltDataModels:
    return _build(_LEX_DEF_TYPES_FOR_DATA, config, scope)


BuiltResponseModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexXrpcQuery, models.LexXrpcProcedure]]]

_LEX_DEF_TYPES_FOR_RESPONSES = {models.LexDefinitionType.QUERY, models.LexDefinitionType.PROCEDURE}


def build_response_models(config: t.Optional[CodegenConfig] = None, scope: Scope = Scope.EMIT) -> BuiltResponseModels:
    return _build(_LEX_DEF_TYPES_FOR_RESPONSES, config, scope)


BuiltDefModels = t.Dict[
    NSID, t.Dict[str, t.Union[models.LexObject, models.LexString, models.LexToken, models.LexArray]]
]

_LEX_DEF_TYPES_FOR_DEF = {
    models.LexDefinitionType.OBJECT,
    models.LexPrimitiveType.STRING,
    models.LexDefinitionType.TOKEN,
    models.LexDefinitionType.ARRAY,
}


def build_def_models(config: t.Optional[CodegenConfig] = None, scope: Scope = Scope.EMIT) -> BuiltDefModels:
    return _build(_LEX_DEF_TYPES_FOR_DEF, config, scope)


BuiltRecordModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexRecord]]]

_LEX_DEF_TYPES_FOR_RECORDS = {models.LexDefinitionType.RECORD}


def build_record_models(config: t.Optional[CodegenConfig] = None, scope: Scope = Scope.EMIT) -> BuiltRecordModels:
    return _build(_LEX_DEF_TYPES_FOR_RECORDS, config, scope)
