import pytest
from atproto_client import models
from atproto_client.exceptions import ModelError
from atproto_client.models import get_or_create

"""These tests are based on the following statements:

Lexicons are allowed to change over time, within some bounds to ensure both forwards and backwards compatibility.
The basic principle is that all old data must still be valid under the updated Lexicon,
and new data must be valid under the old Lexicon.
- Any new fields must be optional
- Non-optional fields can not be removed
- Types can not change
- Fields can not be renamed

Ref: https://atproto.com/specs/lexicon#lexicon-evolution
"""


def test_model_serialization() -> None:
    expected_signing_key = 'blabla'
    test_data = {
        'signingKey': expected_signing_key,
    }
    model = get_or_create(test_data, models.ComAtprotoServerReserveSigningKey.Response)

    assert isinstance(model, models.ComAtprotoServerReserveSigningKey.Response)
    assert isinstance(model.signing_key, str)

    assert model.signing_key == expected_signing_key
    assert model['signing_key'] == expected_signing_key


def test_added_new_fields_as_optional() -> None:
    """New fields must be optional. It means that model must be created without validation errors."""

    expected_signing_key = 'blabla'
    test_data = {
        'signingKey': expected_signing_key,
        'brandNewBackendField': 'foo',
    }
    model = get_or_create(test_data, models.ComAtprotoServerReserveSigningKey.Response)

    assert isinstance(model, models.ComAtprotoServerReserveSigningKey.Response)
    assert isinstance(model.signing_key, str)

    assert model.signing_key == expected_signing_key
    assert model['signing_key'] == expected_signing_key

    assert model.model_extra is not None

    # also, we want to have access to new fields from SDK
    # the problem here is that we can't access them via snake_case,
    # could be fixed in the future
    assert model.brandNewBackendField == 'foo'
    assert model['brandNewBackendField'] == 'foo'


def test_removed_non_optional_field() -> None:
    """If protocol removed non-optional field, it breaks backward compatibility. We must throw an error."""

    test_data = {
        # for example, signingKey was removed
        'brandNewBackendField': 'foo',
    }

    with pytest.raises(ModelError):
        get_or_create(test_data, models.ComAtprotoServerReserveSigningKey.Response)


def test_changed_field_type() -> None:
    """If protocol changed a field type, it breaks backward compatibility. We must throw an error."""

    test_data = {
        # for example, signingKey now is an integer instead of string
        'signingKey': 123,
    }

    with pytest.raises(ModelError):
        get_or_create(test_data, models.ComAtprotoServerReserveSigningKey.Response)


def test_renamed_field_type() -> None:
    """If protocol changed a field type, it breaks backward compatibility. We must throw an error."""

    expected_signing_key = 'blabla'
    test_data = {
        # for example, signingKey now signKey
        'signKey': expected_signing_key,
    }

    with pytest.raises(ModelError):
        get_or_create(test_data, models.ComAtprotoServerReserveSigningKey.Response)
