from atproto.xrpc_client import models
from atproto.xrpc_client.models import get_model_as_dict, get_or_create
from atproto.xrpc_client.models.dot_dict import DotDict
from tests.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('custom_post_record')


def test_custom_post_record_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(model, models.ComAtprotoRepoGetRecord.Response)
    assert isinstance(model.value, DotDict)

    assert model.value['$type'] == models.ids.AppBskyFeedPost
    # lol is the custom field out of lexicon
    assert model.value.lol == 'kek'
    assert model.value['lol'] == 'kek'


def test_custom_post_record_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoRepoGetRecord.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoRepoGetRecord.Response)

    assert isinstance(get_model_as_dict(model.value), dict)
    assert model_dict == get_model_as_dict(restored_model)

    assert restored_model.value['$type'] == models.ids.AppBskyFeedPost
    # lol is the custom field out of lexicon
    assert restored_model.value.lol == 'kek'
    assert restored_model.value['lol'] == 'kek'

    assert model_dict['value']['$type'] == models.ids.AppBskyFeedPost
    assert model_dict['value']['lol'] == 'kek'
