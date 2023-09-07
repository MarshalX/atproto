import typing as t
from pathlib import Path

from atproto.lexicon import models
from atproto.lexicon.parser import lexicon_parse_dir
from atproto.nsid import NSID

if t.TYPE_CHECKING:
    from enum import Enum

LexDefs = t.Dict[
    str,
    t.Any,
]
LexDB = t.Dict[NSID, LexDefs]


class _LexiconDir:
    dir_path: t.Optional[Path]

    def __init__(self, default_path: t.Optional[Path] = None) -> None:
        self.dir_path = default_path

    def set(self, path: Path) -> None:
        self.dir_path = path

    def get(self) -> t.Optional[Path]:
        return self.dir_path


lexicon_dir = _LexiconDir()


def _filter_defs_by_type(
    defs: t.Dict[str, models.LexDefinition], def_types: t.Union[t.Set['models.LexDefinitionType'], t.Set['Enum']]
) -> LexDefs:
    return {k: v for k, v in defs.items() if v.type in def_types}


def _build_nsid_to_defs_map(
    lexicons: t.List[models.LexiconDoc], def_types: t.Union[t.Set['models.LexDefinitionType'], t.Set['Enum']]
) -> LexDB:
    result = {}

    for lexicon in lexicons:
        nsid = NSID.from_str(lexicon.id)
        defs = _filter_defs_by_type(lexicon.defs, def_types)
        if defs:
            result[nsid] = defs

    return result


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


def build_params_models() -> BuiltParamsModels:
    _LEX_DEF_TYPES_FOR_PARAMS = {
        models.LexDefinitionType.QUERY,
        models.LexDefinitionType.PROCEDURE,
        models.LexDefinitionType.SUBSCRIPTION,
    }
    return _build_nsid_to_defs_map(lexicon_parse_dir(lexicon_dir.get()), _LEX_DEF_TYPES_FOR_PARAMS)


BuiltDataModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexXrpcProcedure]]]


def build_data_models() -> BuiltDataModels:
    _LEX_DEF_TYPES_FOR_DATA = {models.LexDefinitionType.PROCEDURE}
    return _build_nsid_to_defs_map(lexicon_parse_dir(lexicon_dir.get()), _LEX_DEF_TYPES_FOR_DATA)


BuiltResponseModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexXrpcQuery, models.LexXrpcProcedure]]]


def build_response_models() -> BuiltResponseModels:
    _LEX_DEF_TYPES_FOR_RESPONSES = {models.LexDefinitionType.QUERY, models.LexDefinitionType.PROCEDURE}
    return _build_nsid_to_defs_map(lexicon_parse_dir(lexicon_dir.get()), _LEX_DEF_TYPES_FOR_RESPONSES)


BuiltDefModels = t.Dict[
    NSID, t.Dict[str, t.Union[models.LexObject, models.LexString, models.LexToken, models.LexArray]]
]


def build_def_models() -> BuiltDefModels:
    _LEX_DEF_TYPES_FOR_DEF = {
        models.LexDefinitionType.OBJECT,
        models.LexPrimitiveType.STRING,
        models.LexDefinitionType.TOKEN,
        models.LexDefinitionType.ARRAY,
    }
    return _build_nsid_to_defs_map(lexicon_parse_dir(lexicon_dir.get()), _LEX_DEF_TYPES_FOR_DEF)


BuiltRecordModels = t.Dict[NSID, t.Dict[str, t.Union[models.LexRecord]]]


def build_record_models() -> BuiltRecordModels:
    _LEX_DEF_TYPES_FOR_RECORDS = {models.LexDefinitionType.RECORD}
    return _build_nsid_to_defs_map(lexicon_parse_dir(lexicon_dir.get()), _LEX_DEF_TYPES_FOR_RECORDS)


if __name__ == '__main__':
    build_params_models()
    build_data_models()
    build_response_models()
    build_def_models()
    build_record_models()
