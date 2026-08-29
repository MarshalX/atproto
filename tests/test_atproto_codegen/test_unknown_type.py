import typing as t

import pytest
from atproto_client import models
from atproto_client.models.dot_dict import DotDict

SDK_POST = {'$type': 'app.bsky.feed.post', 'text': 'hi', 'createdAt': '2026-01-01T00:00:00.000Z'}
CUSTOM_STATUS = {'$type': 'xyz.statusphere.status', 'status': '🚀', 'createdAt': '2026-01-01T00:00:00.000Z'}


def _with_unknown(value: t.Any) -> t.Any:
    """A model whose `debug` field is a lexicon `unknown`."""
    return models.AppBskyActorDefs.ProfileViewBasic(did='did:plc:test', handle='a.bsky.social', debug=value)


def test_sdk_record_is_typed() -> None:
    assert type(_with_unknown(SDK_POST).debug) is models.AppBskyFeedPost.Record


def test_sdk_record_round_trips() -> None:
    dumped = _with_unknown(SDK_POST).model_dump(by_alias=True, exclude_none=True)

    assert dumped['debug'] == SDK_POST


def test_unregistered_type_falls_back_to_dot_dict() -> None:
    model = _with_unknown({'$type': 'zz.nobody.owns.this', 'a': 1})

    assert isinstance(model.debug, DotDict)
    assert model.model_dump(by_alias=True, exclude_none=True)['debug'] == {'$type': 'zz.nobody.owns.this', 'a': 1}


def test_value_without_a_type_falls_back_to_dot_dict() -> None:
    assert isinstance(_with_unknown({'no': 'type'}).debug, DotDict)


def test_already_built_model_passes_through() -> None:
    record = models.AppBskyFeedPost.Record(text='hi', created_at='2026-01-01T00:00:00.000Z')

    assert _with_unknown(record).debug is record


@pytest.mark.usefixtures('custom_package')
def test_custom_record_is_typed_inside_an_sdk_model() -> None:
    """The point of the open type: a record the SDK has never heard of, decoded by its own model."""
    from atproto_client.models.record_registry import resolve_record_type

    debug = _with_unknown(CUSTOM_STATUS).debug

    assert not isinstance(debug, DotDict)
    assert type(debug) is resolve_record_type('xyz.statusphere.status')
    assert debug.status == '🚀'


@pytest.mark.usefixtures('custom_package')
def test_custom_record_round_trips() -> None:
    dumped = _with_unknown(CUSTOM_STATUS).model_dump(by_alias=True, exclude_none=True)

    assert dumped['debug'] == CUSTOM_STATUS
