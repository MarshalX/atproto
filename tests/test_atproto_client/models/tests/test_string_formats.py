import pytest
from atproto_client.models import string_formats
from atproto_client.models.string_formats import _OPT_IN_KEY
from pydantic import TypeAdapter, ValidationError


@pytest.fixture
def invalid_data():
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
def valid_data():
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
    'type_name,field_name,expected_error',
    [
        ('Handle', 'handle', 'must be a domain name'),
        ('Did', 'did', 'must be in format did:method:identifier'),
        ('Nsid', 'nsid', 'must be dot-separated segments'),
        ('AtUri', 'at_uri', 'must be in format at://authority/collection/record'),
        ('Cid', 'cid', 'must be a valid Content Identifier'),
        ('DateTime', 'datetime', 'must be ISO 8601 with timezone'),
        ('Tid', 'tid', 'must be exactly 13 lowercase letters/numbers'),
        ('RecordKey', 'record_key', 'must contain only alphanumeric'),
        ('Uri', 'uri', 'must be a valid URI with scheme and authority/path'),
        ('Language', 'language', 'must be ISO language code'),
    ],
)
def test_string_format_validation(
    type_name: str, field_name: str, expected_error: str, valid_data: dict, invalid_data: dict
):
    """Test validation for each string format type."""
    validator_type = getattr(string_formats, type_name)
    SomeTypeAdapter = TypeAdapter(validator_type)

    # Test that validation is skipped by default
    assert SomeTypeAdapter.validate_python(invalid_data[field_name]) == invalid_data[field_name]

    # Test that valid data passes strict validation
    validated_value = SomeTypeAdapter.validate_python(valid_data[field_name], context={_OPT_IN_KEY: True})
    assert validated_value == valid_data[field_name]

    # Test that invalid data fails strict validation
    try:
        SomeTypeAdapter.validate_python(invalid_data[field_name], context={_OPT_IN_KEY: True})
        pytest.fail(f'{type_name} validation should have failed')
    except ValidationError as e:
        error = e.errors()[0]
        assert expected_error in error['msg']
