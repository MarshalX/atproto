import json
import shutil
import typing as t
from pathlib import Path

import pytest
from atproto_lexicon.exceptions import LexiconParsingError
from atproto_lexicon.parser import _PATH_TO_LEXICONS, lexicon_parse, lexicon_parse_dir, lexicon_parse_file
from pydantic import ValidationError


def test_lexicon_parse_file() -> None:
    lexicon_parse_file(_PATH_TO_LEXICONS.joinpath('app.bsky.actor.profile.json'))


def test_lexicon_parse_dir() -> None:
    lexicon_parse_dir(_PATH_TO_LEXICONS)


def test_lexicon_parse_dir_with_subdirectories(tmp_path: Path) -> None:
    shutil.copy(_PATH_TO_LEXICONS.joinpath('app.bsky.actor.profile.json'), tmp_path)
    nested_dir = tmp_path.joinpath('app', 'bsky', 'feed')
    nested_dir.mkdir(parents=True)
    shutil.copy(_PATH_TO_LEXICONS.joinpath('app.bsky.feed.post.json'), nested_dir)

    parsed_lexicons = lexicon_parse_dir(tmp_path)

    parsed_ids = {lexicon.id for lexicon in parsed_lexicons}
    assert parsed_ids == {'app.bsky.actor.profile', 'app.bsky.feed.post'}


def _doc(defs: t.Dict[str, t.Any], **overrides: t.Any) -> t.Dict[str, t.Any]:
    return {'lexicon': 1, 'id': 'com.example.thing', 'defs': defs, **overrides}


def _record(**overrides: t.Any) -> t.Dict[str, t.Any]:
    return {'type': 'record', 'key': 'tid', 'record': {'type': 'object', 'properties': {}}, **overrides}


def _object(properties: t.Dict[str, t.Any], **overrides: t.Any) -> t.Dict[str, t.Any]:
    return {'type': 'object', 'properties': properties, **overrides}


def _query(properties: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    return {'type': 'query', 'parameters': {'type': 'params', 'properties': properties}}


@pytest.mark.parametrize(
    'doc',
    [
        _doc({'main': _record()}, **{'$type': 'com.atproto.lexicon.schema', 'needsCbor': True}),
        _doc({'main': _object({'name': {'type': 'string', 'x-note': 'extension', 'nullable': True}})}),
        _doc({'flag': {'type': 'boolean'}, 'count': {'type': 'integer'}, 'name': {'type': 'string'}}),
        _doc({'raw': {'type': 'bytes'}, 'link': {'type': 'cid-link'}}),
        _doc({'main': _object({'inner': _object({'name': {'type': 'string'}})})}),
        _doc({'main': _object({'items': {'type': 'array', 'items': _object({})}})}),
        _doc({'main': {'type': 'object'}}),
        _doc({'main': _object({'ref': {'type': 'string', 'format': 'space-ref'}})}),
        _doc(
            {'main': {'type': 'query', 'parameters': None, 'output': {'encoding': 'application/json', 'schema': None}}}
        ),
        _doc({'main': _record(key='literal:self')}),
        _doc({'main': _query({'tags': {'type': 'array', 'items': {'type': 'string'}}})}),
    ],
    ids=[
        'unknown-document-fields',
        'unknown-property-fields',
        'primitive-defs',
        'ipld-defs',
        'inline-object-property',
        'inline-object-array-item',
        'object-without-properties',
        'unknown-string-format',
        'null-parameters-and-schema',
        'literal-record-key',
        'primitive-array-parameter',
    ],
)
def test_lexicon_parse_accepts(doc: t.Dict[str, t.Any]) -> None:
    lexicon_parse(doc)


@pytest.mark.parametrize(
    'doc',
    [
        _doc({'main': _record()}, lexicon=2),
        _doc({'main': _record()}, id='not-an-nsid'),
        _doc({'bad#name': {'type': 'token'}}),
        _doc({'other': _record()}),
        _doc({'main': {'type': 'space'}}),
        _doc({'main': {'type': 'unknown'}}),
        _doc({'main': _object({'value': {'type': 'number'}})}),
        _doc({'main': _object({'name': {'type': 'string'}}, required=['missing'])}),
        _doc({'main': _object({'name': {'type': 'string'}}, nullable=['missing'])}),
        _doc({'main': {'type': 'record', 'record': _object({})}}),
        _doc({'main': _record(key='self')}),
        _doc({'main': _record(key='literal:')}),
        _doc({'main': _query({'blob': {'type': 'unknown'}})}),
        _doc({'main': _query({'refs': {'type': 'array', 'items': {'type': 'ref', 'ref': '#x'}}})}),
        _doc({'main': {'type': 'subscription'}}),
        _doc({'main': {'type': 'subscription', 'message': {'schema': {'type': 'ref', 'ref': '#x'}}}}),
        _doc({'main': {'type': 'query', 'output': {'encoding': 'text/plain; charset=utf-8'}}}),
        _doc({'main': {'type': 'query', 'errors': [{'name': ''}]}}),
        _doc({'main': _object({'matrix': {'type': 'array', 'items': {'type': 'array', 'items': {'type': 'string'}}}})}),
    ],
    ids=[
        'lexicon-version',
        'invalid-nsid',
        'invalid-def-name',
        'record-not-main',
        'unknown-def-type',
        'unknown-as-def',
        'number-type',
        'required-not-in-properties',
        'nullable-not-in-properties',
        'record-without-key',
        'invalid-record-key',
        'empty-literal-record-key',
        'unknown-parameter',
        'ref-array-parameter',
        'subscription-without-message',
        'subscription-message-not-union',
        'encoding-with-parameters',
        'empty-error-name',
        'array-of-arrays',
    ],
)
def test_lexicon_parse_rejects(doc: t.Dict[str, t.Any]) -> None:
    with pytest.raises(ValidationError):
        lexicon_parse(doc)


def test_lexicon_parse_file_reports_location(tmp_path: Path) -> None:
    path = tmp_path.joinpath('com.example.thing.json')
    path.write_text(json.dumps(_doc({'main': {'type': 'record', 'record': _object({})}})), encoding='utf-8')

    with pytest.raises(
        LexiconParsingError, match=r'com\.example\.thing\.json.*defs\.main\.record\.key: Field required'
    ):
        lexicon_parse_file(path)
