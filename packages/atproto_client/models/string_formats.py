"""AT Protocol string format validation."""

import re
from datetime import datetime
from functools import wraps
from typing import Callable, Mapping, Set, Union, cast
from urllib.parse import urlparse

from atproto_core.nsid import validate_nsid as atproto_core_validate_nsid
from pydantic import BeforeValidator, Field, ValidationInfo
from pydantic_core import core_schema
from typing_extensions import Annotated, Literal

_OPT_IN_KEY: Literal['strict_string_format'] = 'strict_string_format'

# constants
MAX_HANDLE_LENGTH: int = 253
MAX_NSID_LENGTH: int = 317
MAX_RECORD_KEY_LENGTH: int = 512
MAX_URI_LENGTH: int = 8 * 1024
MIN_CID_LENGTH: int = 8
TID_LENGTH: int = 13
INVALID_RECORD_KEYS: Set[str] = {'.', '..'}
MAX_DID_LENGTH: int = 2048  # Method-specific identifier max length
MAX_AT_URI_LENGTH: int = 8 * 1024

# patterns
DOMAIN_RE = re.compile(r'^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z]$')
DID_RE = re.compile(
    r'^did:'  # Required prefix
    r'[a-z]+:'  # method-name (lowercase only)
    r'[a-zA-Z0-9._%-]{1,2048}'  # method-specific-id with length limit
    r'(?<!:)$'  # Cannot end with colon
)
LANG_RE = re.compile(r'^(i|[a-z]{2,3})(-[A-Za-z0-9-]+)?$')
RKEY_RE = re.compile(r'^[A-Za-z0-9._:~-]{1,512}$')
TID_RE = re.compile(rf'^[2-7a-z]{{{TID_LENGTH}}}$')
CID_RE = re.compile(r'^[A-Za-z0-9+]{8,}$')
AT_URI_RE = re.compile(
    r'^at://'  # Must start with at://
    r'('  # Authority group start
    # For DIDs: Only allowed chars are letters, numbers, period, hyphen, and percent
    r'did:[a-z]+:[a-zA-Z0-9.-]+'  # Notice removed underscore from allowed chars
    r'|'  # or
    # Handle: require 2+ segments, TLD can't start with digit
    r'[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'  # First segment
    r'(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*'  # Middle segments
    r'\.[a-zA-Z][a-zA-Z0-9-]*'  # TLD must start with letter
    r')'  # Authority group end
    r'(?:'  # Optional path group
    r'/[a-z][a-zA-Z0-9-]*(\.[a-z][a-zA-Z0-9-])+'  # NSID
    r'(?:/[A-Za-z0-9._:~-]+)?'  # Optional record key
    r')?$'
)


class _NamedValidator:
    """Decorator to add a __str__ attribute to a validation function."""

    def __init__(self, validate_fn: Callable[..., str]) -> None:
        self.validate_fn = validate_fn

    def __call__(self, v: str, info: ValidationInfo) -> str:
        return self.validate_fn(v, info)

    def __str__(self) -> str:
        func_str = f':func:`string_formats.{self.validate_fn.__name__}`'
        return f'Validated by: {func_str} (only when `strict_string_format=True`)'


def only_validate_if_strict(validate_fn: Callable[..., str]) -> Callable[..., str]:
    """Skip pydantic validation if not opting into strict validation via context."""

    @wraps(validate_fn)
    def wrapper(v: str, info: ValidationInfo) -> str:
        """Could likely be generalized to support arbitrary signatures."""
        if info and isinstance(info.context, Mapping) and info.context.get(_OPT_IN_KEY, False):
            return cast(core_schema.WithInfoValidatorFunction, validate_fn)(v, info)
        return v

    return wrapper


@only_validate_if_strict
def validate_handle(v: str, _: ValidationInfo) -> str:
    """Validate an AT Protocol Handle Identifier.

    A handle must be a valid domain name with:

    - 2+ segments separated by dots

    - ASCII alphanumeric characters and hyphens only

    - 1-63 chars per segment

    - Max 253 chars total

    - Last segment cannot start with a digit

    Args:
        v: The handle to validate (e.g. alice.bsky.social)

    Returns:
        The validated handle

    Raises:
        ValueError: If handle format is invalid
    """
    # Check ASCII first
    if not v.isascii():
        raise ValueError('Invalid handle: must contain only ASCII characters')

    # Use the spec's reference regex
    if not DOMAIN_RE.match(v.lower()) or len(v) > MAX_HANDLE_LENGTH:
        raise ValueError(
            f'Invalid handle: must be a domain name (e.g. user.bsky.social) with max length {MAX_HANDLE_LENGTH}'
        )

    return v


