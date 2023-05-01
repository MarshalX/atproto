from typing import Dict, List, Union

from lexicon.models import (
    LexDefinition,
    LexDefinitionType,
    LexiconDoc,
    LexXrpcProcedure,
    LexXrpcQuery,
)
from lexicon.parser import lexicon_parse_dir
from nsid import NSID

_LEX_DEF_TYPES_FOR_PARAMS = {LexDefinitionType.QUERY, LexDefinitionType.PROCEDURE}
_LEX_DEF_TYPES_FOR_RESPONSES = {LexDefinitionType.QUERY, LexDefinitionType.PROCEDURE}
_LEX_DEF_TYPES_FOR_DATA = {LexDefinitionType.PROCEDURE}

LexDefs = Dict[str, Union[LexXrpcProcedure, LexXrpcQuery]]
LexDB = Dict[NSID, LexDefs]


def _filter_defs_by_type(defs: Dict[str, LexDefinition], def_types: set) -> LexDefs:
    return {k: v for k, v in defs.items() if v.type in def_types}


def _build_nsid_to_defs_map(lexicons: List[LexiconDoc], def_types: set) -> LexDB:
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


if __name__ == '__main__':
    build_params_models()
    build_data_models()
    build_response_models()
