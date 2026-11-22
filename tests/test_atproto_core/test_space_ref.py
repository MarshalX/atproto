import pytest
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import SpaceRef

from tests.interop_test_files import get_test_cases

_SPACE = 'at://did:plc:asdf123/space/com.example.group/default'
_RECORD = f'{_SPACE}/did:plc:user1/com.atproto.feed.post/abc123'
_PUBLIC = 'at://did:plc:asdf123/com.atproto.feed.post/abc'

_MAX_URI_LEN = 8192
_MAX_DID_LEN = 2048


def test_space_ref_from_str() -> None:
    space_ref = SpaceRef.from_str(_SPACE)
    space_ref2 = SpaceRef.from_str(_SPACE)

    assert space_ref == space_ref2
    assert hash(space_ref) == hash(space_ref2)

    assert str(space_ref) == _SPACE
    assert space_ref.space_did == 'did:plc:asdf123'
    assert space_ref.space_type == 'com.example.group'
    assert space_ref.skey == 'default'


@pytest.mark.parametrize('uri', [_RECORD, _PUBLIC])
def test_space_ref_from_str_accepts_only_space_ref(uri: str) -> None:
    with pytest.raises(InvalidAtUriError):
        SpaceRef.from_str(uri)


def test_space_ref_from_uri() -> None:
    assert SpaceRef.from_uri(_SPACE) == SpaceRef.from_str(_SPACE)
    assert str(SpaceRef.from_uri(_RECORD)) == _SPACE


@pytest.mark.parametrize('space_ref', get_test_cases('spaceref_syntax_valid.txt'))
def test_space_ref_from_str_roundtrip(space_ref: str) -> None:
    assert str(SpaceRef.from_str(space_ref)) == space_ref


@pytest.mark.parametrize('space_ref', get_test_cases('spaceref_syntax_invalid.txt'))
def test_space_ref_from_str_with_invalid(space_ref: str) -> None:
    with pytest.raises(InvalidAtUriError):
        SpaceRef.from_str(space_ref)


@pytest.mark.parametrize(
    'uri',
    [
        _PUBLIC,
        'at://did:plc:asdf123/space',
        'at://did:plc:asdf123/space/com.example.group',
        'at://did:plc:asdf123/space/short/default',
        'at://user.bsky.social/space/com.example.group/default',
        'at://did:plc:asdf123/space/com.example.group/..',
        f'at://did:plc:asdf123/space/com.example.group/{"o" * 513}',
        f'{_SPACE}/user.bsky.social/com.atproto.feed.post/abc123',
        f'{_SPACE}/did:plc:user1',
        f'{_SPACE}/did:plc:user1/com.atproto.feed.post',
        f'{_SPACE}/did:plc:user1/short/abc123',
        f'{_SPACE}/did:plc:user1/com.atproto.feed.post/%%%',
        f'{_RECORD}/extra',
        f'{_SPACE}/',
        f'{_RECORD}/',
        f'{_SPACE}?foo=bar',
        f'{_SPACE}?',
        f'{_SPACE}#/frag',
        f'{_SPACE}#',
        f'{_RECORD}#/frag',
        f'{_SPACE}\n',
        f' {_SPACE}',
    ],
)
def test_space_ref_from_uri_with_invalid(uri: str) -> None:
    with pytest.raises(InvalidAtUriError):
        SpaceRef.from_uri(uri)

    with pytest.raises(InvalidAtUriError):
        SpaceRef.from_str(uri)


def test_space_ref_uri_max_len() -> None:
    uri = f'{_SPACE}/{"o" * _MAX_URI_LEN}'

    with pytest.raises(InvalidAtUriError, match='Space URI is too long'):
        SpaceRef.from_uri(uri)

    with pytest.raises(InvalidAtUriError, match='Space URI is too long'):
        SpaceRef.from_str(uri)


def test_space_ref_did_max_len() -> None:
    did = 'did:plc:'
    longest_did = did + 'a' * (_MAX_DID_LEN - len(did))

    space_ref = SpaceRef.from_str(f'at://{longest_did}/space/com.example.group/default')
    assert space_ref.space_did == longest_did
    assert SpaceRef.from_uri(space_ref.record_uri(longest_did, 'com.atproto.feed.post', 'abc123')) == space_ref

    with pytest.raises(InvalidAtUriError):
        SpaceRef.from_str(f'at://{longest_did}a/space/com.example.group/default')

    with pytest.raises(InvalidAtUriError):
        SpaceRef.from_uri(f'{_SPACE}/{longest_did}a/com.atproto.feed.post/abc123')


def test_space_ref_record_uri() -> None:
    space_ref = SpaceRef.from_str(_SPACE)

    assert space_ref.record_uri('did:plc:user1', 'com.atproto.feed.post', 'abc123') == _RECORD


@pytest.mark.parametrize(
    ('repo', 'collection', 'rkey'),
    [
        ('user.bsky.social', 'com.atproto.feed.post', 'abc123'),
        ('did:plc:user1', 'short', 'abc123'),
        ('did:plc:user1', 'com.atproto.feed.post', '..'),
        ('did:plc:user1', 'com.atproto.feed.post', 'abc/123'),
        ('did:plc:user1', 'com.atproto.feed.post', 'abc123#/frag'),
        ('did:plc:user1', 'com.atproto.feed.post', ''),
        ('', '', ''),
    ],
)
def test_space_ref_record_uri_with_invalid(repo: str, collection: str, rkey: str) -> None:
    space_ref = SpaceRef.from_str(_SPACE)

    with pytest.raises(InvalidAtUriError):
        space_ref.record_uri(repo, collection, rkey)
