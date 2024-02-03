from atproto_client import models
from atproto_client.models import get_or_create, is_record_type
from atproto_client.models.dot_dict import DotDict

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_correct_data() -> dict:
    return load_data_from_file('post_record')


def load_test_custom_data() -> dict:
    return load_data_from_file('custom_record')


def test_is_record_type() -> None:
    lexicon_correct_post_record = get_or_create(load_test_correct_data(), models.ComAtprotoRepoGetRecord.Response)
    custom_record = get_or_create(load_test_custom_data(), models.ComAtprotoRepoGetRecord.Response)
    expected_custom_record_id = 'app.bsky.feed.pythonSdkCustomRecordPost'

    assert isinstance(lexicon_correct_post_record.value, models.AppBskyFeedPost.Record)
    assert is_record_type(lexicon_correct_post_record.value, models.ids.AppBskyFeedPost) is True
    assert is_record_type(lexicon_correct_post_record.value, models.ids.AppBskyFeedGenerator) is False
    assert is_record_type(lexicon_correct_post_record.value, models.AppBskyFeedPost) is True
    assert is_record_type(lexicon_correct_post_record.value, models.AppBskyFeedGenerator) is False

    assert isinstance(custom_record.value, DotDict)
    assert is_record_type(custom_record.value, expected_custom_record_id) is True
    assert is_record_type(custom_record.value, models.ids.AppBskyFeedPost) is False
    assert is_record_type(custom_record.value, models.AppBskyFeedPost) is False
