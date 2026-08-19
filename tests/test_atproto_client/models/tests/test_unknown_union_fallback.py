"""Fallback of open ref unions to :obj:`DotDict`.

An open union may carry a ``$type`` that the installed SDK release does not know yet. Such a member
degrades to a :obj:`DotDict` instead of failing the whole response, while a *known* member that does
not validate still raises. These tests pin both halves. Ref: https://github.com/MarshalX/atproto/issues/354
"""

import typing as t

import pytest
from atproto_client import models
from atproto_client.exceptions import ModelError
from atproto_client.models import dot_dict
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.utils import get_model_as_dict, get_model_as_json, get_or_create

_AUTHOR_DID = 'did:plc:aaaaaaaaaaaaaaaaaaaaaaaa'
_POST_CID = 'bafyreidnwt5s2u353exextusedas4nr77z5rhgzmg5j2swdadb7n65wxsy'
_POST_URI = f'at://{_AUTHOR_DID}/app.bsky.feed.post/3aaaaaaaaaaac'

_UNKNOWN_RECORD = {'$type': 'app.bsky.future.defs#brandNewView', 'uri': _POST_URI}
_KNOWN_RECORD = {'$type': 'app.bsky.embed.record#viewNotFound', 'notFound': True, 'uri': _POST_URI}


def _parse_embed(record: dict) -> t.Any:
    view = models.AppBskyEmbedRecord.View.model_validate({'$type': 'app.bsky.embed.record#view', 'record': record})
    return view.record


def test_known_union_member_resolves_to_model() -> None:
    assert isinstance(_parse_embed(_KNOWN_RECORD), models.AppBskyEmbedRecord.ViewNotFound)


@pytest.mark.parametrize(
    'record',
    [
        pytest.param(_UNKNOWN_RECORD, id='unknown_type'),
        pytest.param({'uri': _POST_URI}, id='no_type'),
        pytest.param({'$type': 'com.example.thing', 'items': [{'a': 1}, {'b': 2}]}, id='nested_list'),
    ],
)
def test_undescribable_union_member_falls_back_to_dot_dict(record: dict) -> None:
    assert isinstance(_parse_embed(record), DotDict)


def test_dot_dict_fallback_keeps_dot_and_bracket_access() -> None:
    record = _parse_embed(_UNKNOWN_RECORD)

    assert record.uri == _POST_URI
    assert record['$type'] == 'app.bsky.future.defs#brandNewView'
    assert record.nonExistingField is None


@pytest.mark.parametrize(
    'record',
    [
        pytest.param({'$type': 'app.bsky.embed.record#viewNotFound', 'uri': _POST_URI}, id='missing_required'),
        pytest.param({**_KNOWN_RECORD, 'uri': 123}, id='wrong_field_type'),
    ],
)
def test_known_union_member_still_raises(record: dict) -> None:
    with pytest.raises(ModelError):
        get_or_create(
            {'$type': 'app.bsky.embed.record#view', 'record': record}, models.AppBskyEmbedRecord.View, strict=True
        )


def test_closed_union_still_rejects_unknown_type() -> None:
    # com.atproto.repo.applyWrites is the only lexicon declaring "closed": true
    with pytest.raises(ModelError):
        get_or_create(
            {'repo': _AUTHOR_DID, 'writes': [{'$type': 'com.atproto.repo.applyWrites#nope'}]},
            models.ComAtprotoRepoApplyWrites.Data,
            strict=True,
        )


def test_list_of_unions_falls_back_per_item() -> None:
    view = models.AppBskyEmbedRecord.ViewRecord.model_validate(
        {
            '$type': 'app.bsky.embed.record#viewRecord',
            'author': {'did': _AUTHOR_DID, 'handle': 'alice.test'},
            'cid': _POST_CID,
            'indexedAt': '2026-01-01T00:00:00Z',
            'uri': _POST_URI,
            'value': {},
            'embeds': [
                {'$type': 'app.bsky.embed.images#view', 'images': []},
                {'$type': 'app.bsky.future.defs#brandNewEmbed'},
            ],
        }
    )

    assert view.embeds is not None
    assert isinstance(view.embeds[0], models.AppBskyEmbedImages.View)
    assert isinstance(view.embeds[1], DotDict)


def test_unknown_union_member_does_not_break_the_rest_of_the_response() -> None:
    """The exact shape reported in issue #354: get_author_feed with an unrecognized embed record."""
    response = models.AppBskyFeedGetAuthorFeed.Response.model_validate(
        {
            'feed': [
                {
                    'post': {
                        '$type': 'app.bsky.feed.defs#postView',
                        'author': {'did': _AUTHOR_DID, 'handle': 'alice.test'},
                        'cid': _POST_CID,
                        'indexedAt': '2026-01-01T00:00:00Z',
                        'record': {},
                        'uri': _POST_URI,
                        'embed': {'$type': 'app.bsky.embed.record#view', 'record': _UNKNOWN_RECORD},
                    }
                }
            ]
        }
    )

    post = response.feed[0].post
    assert isinstance(post.embed, models.AppBskyEmbedRecord.View)
    assert isinstance(post.embed.record, DotDict)
    assert post.uri == _POST_URI


def test_dot_dict_fallback_round_trips() -> None:
    view = models.AppBskyEmbedRecord.View.model_validate(
        {'$type': 'app.bsky.embed.record#view', 'record': _UNKNOWN_RECORD}
    )

    assert get_model_as_dict(view)['record'] == _UNKNOWN_RECORD
    assert '"app.bsky.future.defs#brandNewView"' in get_model_as_json(view)


def test_known_union_member_does_not_build_a_throwaway_dot_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    created = []
    original_init = DotDict.__init__

    def spy(self: DotDict, data: dict) -> None:
        created.append(data)
        original_init(self, data)

    monkeypatch.setattr(dot_dict.DotDict, '__init__', spy)

    assert isinstance(_parse_embed(_KNOWN_RECORD), models.AppBskyEmbedRecord.ViewNotFound)
    assert created == []
