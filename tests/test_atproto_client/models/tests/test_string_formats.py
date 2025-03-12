from functools import lru_cache
from pathlib import Path
from typing import List

import pytest
from atproto_client.exceptions import ModelError
from atproto_client.models import string_formats
from atproto_client.models.string_formats import _OPT_IN_KEY
from atproto_client.models.utils import get_or_create
from pydantic import BaseModel, TypeAdapter, ValidationError

# Test data sourced directly from bluesky-social/atproto repo:
# https://github.com/bluesky-social/atproto/tree/main/interop-test-files/syntax
INTEROP_TEST_FILES_DIR: Path = Path('tests/test_atproto_client/interop-test-files/syntax')


def get_test_cases(filename: str) -> List[str]:
    """Get non-comment, non-empty lines from an interop test file.

    Important: Preserves whitespace in test cases. This is critical for
    format validators where leading/trailing/internal whitespace makes a
    value invalid. For example, ' 1985-04-12T23:20:50.123Z' (with leading space)
    should be invalid for datetime validation.

    Args:
        filename: Name of the test file to read from interop test files directory

    Returns:
        List of test cases with original whitespace preserved
    """
    return [
        line
        for line in INTEROP_TEST_FILES_DIR.joinpath(filename).read_text().splitlines()
        if line and not line.startswith('#')
    ]


@lru_cache
def read_test_data() -> dict:
    """Load all test data once at session start"""
    return {
        'valid': {
            'handle': get_test_cases('handle_syntax_valid.txt'),
            'did': get_test_cases('did_syntax_valid.txt'),
            'nsid': get_test_cases('nsid_syntax_valid.txt'),
            'at_uri': get_test_cases('aturi_syntax_valid.txt'),
            'datetime': get_test_cases('datetime_syntax_valid.txt'),
            'tid': get_test_cases('tid_syntax_valid.txt'),
            'record_key': get_test_cases('recordkey_syntax_valid.txt'),
        },
        'invalid': {
            'handle': get_test_cases('handle_syntax_invalid.txt'),
            'did': get_test_cases('did_syntax_invalid.txt'),
            'nsid': get_test_cases('nsid_syntax_invalid.txt'),
            'at_uri': get_test_cases('aturi_syntax_invalid.txt'),
            'datetime': get_test_cases('datetime_syntax_invalid.txt'),
            'tid': get_test_cases('tid_syntax_invalid.txt'),
            'record_key': get_test_cases('recordkey_syntax_invalid.txt'),
        },
    }


@pytest.fixture
def valid_data() -> dict:
    """Get first valid example of each type plus constants"""
    test_data = read_test_data()
    return {
        'handle': test_data['valid']['handle'][0],
        'did': test_data['valid']['did'][0],
        'nsid': test_data['valid']['nsid'][0],
        'at_uri': test_data['valid']['at_uri'][0],
        'cid': 'bafyreidfayvfuwqa2beehqn7axeeeaej5aqvaowxgwcdt2rw',  # No interop test file for CID
        'datetime': test_data['valid']['datetime'][0],
        'tid': test_data['valid']['tid'][0],
        'record_key': test_data['valid']['record_key'][0],
        'uri': 'https://example.com',  # No interop test file for URI
        'language': 'en-US',  # No interop test file for language
    }


@pytest.fixture
def invalid_data() -> dict:
    """Get first invalid example of each type plus constants"""
    test_data = read_test_data()
    return {
        'handle': test_data['invalid']['handle'][0],
        'did': test_data['invalid']['did'][0],
        'nsid': test_data['invalid']['nsid'][0],
        'at_uri': test_data['invalid']['at_uri'][0],
        'cid': 'short',  # No interop test file for CID
        'datetime': test_data['invalid']['datetime'][0],
        'tid': test_data['invalid']['tid'][0],
        'record_key': test_data['invalid']['record_key'][0],
        'uri': 'invalid-uri-no-scheme',  # No interop test file for URI
        'language': 'invalid!',  # No interop test file for language
    }