@only_validate_if_strict
def validate_did(v: str, _: ValidationInfo) -> str:
    """Validate a Decentralized Identifiers (DID).

    A DID must follow the pattern:

    - Format: did:method:identifier

    - Method must be lowercase letters

    - Identifier allows alphanumeric chars, dots, underscores, hyphens, and percent

    - Max 2KB length

    - No /?#[]@ characters allowed

    - Valid percent-encoding if used

    Args:
        v: The DID to validate (e.g. did:plc:z72i7hdynmk6r22z27h6tvur)

    Returns:
        The validated DID

    Raises:
        ValueError: If DID format is invalid
    """
    # Check for invalid characters
    if any(c in v for c in '/?#[]@'):
        raise ValueError('Invalid DID: cannot contain /, ?, #, [, ], or @ characters')

    # Check for invalid percent encoding
    if '%' in v:
        percent_segments = v.split('%')[1:]
        for segment in percent_segments:
            if len(segment) < 2 or not segment[:2].isalnum():
                raise ValueError('Invalid DID: invalid percent-encoding')

    # Check against regex pattern (which now includes length restriction)
    if not DID_RE.match(v):
        raise ValueError('Invalid DID: must be in format did:method:identifier (e.g. did:plc:1234abcd)')

    return v


@only_validate_if_strict
def validate_nsid(v: str, _: ValidationInfo) -> str:
    """Validate an AT Protocol NSID (Namespaced Identifier).

    An NSID must have:

    - 3+ segments separated by dots

    - Reversed domain name (lowercase alphanumeric + hyphen)

    - Name segment (letters only)

    - Max 317 chars total

    - No segments ending in numbers

    - No @_*#! special characters

    - Max 63 chars per segment

    Args:
        v: The NSID to validate (e.g. app.bsky.feed.post)

    Returns:
        The validated NSID

    Raises:
        ValueError: If NSID format is invalid
    """
    if (
        not atproto_core_validate_nsid(v, soft_fail=True)
        or len(v) > MAX_NSID_LENGTH
        or any(c in v for c in '@_*#!')  # Explicitly disallow special chars
        or any(len(seg) > 63 for seg in v.split('.'))  # Max segment length
        or any(seg[-1].isdigit() for seg in v.split('.'))  # No segments ending in numbers
    ):
        raise ValueError(
            f'Invalid NSID: must be dot-separated segments (e.g. app.bsky.feed.post) with max length {MAX_NSID_LENGTH}'
        )
    return v


@only_validate_if_strict
def validate_language(v: str, _: ValidationInfo) -> str:
    """Validate an ISO language code.

    Must match pattern:

    - 2-3 letter language code or 'i'

    - Optional subtag with alphanumeric chars and hyphens

    Args:
        v: The language code to validate (e.g. en or en-US)

    Returns:
        The validated language code

    Raises:
        ValueError: If language code format is invalid
    """
    if not LANG_RE.match(v):
        raise ValueError('Invalid language code: must be ISO language code (e.g. en or en-US)')
    return v


@only_validate_if_strict
def validate_record_key(v: str, _: ValidationInfo) -> str:
    """Validate an AT Protocol Record Key (rkey).

    A record key must:

    - Be 1-512 characters

    - Contain only alphanumeric chars, dots, underscores, colons, tildes, or hyphens

    - Not be "." or ".."

    Args:
        v: The record key to validate (e.g. 3jxtb5w2hkt2m)

    Returns:
        The validated record key

    Raises:
        ValueError: If record key format is invalid
    """
    if v in INVALID_RECORD_KEYS or not RKEY_RE.match(v):
        raise ValueError(
            'Invalid record key: must contain only alphanumeric, dot, underscore, colon, tilde, or hyphen characters'
        )
    return v


@only_validate_if_strict
def validate_cid(v: str, _: ValidationInfo) -> str:
    """Validate a Content Identifier (CID).

    Must be:

    - Minimum 8 characters

    - Alphanumeric characters and plus signs only

    Args:
        v: The CID to validate (e.g. bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi)

    Returns:
        The validated CID

    Raises:
        ValueError: If CID format is invalid
    """
    if not CID_RE.match(v):
        raise ValueError('Invalid CID: must be a valid Content Identifier with minimum length 8')
    return v


@only_validate_if_strict
def validate_at_uri(v: str, _: ValidationInfo) -> str:
    """Validate an AT Protocol URI.

    Must follow pattern:

    - Starts with at://

    - Contains handle or DID

    - Optional /collection/record-key path

    - Max 8KB length

    - No query parameters or fragments

    Args:
        v: The AT-URI to validate (e.g. at://alice.bsky.social/app.bsky.feed.post/3jxtb5w2hkt2m)

    Returns:
        The validated AT-URI

    Raises:
        ValueError: If AT-URI format is invalid
    """
    if len(v) >= MAX_AT_URI_LENGTH:
        raise ValueError(f'Invalid AT-URI: must be under {MAX_AT_URI_LENGTH} chars')

    if not AT_URI_RE.match(v):
        raise ValueError('Invalid AT-URI: invalid format')

    return v


