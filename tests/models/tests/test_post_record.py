from atproto.xrpc_client import models
from atproto.xrpc_client.models import get_model_as_dict, get_or_create
from tests.models.tests.utils import load_data_from_file

TEST_DATA = load_data_from_file('post_record')


def test_post_record_deserialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, models.AppBskyFeedPost.Main)

    expected_text = 'regress test'
    expected_langs = ['en']
    expected_created_at = '2023-07-21T01:33:51.481951'

    assert model.value.py_type == models.ids.AppBskyFeedPost
    assert model.value['py_type'] == models.ids.AppBskyFeedPost
    assert model.value.text == expected_text
    assert model.value['text'] == expected_text
    assert model['value']['text'] == expected_text
    assert model['value'].text == expected_text
    assert model.value.langs == expected_langs
    assert model.value['langs'] == expected_langs
    assert model['value']['langs'] == expected_langs
    assert model['value'].langs == expected_langs
    assert model.value.created_at == expected_created_at
    assert model.value['created_at'] == expected_created_at
    assert model['value']['created_at'] == expected_created_at
    assert model['value'].created_at == expected_created_at


def test_post_record_serialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    expected_text = 'regress test'
    expected_langs = ['en']
    expected_created_at = '2023-07-21T01:33:51.481951'

    assert restored_model.value.py_type == models.ids.AppBskyFeedPost
    assert restored_model.value['py_type'] == models.ids.AppBskyFeedPost
    assert restored_model.value.text == expected_text
    assert restored_model.value['text'] == expected_text
    assert restored_model.value.langs == expected_langs
    assert restored_model.value['langs'] == expected_langs
    assert restored_model.value.created_at == expected_created_at
    assert restored_model.value['created_at'] == expected_created_at

    assert model_dict['value']['$type'] == models.ids.AppBskyFeedPost
    assert model_dict['value']['text'] == expected_text
    assert model_dict['value']['langs'] == expected_langs
    assert model_dict['value']['createdAt'] == expected_created_at
