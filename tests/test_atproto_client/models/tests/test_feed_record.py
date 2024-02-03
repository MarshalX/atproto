import pytest
from atproto_client import models
from atproto_client.models import dot_dict, get_model_as_dict, get_or_create
from atproto_client.models.blob_ref import BlobRef
from pydantic import ValidationError

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('feed_record')


def test_feed_record_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, models.AppBskyFeedGenerator.Record)

    assert model.value.did == 'did:web:feed.atproto.blue'
    assert model.value['did'] == 'did:web:feed.atproto.blue'
    assert model.value.created_at == '2023-07-20T10:17:40.298101'
    assert model.value['created_at'] == '2023-07-20T10:17:40.298101'


def test_feed_record_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    assert restored_model.value.py_type == models.ids.AppBskyFeedGenerator
    assert restored_model.value['py_type'] == models.ids.AppBskyFeedGenerator
    assert restored_model.value.did == 'did:web:feed.atproto.blue'
    assert restored_model.value['did'] == 'did:web:feed.atproto.blue'
    assert restored_model.value.created_at == '2023-07-20T10:17:40.298101'
    assert restored_model.value['created_at'] == '2023-07-20T10:17:40.298101'

    assert model_dict['value']['did'] == 'did:web:feed.atproto.blue'
    assert model_dict['value']['createdAt'] == '2023-07-20T10:17:40.298101'
    assert model_dict['value']['$type'] == models.ids.AppBskyFeedGenerator


def test_feed_record_avatar_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value.avatar, BlobRef)

    assert model.value.avatar.mime_type == 'image/png'
    assert model.value.avatar.py_type == 'blob'


def test_feed_record_avatar_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    avatar = model.value.avatar
    avatar_dict = get_model_as_dict(avatar)
    restored_avatar = get_or_create(avatar_dict, BlobRef)

    assert avatar_dict == get_model_as_dict(restored_avatar)

    assert isinstance(restored_avatar, BlobRef)
    assert restored_avatar == avatar
    assert restored_avatar.mime_type == avatar.mime_type
    assert restored_avatar.ref.link == avatar.ref.link
    assert restored_avatar.cid == avatar.cid


def test_feed_record_py_type_frozen() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    with pytest.raises(ValidationError):
        model.value.py_type = 'app.bsky.feed.generator'


def test_feed_record_model_strict_mode() -> None:
    test_data = load_test_data()

    non_str_did = 123
    test_data['value']['did'] = non_str_did

    model = get_or_create(test_data, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)

    # we expect here to fall back into DotDict because strict validation is failed
    assert not isinstance(model.value, models.AppBskyFeedGenerator.Record)
    assert isinstance(model.value, dot_dict.DotDict)

    assert model.value.did == non_str_did
