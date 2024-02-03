from atproto_client import models
from atproto_client.models import get_model_as_dict, get_or_create

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('like_record')


def test_like_record_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, models.AppBskyFeedLike.Record)

    expected_cid = 'bafyreiftg3snotlhlko2t7k4f6ic63slwwlrhva4mfm2ws2op2snsgyula'
    expected_uri = 'at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3k5u7c7eis72y'
    expected_created_at = '2023-08-26T12:56:31.044240'

    assert model.value.py_type == models.ids.AppBskyFeedLike
    assert model.value['py_type'] == models.ids.AppBskyFeedLike
    assert model.value.subject.cid == expected_cid
    assert model.value['subject']['cid'] == expected_cid
    assert model['value']['subject']['cid'] == expected_cid
    assert model['value'].subject.cid == expected_cid
    assert model.value.subject.uri == expected_uri
    assert model.value.subject['uri'] == expected_uri
    assert model['value']['subject']['uri'] == expected_uri
    assert model['value'].subject.uri == expected_uri
    assert model.value.created_at == expected_created_at
    assert model.value['created_at'] == expected_created_at
    assert model['value']['created_at'] == expected_created_at
    assert model['value'].created_at == expected_created_at


def test_like_record_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    expected_cid = 'bafyreiftg3snotlhlko2t7k4f6ic63slwwlrhva4mfm2ws2op2snsgyula'
    expected_uri = 'at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3k5u7c7eis72y'
    expected_created_at = '2023-08-26T12:56:31.044240'

    assert restored_model.value.py_type == models.ids.AppBskyFeedLike
    assert restored_model.value['py_type'] == models.ids.AppBskyFeedLike
    assert restored_model.value.subject.uri == expected_uri
    assert restored_model.value.subject['uri'] == expected_uri
    assert restored_model.value['subject']['uri'] == expected_uri
    assert restored_model.value.subject.cid == expected_cid
    assert restored_model.value.subject['cid'] == expected_cid
    assert restored_model.value['subject']['cid'] == expected_cid
    assert restored_model.value.created_at == expected_created_at
    assert restored_model.value['created_at'] == expected_created_at

    assert model_dict['value']['$type'] == models.ids.AppBskyFeedLike
    assert model_dict['value']['subject']['uri'] == expected_uri
    assert model_dict['value']['subject']['cid'] == expected_cid
    assert model_dict['value']['createdAt'] == expected_created_at