@pytest.mark.parametrize(
    'validator_type,field_name,invalid_value',
    [
        (validator_type, field_name, invalid_value)
        for validator_type, field_name in [
            (string_formats.AtUri, 'at_uri'),
            (string_formats.DateTime, 'datetime'),
            (string_formats.Handle, 'handle'),
            (string_formats.Did, 'did'),
            (string_formats.Nsid, 'nsid'),
            (string_formats.Tid, 'tid'),
            (string_formats.RecordKey, 'record_key'),
        ]
        for invalid_value in read_test_data()['invalid'][field_name]
    ],
)
def test_string_format_validation(validator_type: type, field_name: str, invalid_value: str, valid_data: dict) -> None:
    """Test validation for each string format type."""
    SomeTypeAdapter = TypeAdapter(validator_type)

    # Test that validation is skipped by default
    assert SomeTypeAdapter.validate_python(invalid_value) == invalid_value

    # Test that valid data passes strict validation
    validated_value = SomeTypeAdapter.validate_python(valid_data[field_name], context={_OPT_IN_KEY: True})
    assert validated_value == valid_data[field_name]

    # Test that invalid data fails strict validation
    with pytest.raises(ValidationError):
        SomeTypeAdapter.validate_python(invalid_value, context={_OPT_IN_KEY: True})


def test_nsid_with_digits_in_final_segment() -> None:
    """Test that NSIDs with digits in the final segment are now valid."""
    test_cases = [
        'com.example.postV2',
        'app.bsky.feed.post123',
        'com.example.v2',
        'net.users.bob.post99',
    ]

    nsid_adapter = TypeAdapter(string_formats.Nsid)
    for nsid in test_cases:
        # Should pass with strict validation
        validated = nsid_adapter.validate_python(nsid, context={_OPT_IN_KEY: True})
        assert validated == nsid

    # These should still be invalid (digits in non-final segments)
    invalid_cases = [
        'com.example123.post',
        'app.bsky2.feed.post',
    ]
    for invalid_nsid in invalid_cases:
        with pytest.raises(ValidationError):
            nsid_adapter.validate_python(invalid_nsid, context={_OPT_IN_KEY: True})


@pytest.mark.parametrize(
    'valid_value',
    [
        'test.bsky.social',
        'did:plc:1234abcd',
        'app.bsky.feed.post',
        'at://user.bsky.social/posts/123',
        'bafyreidfayvfuwqa2beehqn7axeeeaej5aqvaowxgwcdt2rw',
        '2023-01-01T12:00:00Z',
        '3jqvenncqkgbm',
        'valid-key',
        'https://example.com',
        'en-US',
    ],
)
def test_generic_string_format_validation(valid_value: str) -> None:
    """Test that ATProtoString accepts each valid string format."""

    validated = TypeAdapter(string_formats.AtProtoString).validate_python(valid_value, context={_OPT_IN_KEY: True})
    assert validated == valid_value


def test_get_or_create_with_strict_validation(valid_data: dict, invalid_data: dict) -> None:
    """Test that get_or_create uses strict validation."""

    class FooModel(BaseModel):
        handle: string_formats.Handle
        did: string_formats.Did

    # Test valid data passes
    instance = get_or_create(
        {'handle': valid_data['handle'], 'did': valid_data['did']}, FooModel, strict_string_format=True
    )
    assert isinstance(instance, FooModel)
    assert instance.handle == valid_data['handle']
    assert instance.did == valid_data['did']

    # Test invalid handle fails
    with pytest.raises(ModelError) as exc_info:
        get_or_create({'handle': invalid_data['handle'], 'did': valid_data['did']}, FooModel, strict_string_format=True)
    assert 'must be a domain name' in str(exc_info.value)

    # Test invalid did fails
    with pytest.raises(ModelError) as exc_info:
        get_or_create({'handle': valid_data['handle'], 'did': invalid_data['did']}, FooModel, strict_string_format=True)
    assert 'must be in format did:method:identifier' in str(exc_info.value)

    # Test that validation is skipped when strict_string_format=False
    instance = get_or_create(
        {'handle': invalid_data['handle'], 'did': invalid_data['did']}, FooModel, strict_string_format=False
    )
    assert isinstance(instance, FooModel)
    assert instance.handle == invalid_data['handle']
    assert instance.did == invalid_data['did']
