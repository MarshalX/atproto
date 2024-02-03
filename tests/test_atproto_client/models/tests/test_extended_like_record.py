from atproto_client import models
from atproto_client.models import get_model_as_dict, get_or_create

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('extended_like_record')


def test_extended_like_record_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, models.AppBskyFeedLike.Record)

    assert model.value.py_type == models.ids.AppBskyFeedLike
    # record_type is the custom field out of lexicon
    assert model.value.record_type == 'app.bsky.feed.like'
    assert model.value['record_type'] == 'app.bsky.feed.like'


def test_extended_like_record_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    assert restored_model.value.py_type == models.ids.AppBskyFeedLike
    # record_type is the additional field out of lexicon
    assert restored_model.value.record_type == 'app.bsky.feed.like'
    assert restored_model.value['record_type'] == 'app.bsky.feed.like'

    assert model_dict['value']['$type'] == models.ids.AppBskyFeedLike
    assert model_dict['value']['record_type'] == 'app.bsky.feed.like'
