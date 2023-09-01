import pytest
from pydantic import ValidationError

from atproto.xrpc_client import models
from atproto.xrpc_client.models import get_model_as_dict, get_or_create
from atproto.xrpc_client.models.blob_ref import BlobRef
from tests.models.tests.utils import load_data_from_file

TEST_DATA = load_data_from_file('feed_record')


def test_feed_record_deserialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, models.AppBskyFeedGenerator.Main)

    assert model.value.did == 'did:web:feed.atproto.blue'
    assert model.value['did'] == 'did:web:feed.atproto.blue'
    assert model.value.createdAt == '2023-07-20T10:17:40.298101'
    assert model.value['createdAt'] == '2023-07-20T10:17:40.298101'


def test_feed_record_py_type_frozen():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    with pytest.raises(ValidationError):
        model.value.py_type = 'app.bsky.feed.generator'


def test_feed_record_serialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    assert restored_model.value.py_type == models.ids.AppBskyFeedGenerator
    assert restored_model.value['py_type'] == models.ids.AppBskyFeedGenerator
    assert restored_model.value.did == 'did:web:feed.atproto.blue'
    assert restored_model.value['did'] == 'did:web:feed.atproto.blue'
    assert restored_model.value.createdAt == '2023-07-20T10:17:40.298101'
    assert restored_model.value['createdAt'] == '2023-07-20T10:17:40.298101'

    assert model_dict['value']['did'] == 'did:web:feed.atproto.blue'
    assert model_dict['value']['createdAt'] == '2023-07-20T10:17:40.298101'
    assert model_dict['value']['$type'] == models.ids.AppBskyFeedGenerator


def test_feed_record_avatar_deserialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value.avatar, BlobRef)

    assert model.value.avatar.mime_type == 'image/png'
    assert model.value.avatar.py_type == 'blob'


def test_feed_record_avatar_serialization():
    model = get_or_create(TEST_DATA, models.ComAtprotoRepoGetRecord.Response)

    avatar = model.value.avatar
    avatar_dict = get_model_as_dict(avatar)
    restored_avatar = get_or_create(avatar_dict, BlobRef)

    assert avatar_dict == get_model_as_dict(restored_avatar)

    assert isinstance(restored_avatar, BlobRef)
    assert restored_avatar == avatar
    assert restored_avatar.mime_type == avatar.mime_type
    assert restored_avatar.ref.link == avatar.ref.link
    assert restored_avatar.cid == avatar.cid