@only_validate_if_strict
def validate_datetime(v: str, _: ValidationInfo) -> str:
    """Validate an ISO 8601/RFC 3339 datetime string.

    Requirements:

    - Must use uppercase T as time separator

    - Must include seconds (HH:MM:SS)

    - Must have timezone (Z or ±HH:MM)

    - No -00:00 timezone allowed

    - Valid fractional seconds format if used

    - No whitespace allowed

    Args:
        v: The datetime string to validate (e.g. 2024-11-24T06:02:00Z)

    Returns:
        The validated datetime string

    Raises:
        ValueError: If datetime format is invalid
    """
    # Must contain uppercase T and Z if used
    if v != v.strip():
        raise ValueError('Invalid datetime: no whitespace allowed')

    # Must contain uppercase T
    if 'T' not in v or ('z' in v and 'Z' not in v):
        raise ValueError('Invalid datetime: must contain uppercase T separator')

    # Must have seconds (HH:MM:SS)
    time_part = v.split('T')[1]
    if len(time_part.split(':')) != 3:
        raise ValueError('Invalid datetime: seconds are required')

    # If has decimal point, must have digits after it
    if '.' in v and not re.search(r'\.\d+', v):
        raise ValueError('Invalid datetime: invalid fractional seconds format')

    # Must match exactly timezone pattern with nothing after
    if v.endswith('-00:00'):
        raise ValueError('Invalid datetime: -00:00 timezone not allowed')
    if not (re.match(r'.*Z$', v) or re.match(r'.*[+-]\d{2}:\d{2}$', v)):
        raise ValueError('Invalid datetime: must include timezone')

    # Final validation
    try:
        datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    except ValueError:
        raise ValueError('Invalid datetime: invalid format') from None


@only_validate_if_strict
def validate_tid(v: str, _: ValidationInfo) -> str:
    """Validate an AT Protocol TID (Timestamp Identifiers).

    Must be:

    - Exactly 13 characters

    - Only lowercase letters and numbers 2-7

    - First byte's high bit (0x40) must be 0

    Args:
        v: The TID to validate (e.g. 3jxtb5w2hkt2m)

    Returns:
        The validated TID

    Raises:
        ValueError: If TID format is invalid
    """
    if not TID_RE.match(v) or (ord(v[0]) & 0x40):
        raise ValueError(f'Invalid TID: must be exactly {TID_LENGTH} lowercase letters/numbers')
    return v


@only_validate_if_strict
def validate_uri(v: str, _: ValidationInfo) -> str:
    """Validate a standard URI.

    Requirements:

    - Must have a scheme starting with a letter

    - Must have authority (netloc) or path/query/fragment

    - Max 8KB length

    - No spaces allowed

    - Must follow RFC-3986 format

    Args:
        v: The URI to validate (e.g. https://example.com/path)

    Returns:
        The validated URI

    Raises:
        ValueError: If URI format is invalid
    """
    if len(v) >= MAX_URI_LENGTH or ' ' in v:
        raise ValueError(f'Invalid URI: must be under {MAX_URI_LENGTH} chars and not contain spaces')
    parsed = urlparse(v)
    if not (
        parsed.scheme
        and parsed.scheme[0].isalpha()
        and (parsed.netloc or parsed.path or parsed.query or parsed.fragment)
    ):
        raise ValueError('Invalid URI: must be a valid URI with scheme and authority/path (e.g. https://example.com)')
    return v


Handle = Annotated[str, BeforeValidator(_NamedValidator(validate_handle))]
Did = Annotated[str, BeforeValidator(_NamedValidator(validate_did))]
Nsid = Annotated[str, BeforeValidator(_NamedValidator(validate_nsid))]
Language = Annotated[str, BeforeValidator(_NamedValidator(validate_language))]
RecordKey = Annotated[str, BeforeValidator(_NamedValidator(validate_record_key))]
Cid = Annotated[str, BeforeValidator(_NamedValidator(validate_cid))]
AtUri = Annotated[str, BeforeValidator(_NamedValidator(validate_at_uri))]
DateTime = Annotated[str, BeforeValidator(_NamedValidator(validate_datetime))]  # see pydantic-extra-types #239
Tid = Annotated[str, BeforeValidator(_NamedValidator(validate_tid))]
Uri = Annotated[str, BeforeValidator(_NamedValidator(validate_uri))]

AtIdentifier = Union[Handle, Did]

# Any valid ATProto string format
AtProtoString = Annotated[
    Union[Handle, Did, Nsid, AtUri, Cid, DateTime, Tid, RecordKey, Uri, Language],
    Field(description='ATProto string format'),
]
