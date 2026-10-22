import copy
import pickle

import pytest
from atproto_client import models
from atproto_client.models.base import _SharedFieldsSet

Post = models.AppBskyFeedPost.Record


def _post(text: str) -> models.AppBskyFeedPost.Record:
    return Post.model_validate({'text': text, 'createdAt': '2024-01-01T00:00:00Z'})


def test_models_of_the_same_shape_share_the_fields_set() -> None:
    first, second = _post('a'), _post('b')

    assert type(first.__pydantic_fields_set__) is _SharedFieldsSet
    assert first.__pydantic_fields_set__ is second.__pydantic_fields_set__
    assert second.model_dump(exclude_unset=True, by_alias=True) == {'text': 'b', 'createdAt': '2024-01-01T00:00:00Z'}


def test_setattr_does_not_leak_into_other_models() -> None:
    first, second = _post('a'), _post('b')

    first.langs = ['en']
    first.via = 'client'

    assert 'langs' in first.__pydantic_fields_set__
    assert 'langs' not in second.__pydantic_fields_set__
    assert 'via' not in second.__pydantic_fields_set__
    assert second.model_extra == {}


def test_model_fields_set_is_safe_to_mutate() -> None:
    first, second = _post('a'), _post('b')

    first.model_fields_set.add('langs')

    assert 'langs' not in second.__pydantic_fields_set__


def test_copies_do_not_leak_into_other_models() -> None:
    first, second = _post('a'), _post('b')

    updated = first.model_copy(update={'langs': ['en']})
    deep = copy.deepcopy(first)
    deep.langs = ['de']

    assert 'langs' in updated.model_fields_set
    assert 'langs' not in second.__pydantic_fields_set__


def test_models_pickled_together_do_not_share_a_plain_set() -> None:
    first, second = pickle.loads(pickle.dumps([_post('a'), _post('b')]))  # noqa: S301

    first.langs = ['en']

    assert 'langs' not in second.__pydantic_fields_set__
    assert 'langs' not in _post('c').__pydantic_fields_set__


def test_models_with_extra_fields_keep_their_own_set() -> None:
    first = Post.model_validate({'text': 'a', 'createdAt': '2024-01-01T00:00:00Z', 'via': 'client'})
    second = Post.model_validate({'text': 'a', 'createdAt': '2024-01-01T00:00:00Z', 'via': 'client'})

    assert type(first.__pydantic_fields_set__) is set
    assert first.__pydantic_fields_set__ is not second.__pydantic_fields_set__


def test_deprecated_fields_set_is_safe_to_mutate() -> None:
    import warnings

    first, second = _post('a'), _post('b')

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        first.__fields_set__.add('langs')

    assert 'langs' not in second.__pydantic_fields_set__


def test_lexicon_warning_is_read_at_validation_time(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('ATPROTO_LEXICON_WARN', '1')

    with pytest.warns(UserWarning, match='Extra fields found'):
        Post.model_validate({'text': 'a', 'createdAt': '2024-01-01T00:00:00Z', 'via': 'client'})
