import typing as t

from atproto_client import models
from atproto_client.models import get_model_as_dict, get_or_create

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> t.Dict[str, t.Any]:
    return load_data_from_file('extended_post_record')


def test_extended_post_record_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, models.AppBskyFeedPost.Record)

    assert model.value['py_type'] == models.ids.AppBskyFeedPost
    assert model.value.py_type == models.ids.AppBskyFeedPost

    # lol is the additional field out of lexicon

    assert model.value.model_extra is not None
    assert 'lol' in model.value.model_extra

    assert model.value.lol == 'kek'  # pyrefly: ignore[missing-attribute]
    assert model.value['lol'] == 'kek'


def test_extended_post_record_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(restored_model, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)
    assert isinstance(restored_model.value, models.AppBskyFeedPost.Record)

    assert restored_model.value['py_type'] == models.ids.AppBskyFeedPost

    # lol is the additional field out of lexicon

    assert restored_model.value.model_extra is not None
    assert 'lol' in restored_model.value.model_extra

    assert restored_model.value.lol == 'kek'  # pyrefly: ignore[missing-attribute]
    assert restored_model.value['lol'] == 'kek'

    assert model_dict['value']['$type'] == models.ids.AppBskyFeedPost
    assert model_dict['value']['lol'] == 'kek'
