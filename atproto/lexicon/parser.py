import json
import os
from enum import Enum
from pathlib import Path

import dacite
import models
from exceptions import UnknownDefinitionTypeError, UnknownPrimitiveTypeError

_PATH_TO_LEXICONS = Path(__file__).parent.parent.parent.joinpath('lexicons').absolute()

_LEX_DEFINITION_TYPE_TO_CLASS = {
    models.LexDefinitionType.PROCEDURE: models.LexXrpcProcedure,
    models.LexDefinitionType.QUERY: models.LexXrpcQuery,
    models.LexDefinitionType.TOKEN: models.LexToken,
    models.LexDefinitionType.OBJECT: models.LexObject,
}

_LEX_PRIMITIVE_TYPE_TO_CLASS = {
    models.LexPrimitiveType.BOOLEAN: models.LexBoolean,
    models.LexPrimitiveType.NUMBER: models.LexNumber,
    models.LexPrimitiveType.INTEGER: models.LexInteger,
    models.LexPrimitiveType.STRING: models.LexString,
    models.LexPrimitiveType.REF: models.LexRef,  # not 100% sure cuz not documented
}


def _lex_definition_type_hook(data: dict) -> models.LexDefinition:
    try:
        definition_class = _LEX_DEFINITION_TYPE_TO_CLASS.get(models.LexDefinitionType(data['type']))
    except (ValueError, KeyError):
        raise UnknownDefinitionTypeError(data['type'])

    return lexicon_parse(data, definition_class)


def _lex_primitive_type_hook(data: dict) -> models.LexPrimitive:
    try:
        primitive_class = _LEX_PRIMITIVE_TYPE_TO_CLASS.get(models.LexPrimitiveType(data['type']))
    except (ValueError, KeyError):
        raise UnknownPrimitiveTypeError

    return lexicon_parse(data, primitive_class)


_TYPE_HOOKS = {models.LexDefinition: _lex_definition_type_hook, models.LexPrimitive: _lex_primitive_type_hook}
_DEFAULT_DACITE_CONFIG = dacite.Config(cast=[Enum], type_hooks=_TYPE_HOOKS)


def lexicon_parse(data: dict, data_class=None):
    if not data_class:
        data_class = models.LexiconDoc

    return dacite.from_dict(data_class=data_class, data=data, config=_DEFAULT_DACITE_CONFIG)


def main(lexicon_path: Path):
    with open(lexicon_path, 'r', encoding='UTF-8') as f:
        plain_lexicon = json.loads(f.read())

    return lexicon_parse(plain_lexicon)


if __name__ == '__main__':
    for _, _, lexicons in os.walk(_PATH_TO_LEXICONS):
        for lexicon in lexicons:
            lexicon_doc = main(_PATH_TO_LEXICONS.joinpath(lexicon))
            print(lexicon_doc)
