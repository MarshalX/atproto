from atproto_client import models
from atproto_client.models import get_model_as_dict, get_or_create

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('post_record')


def test_post_record_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, models.AppBskyFeedPost.Record)

    expected_text = 'new text114'
    expected_langs = None
    expected_created_at = '2024-02-22T19:58:13.903293+00:00'

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


def test_post_record_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    expected_text = 'new text114'
    expected_created_at = '2024-02-22T19:58:13.903293+00:00'

    assert restored_model.value.py_type == models.ids.AppBskyFeedPost
    assert restored_model.value['py_type'] == models.ids.AppBskyFeedPost
    assert restored_model.value.text == expected_text
    assert restored_model.value['text'] == expected_text
    assert restored_model.value.created_at == expected_created_at
    assert restored_model.value['created_at'] == expected_created_at

    assert model_dict['value']['$type'] == models.ids.AppBskyFeedPost
    assert model_dict['value']['text'] == expected_text
    assert model_dict['value']['createdAt'] == expected_created_at
