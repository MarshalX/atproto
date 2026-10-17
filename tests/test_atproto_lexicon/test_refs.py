import typing as t

from atproto_lexicon.models import LexiconDoc
from atproto_lexicon.parser import _PATH_TO_LEXICONS, lexicon_parse, lexicon_parse_dir
from atproto_lexicon.refs import find_unresolved_refs


def _doc(nsid: str, defs: t.Dict[str, t.Any]) -> LexiconDoc:
    return lexicon_parse({'lexicon': 1, 'id': nsid, 'defs': defs})


def _object(**properties: t.Any) -> t.Dict[str, t.Any]:
    return {'type': 'object', 'properties': properties}


def test_vendored_lexicons_resolve() -> None:
    assert find_unresolved_refs(lexicon_parse_dir(_PATH_TO_LEXICONS)) == {}


def test_local_refs_resolve_against_own_doc() -> None:
    doc = _doc(
        'com.example.thing',
        {
            'main': _object(view={'type': 'ref', 'ref': '#view'}, self={'type': 'ref', 'ref': 'com.example.thing'}),
            'view': _object(),
        },
    )

    assert find_unresolved_refs([doc]) == {}


def test_missing_def_in_present_doc_is_reported() -> None:
    defs = _doc('com.example.defs', {'view': _object()})
    doc = _doc('com.example.thing', {'main': _object(view={'type': 'ref', 'ref': 'com.example.defs#nope'})})

    assert find_unresolved_refs([defs, doc]) == {'com.example.defs#nope': ['com.example.thing']}


def test_missing_lexicons_are_grouped_by_nsid() -> None:
    first = _doc(
        'com.example.first',
        {
            'main': _object(
                a={'type': 'ref', 'ref': 'com.other.defs#a'},
                b={'type': 'union', 'refs': ['com.other.defs#b', 'com.another.defs']},
            )
        },
    )
    second = _doc('com.example.second', {'main': _object(a={'type': 'ref', 'ref': 'com.other.defs#a'})})

    assert find_unresolved_refs([first, second]) == {
        'com.another.defs': ['com.example.first'],
        'com.other.defs': ['com.example.first', 'com.example.second'],
    }


def test_nested_refs_are_found() -> None:
    doc = _doc(
        'com.example.thing',
        {
            'main': {
                'type': 'procedure',
                'parameters': {
                    'type': 'params',
                    'properties': {'kind': {'type': 'string', 'knownValues': ['plain', 'com.missing.params#token']}},
                },
                'input': {'encoding': 'application/json', 'schema': {'type': 'ref', 'ref': 'com.missing.input'}},
                'output': {
                    'encoding': 'application/json',
                    'schema': _object(
                        items={'type': 'array', 'items': {'type': 'union', 'refs': ['com.missing.array#item']}},
                        nested=_object(deep={'type': 'ref', 'ref': 'com.missing.nested'}),
                    ),
                },
            },
            'record': {'type': 'record', 'record': _object(ref={'type': 'ref', 'ref': 'com.missing.record'})},
            'sub': {
                'type': 'subscription',
                'message': {'schema': {'type': 'union', 'refs': ['com.missing.message#event']}},
            },
            'kinds': {'type': 'string', 'enum': ['com.missing.enum#value']},
        },
    )

    assert set(find_unresolved_refs([doc])) == {
        'com.missing.array',
        'com.missing.enum',
        'com.missing.input',
        'com.missing.message',
        'com.missing.nested',
        'com.missing.params',
        'com.missing.record',
    }
