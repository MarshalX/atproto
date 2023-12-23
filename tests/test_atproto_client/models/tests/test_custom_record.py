from atproto_client import models
from atproto_client.models import get_model_as_dict, get_or_create
from atproto_client.models.dot_dict import DotDict

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('custom_record')


def test_custom_record_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)
    expected_custom_record_id = 'app.bsky.feed.pythonSdkCustomRecordPost'

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, DotDict)

    assert model.value['$type'] != models.ids.AppBskyFeedPost
    assert model.value['$type'] == expected_custom_record_id

    assert model.value.text == 'foo'
    assert model.value['text'] == 'foo'

    assert model.value.langs == ['en']
    assert model.value['createdAt'] == '2023-07-21T01:33:51.481951'
    assert model.value.createdAt == '2023-07-21T01:33:51.481951'
    assert model.value['created_at'] == '2023-07-21T01:33:51.481951'
    assert model.value.created_at == '2023-07-21T01:33:51.481951'


def test_custom_record_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)
    expected_custom_record_id = 'app.bsky.feed.pythonSdkCustomRecordPost'

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    assert restored_model.value['$type'] != models.ids.AppBskyFeedPost
    assert restored_model.value['$type'] == expected_custom_record_id

    assert restored_model.value.text == 'foo'
    assert restored_model.value['text'] == 'foo'

    assert model_dict['value']['$type'] == expected_custom_record_id
    assert model_dict['value']['text'] == 'foo'
