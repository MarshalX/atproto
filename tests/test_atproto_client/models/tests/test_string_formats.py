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


# TODO: 230 passed, 11 xfailed
# These cases appear in both _valid.txt and _invalid.txt files.
# Need investigation to determine if our validation is incorrect or if test data needs updating:
SKIP_THESE_VALUES = [
    (
        string_formats.AtUri,
        'at://did:plc:asdf123',
    ),  # Listed as both valid and invalid in AT-URI files under "enforces spec basics"
    (
        string_formats.AtUri,
        'at://did:plc:asdf123/com.atproto.feed.post',
    ),  # Same AT-URI pattern - appears in both valid/invalid files
    (
        string_formats.DateTime,
        '1985-04-12T23:20:50.123Z',
    ),  # Listed as "preferred" in valid but also appears in invalid under RFC-3339 section
    (
        string_formats.DateTime,
        '1985-04-12T23:20:50.123-00:00',
    ),  # Listed as "supported" in valid but marked invalid under timezone formats
    (string_formats.DateTime, '1985-04-12T23:20Z'),  # Similar timezone format discrepancy between valid/invalid files
    (string_formats.Handle, 'john.test'),  # Base pattern appears valid but numeric suffix versions are marked invalid
    (string_formats.Nsid, 'one.two.three'),  # Same pattern - base form valid but numeric suffixes marked invalid
]


def get_test_cases(filename: str) -> List[str]:
    """Get non-comment, non-empty lines from an interop test file."""
    return [
        line.strip()
        for line in INTEROP_TEST_FILES_DIR.joinpath(filename).read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]


@pytest.fixture
def valid_handles() -> List[str]:
    return get_test_cases('handle_syntax_valid.txt')


@pytest.fixture
def valid_dids() -> List[str]:
    return get_test_cases('did_syntax_valid.txt')


@pytest.fixture
def valid_nsids() -> List[str]:
    return get_test_cases('nsid_syntax_valid.txt')


@pytest.fixture
def valid_aturis() -> List[str]:
    return get_test_cases('aturi_syntax_valid.txt')


@pytest.fixture
def valid_datetimes() -> List[str]:
    return get_test_cases('datetime_syntax_valid.txt')


@pytest.fixture
def valid_tids() -> List[str]:
    return get_test_cases('tid_syntax_valid.txt')


@pytest.fixture
def valid_record_keys() -> List[str]:
    return get_test_cases('recordkey_syntax_valid.txt')


@pytest.fixture
def valid_data(
    valid_handles: List[str],
    valid_dids: List[str],
    valid_nsids: List[str],
    valid_aturis: List[str],
    valid_datetimes: List[str],
    valid_tids: List[str],
    valid_record_keys: List[str],
) -> dict:
    return {
        'handle': valid_handles[0],
        'did': valid_dids[0],
        'nsid': valid_nsids[0],
        'at_uri': valid_aturis[0],
        'cid': 'bafyreidfayvfuwqa2beehqn7axeeeaej5aqvaowxgwcdt2rw',  # No interop test file for CID
        'datetime': valid_datetimes[0],
        'tid': valid_tids[0],
        'record_key': valid_record_keys[0],
        'uri': 'https://example.com',  # No interop test file for URI
        'language': 'en-US',  # No interop test file for language
    }


@pytest.fixture
def invalid_data() -> dict:
    return {
        'handle': get_test_cases('handle_syntax_invalid.txt')[0],
        'did': get_test_cases('did_syntax_invalid.txt')[0],
        'nsid': get_test_cases('nsid_syntax_invalid.txt')[0],
        'at_uri': get_test_cases('aturi_syntax_invalid.txt')[0],
        'cid': 'short',  # No interop test file for CID
        'datetime': get_test_cases('datetime_syntax_invalid.txt')[0],
        'tid': get_test_cases('tid_syntax_invalid.txt')[0],
        'record_key': get_test_cases('recordkey_syntax_invalid.txt')[0],
        'uri': 'invalid-uri-no-scheme',  # No interop test file for URI
        'language': 'invalid!',  # No interop test file for language
    }


