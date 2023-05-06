from typing import Dict, List, Union

from atproto.lexicon import models
from atproto.lexicon.parser import lexicon_parse_dir
from atproto.nsid import NSID

_LEX_DEF_TYPES_FOR_PARAMS = {models.LexDefinitionType.QUERY, models.LexDefinitionType.PROCEDURE}
_LEX_DEF_TYPES_FOR_RESPONSES = {models.LexDefinitionType.QUERY, models.LexDefinitionType.PROCEDURE}
_LEX_DEF_TYPES_FOR_REFS = {models.LexDefinitionType.QUERY, models.LexDefinitionType.PROCEDURE}
_LEX_DEF_TYPES_FOR_DATA = {models.LexDefinitionType.PROCEDURE}
_LEX_DEF_TYPES_FOR_RECORDS = {models.LexDefinitionType.RECORD}
_LEX_DEF_TYPES_FOR_DEF = {
    models.LexDefinitionType.OBJECT,
    models.LexPrimitiveType.STRING,
    models.LexDefinitionType.TOKEN,
}

LexDefs = Dict[
    str,
    Union[
        models.LexXrpcProcedure,
        models.LexXrpcQuery,
        models.LexObject,
        models.LexToken,
        models.LexString,
        models.LexRecord,
    ],
]
LexDB = Dict[NSID, LexDefs]


def _filter_defs_by_type(defs: Dict[str, models.LexDefinition], def_types: set) -> LexDefs:
    return {k: v for k, v in defs.items() if v.type in def_types}


def _build_nsid_to_defs_map(lexicons: List[models.LexiconDoc], def_types: set) -> LexDB:
    result = {}

    for lexicon in lexicons:
        nsid = NSID.from_str(lexicon.id)
        defs = _filter_defs_by_type(lexicon.defs, def_types)
        if defs:
            result[nsid] = defs

    return result


def build_params_models() -> LexDB:
    return _build_nsid_to_defs_map(lexicon_parse_dir(), _LEX_DEF_TYPES_FOR_PARAMS)


def build_data_models() -> LexDB:
    return _build_nsid_to_defs_map(lexicon_parse_dir(), _LEX_DEF_TYPES_FOR_DATA)


def build_response_models() -> LexDB:
    return _build_nsid_to_defs_map(lexicon_parse_dir(), _LEX_DEF_TYPES_FOR_RESPONSES)


def build_def_models() -> LexDB:
    return _build_nsid_to_defs_map(lexicon_parse_dir(), _LEX_DEF_TYPES_FOR_DEF)


def build_record_models() -> LexDB:
    return _build_nsid_to_defs_map(lexicon_parse_dir(), _LEX_DEF_TYPES_FOR_RECORDS)


def build_refs_models() -> LexDB:
    return _build_nsid_to_defs_map(lexicon_parse_dir(), _LEX_DEF_TYPES_FOR_REFS)


if __name__ == '__main__':
    build_params_models()
    build_data_models()
    build_response_models()
    build_def_models()
    build_record_models()
    build_refs_models()
