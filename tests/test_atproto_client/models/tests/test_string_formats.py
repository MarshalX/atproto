import pytest
from atproto_client.exceptions import ModelError
from atproto_client.models import string_formats
from atproto_client.models.string_formats import _OPT_IN_KEY
from atproto_client.models.utils import get_or_create
from pydantic import BaseModel, TypeAdapter, ValidationError


@pytest.fixture
def invalid_data() -> dict:
    return {
        'handle': 'invalid@ @handle',
        'did': 'not-a-did',
        'nsid': 'invalid-nsid',
        'at_uri': 'not-an-at-uri',
        'cid': 'short',
        'datetime': '2023-01-01',
        'tid': 'invalid-tid',
        'record_key': '..',
        'uri': 'invalid-uri-no-scheme',
        'language': 'invalid!',
    }


@pytest.fixture
def valid_data() -> dict:
    return {
        'handle': 'test.bsky.social',
        'did': 'did:plc:1234abcd',
        'nsid': 'app.bsky.feed.post',
        'at_uri': 'at://user.bsky.social/posts/123',
        'cid': 'bafyreidfayvfuwqa2beehqn7axeeeaej5aqvaowxgwcdt2rw',
        'datetime': '2023-01-01T12:00:00Z',
        'tid': '3jqvenncqkgbm',
        'record_key': 'valid-key',
        'uri': 'https://example.com',
        'language': 'en-US',
    }


@pytest.mark.parametrize(
    'validator_type,field_name,expected_error',
    [
        (string_formats.Handle, 'handle', 'must be a domain name'),
        (string_formats.Did, 'did', 'must be in format did:method:identifier'),
        (string_formats.Nsid, 'nsid', 'must be dot-separated segments'),
        (string_formats.AtUri, 'at_uri', 'must be in format at://authority/collection/record'),
        (string_formats.Cid, 'cid', 'must be a valid Content Identifier'),
        (string_formats.DateTime, 'datetime', 'must be ISO 8601 with timezone'),
        (string_formats.Tid, 'tid', 'must be exactly 13 lowercase letters/numbers'),
        (string_formats.RecordKey, 'record_key', 'must contain only alphanumeric'),
        (string_formats.Uri, 'uri', 'must be a valid URI with scheme and authority/path'),
        (string_formats.Language, 'language', 'must be ISO language code'),
    ],
)
def test_string_format_validation(
    validator_type: type, field_name: str, expected_error: str, valid_data: dict, invalid_data: dict
) -> None:
    """Test validation for each string format type."""
    SomeTypeAdapter = TypeAdapter(validator_type)

    # Test that validation is skipped by default
    assert SomeTypeAdapter.validate_python(invalid_data[field_name]) == invalid_data[field_name]

    # Test that valid data passes strict validation
    validated_value = SomeTypeAdapter.validate_python(valid_data[field_name], context={_OPT_IN_KEY: True})
    assert validated_value == valid_data[field_name]

    # Test that invalid data fails strict validation
    try:
        SomeTypeAdapter.validate_python(invalid_data[field_name], context={_OPT_IN_KEY: True})
        pytest.fail(f'{validator_type.__name__} validation should have failed')
    except ValidationError as e:
        error = e.errors()[0]
        assert expected_error in error['msg']


def test_get_or_create_with_strict_validation(valid_data: dict, invalid_data: dict) -> None:
    """Test that get_or_create uses strict validation."""

    class TestModel(BaseModel):
        handle: string_formats.Handle
        did: string_formats.Did

    # Test valid data passes
    instance = get_or_create(
        {'handle': valid_data['handle'], 'did': valid_data['did']}, TestModel, strict_string_format=True
    )
    assert isinstance(instance, TestModel)
    assert instance.handle == valid_data['handle']
    assert instance.did == valid_data['did']

    # Test invalid handle fails
    try:
        get_or_create(
            {'handle': invalid_data['handle'], 'did': valid_data['did']}, TestModel, strict_string_format=True
        )
        pytest.fail('Handle validation should have failed')
    except ModelError as e:
        assert 'must be a domain name' in str(e)

    # Test invalid did fails
    try:
        get_or_create(
            {'handle': valid_data['handle'], 'did': invalid_data['did']}, TestModel, strict_string_format=True
        )
        pytest.fail('Did validation should have failed')
    except ModelError as e:
        assert 'must be in format did:method:identifier' in str(e)

    # Test that validation is skipped when strict_string_format=False
    instance = get_or_create(
        {'handle': invalid_data['handle'], 'did': invalid_data['did']}, TestModel, strict_string_format=False
    )
    assert isinstance(instance, TestModel)
    assert instance.handle == invalid_data['handle']
    assert instance.did == invalid_data['did']
