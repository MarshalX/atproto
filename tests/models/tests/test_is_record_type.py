from atproto.xrpc_client import models
from atproto.xrpc_client.models import get_or_create, is_record_type
from atproto.xrpc_client.models.dot_dict import DotDict
from tests.models.tests.utils import load_data_from_file


def load_test_correct_data() -> dict:
    return load_data_from_file('post_record')


def load_test_extended_data() -> dict:
    return load_data_from_file('custom_post_record')


def test_is_record_type() -> None:
    lexicon_correct_post_record = get_or_create(load_test_correct_data(), models.ComAtprotoRepoGetRecord.Response)
    extended_post_record = get_or_create(load_test_extended_data(), models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(lexicon_correct_post_record.value, models.AppBskyFeedPost.Main)
    assert is_record_type(lexicon_correct_post_record.value, models.ids.AppBskyFeedPost) is True
    assert is_record_type(lexicon_correct_post_record.value, models.ids.AppBskyFeedGenerator) is False
    assert is_record_type(lexicon_correct_post_record.value, models.AppBskyFeedPost) is True
    assert is_record_type(lexicon_correct_post_record.value, models.AppBskyFeedGenerator) is False

    assert isinstance(extended_post_record.value, DotDict)
    assert is_record_type(extended_post_record.value, models.ids.AppBskyFeedPost) is True
    assert is_record_type(extended_post_record.value, models.ids.AppBskyFeedGenerator) is False
    assert is_record_type(extended_post_record.value, models.AppBskyFeedPost) is True
    assert is_record_type(extended_post_record.value, models.AppBskyFeedGenerator) is False
