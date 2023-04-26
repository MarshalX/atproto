import json
from enum import Enum

import dacite
import models

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
    models.LexPrimitiveType.REF: models.LexRef,     # not 100% sure cuz not documented
}


def _lex_user_type_hook(data: dict) -> models.LexDefinition:
    return lexicon_parse(data, _LEX_DEFINITION_TYPE_TO_CLASS[models.LexDefinitionType(data['type'])])


def _lex_primitive_type_hook(data: dict) -> models.LexPrimitive:
    return lexicon_parse(data, _LEX_PRIMITIVE_TYPE_TO_CLASS[models.LexPrimitiveType(data['type'])])


_TYPE_HOOKS = {models.LexDefinition: _lex_user_type_hook, models.LexPrimitive: _lex_primitive_type_hook}
_DEFAULT_DACITE_CONFIG = dacite.Config(cast=[Enum], type_hooks=_TYPE_HOOKS)


def lexicon_parse(data: dict, data_class=None):
    if not data_class:
        data_class = models.LexiconDoc

    return dacite.from_dict(data_class=data_class, data=data, config=_DEFAULT_DACITE_CONFIG)


def main(schema_name: str):
    from pathlib import Path

    path = Path(__file__).parent.parent.parent.absolute()
    schema = path.joinpath('test_data', f'{schema_name}.json')

    with open(schema, 'r', encoding='UTF-8') as f:
        schema = json.loads(f.read())

    lexicon_doc = lexicon_parse(schema)
    print(lexicon_doc)
    # breakpoint()


if __name__ == '__main__':
    main('createAccount')
    main('actor')

    # TODO(MarshalX): what is "type": "params"
    # main('getAuthorFeed')
    # main('resolveHandle')
