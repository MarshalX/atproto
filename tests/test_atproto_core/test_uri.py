from atproto_core.uri import AtUri


def test_at_uri_from_str() -> None:
    test_uri = 'at://did:plc:poqvcn9iqfkgukdvqvb2qzba/app.bsky.feed.post/1jlmwihiomm9m'

    at_uri = AtUri.from_str(test_uri)
    at_uri2 = AtUri.from_str(test_uri)

    assert at_uri == at_uri2

    assert test_uri == str(at_uri)
    assert at_uri.rkey == '1jlmwihiomm9m'
    assert at_uri.collection == 'app.bsky.feed.post'
