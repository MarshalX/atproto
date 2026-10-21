from dataclasses import dataclass

import pytest
from atproto_client import models
from atproto_client.exceptions import ModelError
from atproto_client.models.utils import get_or_create, is_json, load_json


def test_load_json() -> None:
    assert load_json('{"key": "value"}')
    assert load_json(b'{"key": "value"}')

    assert load_json('{"key": "value"', strict=False) is None
    with pytest.raises(ValueError):
        load_json(b'{"key": "value"')

    assert load_json('{"key": "value"', strict=False) is None
    with pytest.raises(ValueError):
        load_json(b'{"key": "value"')

    assert load_json('{"key": "value"}'.encode('UTF-16'), strict=False) is None

    with pytest.raises(TypeError):
        load_json(None)  # pyrefly: ignore[bad-argument-type]


def test_is_json() -> None:
    assert is_json('{"key": "value"}') is True
    assert is_json(b'{"key": "value"}') is True

    assert is_json('{"key": "value"') is False
    assert is_json(b'{"key": "value"') is False

    assert is_json('{"key": "value"}'.encode('UTF-16')) is False

    assert is_json(b'') is False
    assert is_json(b'{}') is True

    with pytest.raises(TypeError):
        load_json(None)  # pyrefly: ignore[bad-argument-type]


def test_get_or_create_works_with_dataclasses() -> None:
    """Test that get_or_create works with dataclasses."""

    @dataclass
    class Foo:
        bar: str

    with pytest.raises(ModelError, match='Cannot parse model of type'):
        get_or_create(('bar', 'not a mapping'), Foo)  # pyrefly: ignore[no-matching-overload]

    result = get_or_create({'bar': 'baz'}, Foo)
    assert result == Foo(bar='baz')


def test_get_or_create_resolves_record_from_type() -> None:
    data = {'$type': 'app.bsky.feed.post', 'text': 'Hello', 'createdAt': '2024-01-01T00:00:00Z'}

    post = get_or_create(data)
    assert isinstance(post, models.AppBskyFeedPost.Record)
    assert post.text == 'Hello'

    assert get_or_create({'$type': 'com.example.unknown'}) is None

    with pytest.raises(ModelError):
        get_or_create({'$type': 'app.bsky.feed.post'})
