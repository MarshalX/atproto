import pytest
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import AtUri

from tests.interop_test_files import get_test_cases


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
