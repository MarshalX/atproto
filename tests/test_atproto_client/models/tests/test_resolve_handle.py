from atproto_client import models
from atproto_client.models import get_model_as_dict, get_or_create

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('resolve_handle')


def test_resolve_handle_deserialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoIdentityResolveHandle.Response)

    assert isinstance(model, models.ComAtprotoIdentityResolveHandle.Response)
    assert isinstance(model.did, str)

    expected_did = 'did:plc:z72i7hdynmk6r22z27h6tvur'

    assert model.did == expected_did
    assert model['did'] == expected_did


def test_resolve_handle_serialization() -> None:
    model = get_or_create(load_test_data(), models.ComAtprotoIdentityResolveHandle.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.ComAtprotoIdentityResolveHandle.Response)

    assert isinstance(get_model_as_dict(model), dict)
    assert model_dict == get_model_as_dict(restored_model)

    expected_did = 'did:plc:z72i7hdynmk6r22z27h6tvur'

    assert restored_model.did == expected_did
    assert restored_model['did'] == expected_did

    assert model_dict['did'] == expected_did