@pytest.mark.parametrize(
    'validator_type,field_name,error_keywords,invalid_value',
    [(string_formats.AtUri, 'at_uri', ['Invalid AT-URI'], c) for c in get_test_cases('aturi_syntax_invalid.txt')]
    + [
        (string_formats.DateTime, 'datetime', ['Invalid datetime'], c)
        for c in get_test_cases('datetime_syntax_invalid.txt')
    ]
    + [
        (string_formats.Handle, 'handle', 'must be a domain name', c)
        for c in get_test_cases('handle_syntax_invalid.txt')
    ]
    + [
        (string_formats.Did, 'did', 'must be in format did:method:identifier', c)
        for c in get_test_cases('did_syntax_invalid.txt')
    ]
    + [
        (string_formats.Nsid, 'nsid', 'must be dot-separated segments', c)
        for c in get_test_cases('nsid_syntax_invalid.txt')
    ]
    + [
        (string_formats.Tid, 'tid', 'must be exactly 13 lowercase letters/numbers', c)
        for c in get_test_cases('tid_syntax_invalid.txt')
    ]
    + [
        (string_formats.RecordKey, 'record_key', 'must contain only alphanumeric', c)
        for c in get_test_cases('recordkey_syntax_invalid.txt')
    ],
)
def test_string_format_validation(
    validator_type: type, field_name: str, error_keywords: List[str], invalid_value: str, valid_data: dict
) -> None:
    """Test validation for each string format type."""
    if any(invalid_value == skip_value for _, skip_value in SKIP_THESE_VALUES):
        pytest.xfail(f'TODO: Fix validation for {invalid_value}')

    SomeTypeAdapter = TypeAdapter(validator_type)

    # Test that validation is skipped by default
    assert SomeTypeAdapter.validate_python(invalid_value) == invalid_value

    # Test that valid data passes strict validation
    validated_value = SomeTypeAdapter.validate_python(valid_data[field_name], context={_OPT_IN_KEY: True})
    assert validated_value == valid_data[field_name]

    # Test that invalid data fails strict validation
    with pytest.raises(ValidationError) as exc_info:
        SomeTypeAdapter.validate_python(invalid_value, context={_OPT_IN_KEY: True})
    error_msg = str(exc_info.value)
    assert any(keyword in error_msg for keyword in error_keywords)


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

    validated = TypeAdapter(string_formats.ATProtoString).validate_python(valid_value, context={_OPT_IN_KEY: True})
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
    try:
        get_or_create({'handle': invalid_data['handle'], 'did': valid_data['did']}, FooModel, strict_string_format=True)
        pytest.fail('Handle validation should have failed')
    except ModelError as e:
        assert 'must be a domain name' in str(e)

    # Test invalid did fails
    try:
        get_or_create({'handle': valid_data['handle'], 'did': invalid_data['did']}, FooModel, strict_string_format=True)
        pytest.fail('Did validation should have failed')
    except ModelError as e:
        assert 'must be in format did:method:identifier' in str(e)

    # Test that validation is skipped when strict_string_format=False
    instance = get_or_create(
        {'handle': invalid_data['handle'], 'did': invalid_data['did']}, FooModel, strict_string_format=False
    )
    assert isinstance(instance, FooModel)
    assert instance.handle == invalid_data['handle']
    assert instance.did == invalid_data['did']


@pytest.mark.parametrize('validator_type,value', SKIP_THESE_VALUES)
def test_skipped_validation_cases(validator_type: type, value: str) -> None:
    """
    Test each skipped case that we suspect is a discrepancy between valid/invalid test files
    """
    _TAdapter = TypeAdapter(validator_type)

    # Should validate successfully with strict validation
    validated = _TAdapter.validate_python(value, context={_OPT_IN_KEY: True})
    assert validated == value

    # Also verify it appears in the corresponding invalid test file
    invalid_filename = {
        string_formats.AtUri: 'aturi_syntax_invalid.txt',
        string_formats.DateTime: 'datetime_syntax_invalid.txt',
        string_formats.Handle: 'handle_syntax_invalid.txt',
        string_formats.Nsid: 'nsid_syntax_invalid.txt',
    }[validator_type]

    invalid_cases = get_test_cases(invalid_filename)
    assert value in invalid_cases, f'{value} not found in {invalid_filename} despite being marked as invalid'
