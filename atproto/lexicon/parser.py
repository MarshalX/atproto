import json
import os
import typing as t
from enum import Enum
from pathlib import Path

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
    except (ValueError, KeyError) as e:
        raise UnknownDefinitionTypeError('Unknown definition type ' + data['type']) from e

    return lexicon_parse(data, definition_class)


def _lex_primitive_type_hook(data: dict) -> models.LexPrimitive:
    try:
        primitive_class = _LEX_PRIMITIVE_TYPE_TO_CLASS[models.LexPrimitiveType(data['type'])]
    except (ValueError, KeyError) as e:
        raise UnknownPrimitiveTypeError('Unknown primitive type ' + data['type']) from e

    return lexicon_parse(data, primitive_class)


_TYPE_HOOKS = {models.LexDefinition: _lex_definition_type_hook, models.LexPrimitive: _lex_primitive_type_hook}
_DEFAULT_DACITE_CONFIG = dacite.Config(cast=[Enum], type_hooks=_TYPE_HOOKS, check_types=_DEBUG)

L = t.TypeVar('L')


def lexicon_parse(data: dict, data_class: t.Optional[t.Type[L]] = models.LexiconDoc) -> L:
    return dacite.from_dict(data_class=data_class, data=data, config=_DEFAULT_DACITE_CONFIG)


def lexicon_parse_file(lexicon_path: t.Union[Path, str], *, soft_fail: bool = False) -> t.Optional[models.LexiconDoc]:
    try:
        with open(lexicon_path, 'r', encoding='UTF-8') as f:
            plain_lexicon = json.loads(f.read())
            return lexicon_parse(plain_lexicon)
    except Exception as e:  # noqa: BLE001
        if soft_fail:
            return None

        raise LexiconParsingError("Can't parse lexicon") from e


def lexicon_parse_dir(
    lexicon_dir: t.Optional[t.Union[Path, str]] = None, *, soft_fail: bool = False
) -> t.List[models.LexiconDoc]:
    lexicon_dir_path = Path(lexicon_dir) if isinstance(lexicon_dir, str) else lexicon_dir
    if lexicon_dir_path is None:
        lexicon_dir_path = _PATH_TO_LEXICONS

    parsed_lexicons = []

    for _, _, lexicons in sorted(os.walk(lexicon_dir_path)):
        for lexicon in sorted(lexicons):
            if not lexicon.endswith(_LEXICON_FILE_EXT):
                continue

            lexicon_path = lexicon_dir_path.joinpath(lexicon)
            parsed_lexicon = lexicon_parse_file(lexicon_path, soft_fail=soft_fail)
            if parsed_lexicon:
                parsed_lexicons.append(parsed_lexicon)

    return parsed_lexicons
