import json
import os
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

import dacite

from atproto.exceptions import (
    LexiconParsingError,
    UnknownDefinitionTypeError,
    UnknownPrimitiveTypeError,
)
from atproto.lexicon import models

_DEBUG = os.environ.get('DEBUG', '0') == '1'

_PATH_TO_LEXICONS = Path(__file__).parent.parent.parent.joinpath('lexicons').absolute()
_LEXICON_FILE_EXT = '.json'
_LEX_DEFINITION_TYPE_TO_CLASS = {
    models.LexDefinitionType.RECORD: models.LexRecord,
    models.LexDefinitionType.PROCEDURE: models.LexXrpcProcedure,
    models.LexDefinitionType.QUERY: models.LexXrpcQuery,
    models.LexDefinitionType.SUBSCRIPTION: models.LexSubscription,
    models.LexDefinitionType.TOKEN: models.LexToken,
    models.LexDefinitionType.OBJECT: models.LexObject,
    models.LexDefinitionType.BLOB: models.LexBlob,
    models.LexDefinitionType.ARRAY: models.LexArray,
    # TODO(MarshalX): definitions could be primitives?
    models.LexDefinitionType.STRING: models.LexString,
}

_LEX_PRIMITIVE_TYPE_TO_CLASS = {
    models.LexPrimitiveType.BOOLEAN: models.LexBoolean,
    models.LexPrimitiveType.NUMBER: models.LexNumber,
    models.LexPrimitiveType.INTEGER: models.LexInteger,
    models.LexPrimitiveType.STRING: models.LexString,
    models.LexPrimitiveType.REF: models.LexRef,
    models.LexPrimitiveType.UNION: models.LexRefUnion,
    models.LexPrimitiveType.UNKNOWN: models.LexUnknown,
    models.LexPrimitiveType.CID_LINK: models.LexCidLink,
    models.LexPrimitiveType.BYTES: models.LexBytes,
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


def lexicon_parse_file(lexicon_path: Union[Path, str], *, soft_fail: bool = False) -> Optional[models.LexiconDoc]:
    try:
        with open(lexicon_path, 'r', encoding='UTF-8') as f:
            plain_lexicon = json.loads(f.read())
            return lexicon_parse(plain_lexicon)
    except Exception as e:
        if soft_fail:
            return None

        raise LexiconParsingError("Can't parse lexicon") from e


def lexicon_parse_dir(path: Union[Path, str] = None, *, soft_fail: bool = False) -> List[models.LexiconDoc]:
    if path is None:
        path = _PATH_TO_LEXICONS

    parsed_lexicons = []

    for _, _, lexicons in os.walk(path):
        for lexicon in lexicons:
            if not lexicon.endswith(_LEXICON_FILE_EXT):
                continue

            lexicon_path = path.joinpath(lexicon)
            parsed_lexicon = lexicon_parse_file(lexicon_path, soft_fail=soft_fail)
            if parsed_lexicon:
                parsed_lexicons.append(parsed_lexicon)

    return parsed_lexicons


if __name__ == '__main__':
    lex = lexicon_parse_file(_PATH_TO_LEXICONS.joinpath('app.bsky.actor.profile.json'))
    all_lex = lexicon_parse_dir(_PATH_TO_LEXICONS)
    print('Done')
