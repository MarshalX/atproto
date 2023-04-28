import json
import os
from enum import Enum
from pathlib import Path

import dacite
import models
from exceptions import UnknownDefinitionTypeError, UnknownPrimitiveTypeError

_DEBUG = os.environ.get('DEBUG', '0') == '1'

_PATH_TO_LEXICONS = Path(__file__).parent.parent.parent.joinpath('lexicons').absolute()

_LEX_DEFINITION_TYPE_TO_CLASS = {
    models.LexDefinitionType.PROCEDURE: models.LexXrpcProcedure,
    models.LexDefinitionType.QUERY: models.LexXrpcQuery,
    models.LexDefinitionType.TOKEN: models.LexToken,
    models.LexDefinitionType.OBJECT: models.LexObject,
    models.LexDefinitionType.RECORD: models.LexRecord,
    models.LexDefinitionType.SUBSCRIPTION: models.LexSubscription,
    # TODO(MarshalX): definitions could be primitives? it only happens with string in
    #  com.atproto.admin.defs.json and com.atproto.moderation.defs.json
    models.LexDefinitionType.STRING: models.LexString,
}

_LEX_PRIMITIVE_TYPE_TO_CLASS = {
    models.LexPrimitiveType.BOOLEAN: models.LexBoolean,
    models.LexPrimitiveType.NUMBER: models.LexNumber,
    models.LexPrimitiveType.INTEGER: models.LexInteger,
    models.LexPrimitiveType.STRING: models.LexString,
    models.LexPrimitiveType.REF: models.LexRef,
    models.LexPrimitiveType.UNION: models.LexRefUnion,
}


def _lex_definition_type_hook(data: dict) -> models.LexDefinition:
    try:
        definition_class = _LEX_DEFINITION_TYPE_TO_CLASS[models.LexDefinitionType(data['type'])]
    except (ValueError, KeyError):
        raise UnknownDefinitionTypeError('Unknown definition type ' + data['type'])

    return lexicon_parse(data, definition_class)


def _lex_primitive_type_hook(data: dict) -> models.LexPrimitive:
    try:
        primitive_class = _LEX_PRIMITIVE_TYPE_TO_CLASS[models.LexPrimitiveType(data['type'])]
    except (ValueError, KeyError):
        raise UnknownPrimitiveTypeError('Unknown primitive type ' + data['type'])

    return lexicon_parse(data, primitive_class)


_TYPE_HOOKS = {models.LexDefinition: _lex_definition_type_hook, models.LexPrimitive: _lex_primitive_type_hook}
_DEFAULT_DACITE_CONFIG = dacite.Config(cast=[Enum], type_hooks=_TYPE_HOOKS, check_types=_DEBUG)


def lexicon_parse(data: dict, data_class=None):
    if not data_class:
        data_class = models.LexiconDoc

    return dacite.from_dict(data_class=data_class, data=data, config=_DEFAULT_DACITE_CONFIG)


def main(lexicon_path: Path):
    with open(lexicon_path, 'r', encoding='UTF-8') as f:
        plain_lexicon = json.loads(f.read())

    return lexicon_parse(plain_lexicon)


if __name__ == '__main__':
    lexicons_to_test = None

    parsed_lexicons = []
    parsing_errors_count = 0
    for _, _, lexicons in os.walk(_PATH_TO_LEXICONS):
        for lexicon in lexicons:
            if not lexicon.endswith('.json'):
                continue

            if lexicons_to_test and lexicon not in lexicons_to_test:
                continue

            try:
                lexicon_doc = main(_PATH_TO_LEXICONS.joinpath(lexicon))
                parsed_lexicons.append(lexicon_doc)
            except Exception as e:
                parsing_errors_count += 1
                print(lexicon, str(e))

    print('Errors count:', parsing_errors_count)
    assert parsing_errors_count == 0
    breakpoint()
