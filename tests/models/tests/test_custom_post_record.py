from atproto.xrpc_client import models
from atproto.xrpc_client.models import get_model_as_dict, get_or_create
from tests.models.tests.utils import load_data_from_file

TEST_DATA = load_data_from_file('custom_post_record')


def test_custom_post_record_deserialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, models.AppBskyFeedPost.Main)

    assert model.value.py_type == models.ids.AppBskyFeedPost
    # lol is the custom field, this should be ignored
    assert 'createdAt' in get_model_as_dict(model)['value']
    assert 'lol' not in get_model_as_dict(model)['value']


def test_custom_post_record_serialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    assert restored_model.value.py_type == models.ids.AppBskyFeedPost

    # lol is the custom field, this should be ignored
    assert 'createdAt' in get_model_as_dict(model)['value']
    assert 'lol' not in get_model_as_dict(model)['value']
