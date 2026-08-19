import typing as t

import typing_extensions as te
from atproto_client import models
from atproto_client.models import get_or_create, is_record_type
from atproto_client.models.base import ModelBase
from atproto_client.models.dot_dict import DotDict

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_correct_data() -> dict:
    return load_data_from_file('post_record')


def load_test_custom_data() -> dict:
    return load_data_from_file('custom_record')


def load_record(loader: t.Callable[[], dict]) -> t.Union[ModelBase, DotDict]:
    response = get_or_create(loader(), models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(response, models.ComAtprotoRepoGetRecord.Response)

    return response.value


def test_is_record_type() -> None:
    lexicon_correct_post_record = load_record(load_test_correct_data)
    custom_record = load_record(load_test_custom_data)
    expected_custom_record_id = 'app.bsky.feed.pythonSdkCustomRecordPost'

    assert isinstance(lexicon_correct_post_record, models.AppBskyFeedPost.Record)
    assert is_record_type(lexicon_correct_post_record, models.ids.AppBskyFeedPost) is True
    assert is_record_type(lexicon_correct_post_record, models.ids.AppBskyFeedGenerator) is False
    assert is_record_type(lexicon_correct_post_record, models.AppBskyFeedPost) is True
    assert is_record_type(lexicon_correct_post_record, models.AppBskyFeedGenerator) is False
    assert is_record_type(lexicon_correct_post_record, models.AppBskyFeedPost.Record) is True
    assert is_record_type(lexicon_correct_post_record, models.AppBskyFeedGenerator.Record) is False

    assert isinstance(custom_record, DotDict)
    assert is_record_type(custom_record, expected_custom_record_id) is True
    assert is_record_type(custom_record, models.ids.AppBskyFeedPost) is False
    assert is_record_type(custom_record, models.AppBskyFeedPost) is False
    assert is_record_type(custom_record, models.AppBskyFeedPost.Record) is False


def test_is_record_type_with_non_record_expected_type() -> None:
    post_record = load_record(load_test_correct_data)
    non_record_types: t.List[t.Any] = [
        models.AppBskyEmbedImages,  # module without a Record
        models.AppBskyEmbedImages.Main,  # model that is not a Record
        models.ComAtprotoRepoGetRecord.Response,  # model without the "$type" field
        42,
    ]

    for expected_type in non_record_types:
        assert is_record_type(post_record, expected_type) is False


def test_is_record_type_narrows_type() -> None:
    post_record = load_record(load_test_correct_data)

    if is_record_type(post_record, models.AppBskyFeedPost):
        te.assert_type(post_record, models.AppBskyFeedPost.Record)
        assert post_record.text

    if is_record_type(post_record, models.AppBskyFeedPost.Record):
        te.assert_type(post_record, models.AppBskyFeedPost.Record)
        assert post_record.text

    te.assert_type(is_record_type(post_record, models.ids.AppBskyFeedPost), bool)
