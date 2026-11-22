import pytest
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import AtUri

from tests.interop_test_files import get_test_cases

_SPACE = 'at://did:plc:asdf123/space/com.example.group/default'
_SPACE_RECORD = f'{_SPACE}/did:plc:user1/com.atproto.feed.post/abc123'


def test_at_uri_from_str() -> None:
    test_uri = 'at://did:plc:poqvcn9iqfkgukdvqvb2qzba/app.bsky.feed.post/1jlmwihiomm9m'

    at_uri = AtUri.from_str(test_uri)
    at_uri2 = AtUri.from_str(test_uri)

    assert at_uri == at_uri2

    assert test_uri == str(at_uri)
    assert at_uri.rkey == '1jlmwihiomm9m'
    assert at_uri.collection == 'app.bsky.feed.post'


def test_at_uri_from_relative_str() -> None:
    base = 'did:web:localhost:1234'
    uri = '/foo?foo=bar'

    at_uri = AtUri.from_relative_str(base, uri)
    assert at_uri.origin == 'at://did:web:localhost:1234'
    assert at_uri.pathname == '/foo'
    assert at_uri.search == 'foo=bar'
    assert str(at_uri) == 'at://did:web:localhost:1234/foo?foo=bar'


def test_at_uri_make() -> None:
    did = 'did:plc:poqvcn9iqfkgukdvqvb2qzba'
    collection = 'app.bsky.feed.post'
    rkey = '1jlmwihiomm9m'

    at_uri = AtUri.make(did, collection, rkey)
    assert at_uri.host == did
    assert at_uri.collection == collection
    assert at_uri.rkey == rkey


def test_at_uri_hostname_with_digits() -> None:
    test_uri = 'at://100ideas.bsky.social'
    expected_hostname = '100ideas.bsky.social'

    at_uri = AtUri.from_str(test_uri)
    assert at_uri.hostname == expected_hostname


def test_at_uri_constructor() -> None:
    host = '100ideas.bsky.social'
    expected__uri = 'at://100ideas.bsky.social/'
    expected_hostname = '100ideas.bsky.social'

    at_uri = AtUri(host)
    assert str(at_uri) == expected__uri
    assert at_uri.hostname == expected_hostname
    assert at_uri.collection == ''
    assert at_uri.rkey == ''

    at_uri2 = AtUri(host, 'app.bsky.feed.post')
    assert at_uri.hostname == expected_hostname
    assert at_uri2.collection == 'app.bsky.feed.post'

    at_uri3 = AtUri(host, '/app.bsky.feed.post', 'title')
    assert at_uri.hostname == expected_hostname
    assert at_uri3.collection == 'app.bsky.feed.post'
    assert at_uri3.hash == 'title'

    with pytest.raises(InvalidAtUriError):
        AtUri(host, hash_='title')

    with pytest.raises(InvalidAtUriError):
        AtUri(host, search_params=[('key', 'value')])

    with pytest.raises(InvalidAtUriError):
        AtUri(host, hash_='title', search_params=[('key', 'value')])

    at_uri4 = AtUri(host, pathname='app.bsky.feed.post', hash_='title', search_params=[('key', 'value')])
    assert at_uri4.search_params == [('key', 'value')]


@pytest.mark.parametrize('valid_at_uri', get_test_cases('aturi_syntax_valid.txt'))
def test_at_uri_from_str_roundtrip(valid_at_uri: str) -> None:
    """Test str -> AtUri.from_str -> str roundtrip with valid data."""
    round_tripped_at_uri = str(AtUri.from_str(valid_at_uri))
    assert round_tripped_at_uri.startswith(valid_at_uri)  # trailing slash is okay


def test_at_uri_href() -> None:
    test_uri = 'at://did:plc:poqvcn9iqfkgukdvqvb2qzba/app.bsky.feed.post/1jlmwihiomm9m'

    at_uri = AtUri.from_str(test_uri)
    assert at_uri.href == test_uri
    assert at_uri.href == str(at_uri)


def test_at_uri_http_is_deprecated() -> None:
    at_uri = AtUri.from_str('at://did:plc:poqvcn9iqfkgukdvqvb2qzba/app.bsky.feed.post/1jlmwihiomm9m')

    with pytest.deprecated_call():
        assert at_uri.http == at_uri.href


def test_at_uri_space() -> None:
    at_uri = AtUri.from_str(_SPACE)

    assert str(at_uri) == _SPACE
    assert at_uri.is_space
    assert at_uri.space_did == 'did:plc:asdf123'
    assert at_uri.space_type == 'com.example.group'
    assert at_uri.skey == 'default'
    assert at_uri.author_did == ''
    assert at_uri.collection == ''
    assert at_uri.rkey == ''


def test_at_uri_space_record() -> None:
    at_uri = AtUri.from_str(_SPACE_RECORD)

    assert str(at_uri) == _SPACE_RECORD
    assert at_uri.is_space
    assert at_uri.space_did == 'did:plc:asdf123'
    assert at_uri.space_type == 'com.example.group'
    assert at_uri.skey == 'default'
    assert at_uri.author_did == 'did:plc:user1'
    assert at_uri.collection == 'com.atproto.feed.post'
    assert at_uri.rkey == 'abc123'


def test_at_uri_without_space() -> None:
    at_uri = AtUri.from_str('at://did:plc:asdf123/com.atproto.feed.post/abc')

    assert not at_uri.is_space
    assert at_uri.space_did == ''
    assert at_uri.space_type == ''
    assert at_uri.skey == ''
    assert at_uri.author_did == 'did:plc:asdf123'
    assert at_uri.collection == 'com.atproto.feed.post'
    assert at_uri.rkey == 'abc'

    assert not AtUri.from_str('at://did:plc:asdf123').is_space
    assert not AtUri.from_str('at://did:plc:asdf123/space.example.group/space').is_space


def test_at_uri_author_did_with_handle() -> None:
    assert AtUri.from_str('at://user.bsky.social/com.atproto.feed.post/abc').author_did == ''
    assert AtUri.from_str('at://user.bsky.social').author_did == ''


def test_at_uri_space_with_invalid_parts() -> None:
    assert AtUri.from_str('at://user.bsky.social/space/com.example.group/default').space_did == ''
    assert AtUri.from_str('at://did:plc:asdf123/space/short/default').space_type == ''
    assert AtUri.from_str('at://did:plc:asdf123/space/com.example.group/..').skey == ''

    at_uri = AtUri.from_str(f'{_SPACE}/user.bsky.social/short/..')
    assert at_uri.is_space
    assert at_uri.author_did == ''
    assert at_uri.collection == ''
    assert at_uri.rkey == ''
