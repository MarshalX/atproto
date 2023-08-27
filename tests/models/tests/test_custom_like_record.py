from atproto.xrpc_client import models
from atproto.xrpc_client.models import base, get_model_as_dict, get_or_create
from tests.models.tests.utils import load_data_from_file

TEST_DATA = load_data_from_file('custom_like_record')


def test_custom_like_record_deserialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, base.DotDict)

    assert model.value['$type'] == models.ids.AppBskyFeedLike
    # record_type is the custom field out of lexicon
    assert model.value.record_type == 'app.bsky.feed.like'
    assert model.value['record_type'] == 'app.bsky.feed.like'


def test_custom_like_record_serialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    assert restored_model.value['$type'] == models.ids.AppBskyFeedLike
    # record_type is the custom field out of lexicon
    assert restored_model.value.record_type == 'app.bsky.feed.like'
    assert restored_model.value['record_type'] == 'app.bsky.feed.like'

    assert model_dict['value']['$type'] == models.ids.AppBskyFeedLike
    assert model_dict['value']['record_type'] == 'app.bsky.feed.like'
