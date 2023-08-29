from atproto.xrpc_client import models
from atproto.xrpc_client.models import get_or_create, is_record_type
from atproto.xrpc_client.models.dot_dict import DotDict
from tests.models.tests.utils import load_data_from_file

TEST_DATA_LEXICON_CORRECT = load_data_from_file('post_record')
TEST_DATA_EXTENDED_LEXICON = load_data_from_file('custom_post_record')


def test_is_record_type():
    lexicon_correct_post_record = get_or_create(TEST_DATA_LEXICON_CORRECT, models.ComAtprotoRepoGetRecord.Response)
    extended_post_record = get_or_create(TEST_DATA_EXTENDED_LEXICON, models.ComAtprotoRepoGetRecord.Response)

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
