import typing as t

import pytest
from atproto_client import models
from atproto_client.utils import PaginatedResponse
from atproto_codegen.models.generator import _get_page_items_field
from atproto_lexicon.parser import lexicon_parse

_ARRAY = {'type': 'array', 'items': {'type': 'string'}}
_CURSOR = {'type': 'string'}


def _query(
    params: t.Dict[str, t.Any], output: t.Dict[str, t.Any], required: t.Sequence[str] = (), main_type: str = 'query'
) -> t.Any:
    doc = lexicon_parse(
        {
            'lexicon': 1,
            'id': 'com.example.list',
            'defs': {
                'main': {
                    'type': main_type,
                    'parameters': {'type': 'params', 'properties': params},
                    'output': {
                        'encoding': 'application/json',
                        'schema': {'type': 'object', 'required': list(required), 'properties': output},
                    },
                }
            },
        }
    )
    return doc.defs['main']


def _page_items_name(definition: t.Any) -> t.Optional[str]:
    page_items_field = _get_page_items_field(definition)
    return page_items_field[1] if page_items_field else None


def test_single_array_is_page_items() -> None:
    definition = _query({'cursor': _CURSOR}, {'cursor': _CURSOR, 'items': _ARRAY, 'subject': {'type': 'string'}})

    assert _page_items_name(definition) == 'items'


def test_required_array_wins_over_side_data() -> None:
    definition = _query(
        {'cursor': _CURSOR}, {'cursor': _CURSOR, 'items': _ARRAY, 'relatedProfiles': _ARRAY}, required=['items']
    )

    assert _page_items_name(definition) == 'items'


@pytest.mark.parametrize(
    ('params', 'output', 'main_type'),
    [
        ({}, {'cursor': _CURSOR, 'items': _ARRAY}, 'query'),
        ({'cursor': _CURSOR}, {'items': _ARRAY}, 'query'),
        ({'cursor': _CURSOR}, {'cursor': _CURSOR}, 'query'),
        ({'cursor': _CURSOR}, {'cursor': _CURSOR, 'a': _ARRAY, 'b': _ARRAY}, 'query'),
        ({'cursor': _CURSOR}, {'cursor': _CURSOR, 'items': _ARRAY}, 'procedure'),
    ],
    ids=['no-cursor-param', 'no-cursor-output', 'no-array', 'ambiguous-arrays', 'procedure'],
)
def test_not_paginated(params: t.Dict[str, t.Any], output: t.Dict[str, t.Any], main_type: str) -> None:
    assert _get_page_items_field(_query(params, output, main_type=main_type)) is None


@pytest.mark.parametrize(
    ('response', 'items'),
    [
        (models.AppBskyGraphGetFollows.Response, 'follows'),
        # startCursor is for `since`, not the next page
        (models.AppBskyFeedGetTimeline.Response, 'feed'),
        (models.AppBskyFeedSearchPostsV2.Response, 'posts'),
        (models.AppBskyNotificationGetGroupedNotifications.Response, 'groups'),
        (models.ChatBskyConvoGetMessages.Response, 'messages'),
    ],
)
def test_generated_responses_are_paginated(response: t.Any, items: str) -> None:
    page = response.model_construct(**{items: ['x'], 'cursor': 'c'})

    assert isinstance(page, PaginatedResponse)
    assert page.get_page_items() == ['x']


def test_not_paginated_response() -> None:
    assert not hasattr(models.AppBskyActorGetProfile, 'Response')
    assert not hasattr(models.AppBskyFeedGetPosts.Response, 'get_page_items')
