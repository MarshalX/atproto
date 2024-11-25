import re
from datetime import datetime
from typing import Callable, Mapping, Set, Union
from urllib.parse import urlparse

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
NSID_RE = re.compile(
    r'(?![0-9])'  # Can't start with number
    r'((?!-)[a-z0-9-]{1,63}(?<!-)\.){2,}'  # At least 2 segments, each 1-63 chars
    r'[a-zA-Z]'  # Last segment must start with letter
    r'[a-zA-Z0-9-]*'  # Middle chars
    r'[a-zA-Z]'  # Must end with letter
    r'$'  # End of string
)
LANG_RE = re.compile(r'^(i|[a-z]{2,3})(-[A-Za-z0-9-]+)?$')
RKEY_RE = re.compile(r'^[A-Za-z0-9._:~-]{1,512}$')
TID_RE = re.compile(rf'^[2-7a-z]{{{TID_LENGTH}}}$')
CID_RE = re.compile(r'^[A-Za-z0-9+]{8,}$')
AT_URI_RE = re.compile(
    r'^at://'  # Protocol
    r'('  # Authority is either:
    r'([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z]'  # Handle (must be domain)
    r'|'  # or
    r'did:[a-z]+:[a-zA-Z0-9._%-]+'  # DID
    r')'
    r'(/[a-z][a-zA-Z0-9-]*(\.[a-z][a-zA-Z0-9-]*)+(/[a-zA-Z0-9._:~-]+)?)?$'  # Optional COLLECTION/RKEY
)


def only_validate_if_strict(validate_fn: core_schema.WithInfoValidatorFunction) -> Callable:
    """Skip validation if not opting into strict validation."""

    def wrapper(v: str, info: ValidationInfo) -> str:
        if info and isinstance(info.context, Mapping) and info.context.get(_OPT_IN_KEY, False):
            return validate_fn(v, info)
        return v

    return wrapper


@only_validate_if_strict
def validate_handle(v: str, info: ValidationInfo) -> str:
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
def validate_did(v: str, info: ValidationInfo) -> str:
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
def validate_nsid(v: str, info: ValidationInfo) -> str:
    if (
        not NSID_RE.match(v)
        or '..' in v  # No double dots
        or len(v) > MAX_NSID_LENGTH
        or any(c in v for c in '@_*#!')  # Explicitly disallow special chars
        or not all(seg for seg in v.split('.'))  # No empty segments
        or any(len(seg) > 63 for seg in v.split('.'))  # Max segment length
        or any(seg[-1].isdigit() for seg in v.split('.'))  # No segments ending in numbers
        or any(seg.endswith('-') for seg in v.split('.'))  # No segments ending in hyphen
    ):
        raise ValueError(
            f'Invalid NSID: must be dot-separated segments (e.g. app.bsky.feed.post) with max length {MAX_NSID_LENGTH}'
        )
    return v


@only_validate_if_strict
def validate_language(v: str, info: ValidationInfo) -> str:
    if not LANG_RE.match(v):
        raise ValueError('Invalid language code: must be ISO language code (e.g. en or en-US)')
    return v


@only_validate_if_strict
def validate_record_key(v: str, info: ValidationInfo) -> str:
    if v in INVALID_RECORD_KEYS or not RKEY_RE.match(v):
        raise ValueError(
            'Invalid record key: must contain only alphanumeric, dot, underscore, colon, tilde, or hyphen characters'
        )
    return v


@only_validate_if_strict
def validate_cid(v: str, info: ValidationInfo) -> str:
    if not CID_RE.match(v):
        raise ValueError('Invalid CID: must be a valid Content Identifier with minimum length 8')
    return v


@only_validate_if_strict
def validate_at_uri(v: str, info: ValidationInfo) -> str:
    # Check length
    if len(v) >= MAX_AT_URI_LENGTH:
        raise ValueError(f'Invalid AT-URI: must be under {MAX_AT_URI_LENGTH} chars')

    # Check for invalid path patterns
    if (
        '/./' in v  # No dot segments
        or '/../' in v
        or v.endswith('/')  # No trailing slashes
        or '#' in v  # No fragments
        or '?' in v  # No query params
        or (
            '%' in v  # Check percent encoding
            and not re.match(r'%[0-9A-Fa-f]{2}', v[v.index('%') :])
        )
    ):
        raise ValueError(
            (
                'Invalid AT-URI: must not contain /./, /../, trailing slashes,'
                ' fragments, queries, or invalid percent encoding'
            )
        )

    parts = v[5:].split('/')  # Skip 'at://'

    # Must have valid authority
    if len(parts) < 1:
        raise ValueError('Invalid AT-URI: missing authority')

    # If there's a path, must have collection
    if len(parts) > 1:
        if len(parts) == 2:
            try:
                validate_nsid(parts[1], info)
            except ValueError:
                raise ValueError('Invalid AT-URI: collection must be a valid NSID') from None
        else:
            raise ValueError('Invalid AT-URI: must be in format at://authority/collection[/record]')

    # Basic format check still needed for authority validation
    if not AT_URI_RE.match(v):
        raise ValueError('Invalid AT-URI: invalid authority format')

    return v


@only_validate_if_strict
def validate_datetime(v: str, info: ValidationInfo) -> str:
    # Must contain T separator
    if 'T' not in v:
        raise ValueError('Invalid datetime: must contain T separator')

    # Must have timezone
    orig_val = v
    v = re.sub(r'([+-][0-9]{2}:[0-9]{2}|Z)$', '', orig_val)
    if v == orig_val:
        raise ValueError('Invalid datetime: must include timezone (Z or +/-HH:MM)')

    # Strip fractional seconds before parsing
    v = re.sub(r'\.[0-9]+$', '', v)

    try:
        datetime.fromisoformat(v)
        return orig_val
    except ValueError:
        raise ValueError('Invalid datetime: must be valid ISO 8601 format') from None


@only_validate_if_strict
def validate_tid(v: str, info: ValidationInfo) -> str:
    if not TID_RE.match(v) or (ord(v[0]) & 0x40):
        raise ValueError(f'Invalid TID: must be exactly {TID_LENGTH} lowercase letters/numbers')
    return v


@only_validate_if_strict
def validate_uri(v: str, info: ValidationInfo) -> str:
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


Handle = Annotated[str, BeforeValidator(validate_handle)]
Did = Annotated[str, BeforeValidator(validate_did)]
Nsid = Annotated[str, BeforeValidator(validate_nsid)]
Language = Annotated[str, BeforeValidator(validate_language)]
RecordKey = Annotated[str, BeforeValidator(validate_record_key)]
Cid = Annotated[str, BeforeValidator(validate_cid)]
AtUri = Annotated[str, BeforeValidator(validate_at_uri)]
DateTime = Annotated[str, BeforeValidator(validate_datetime)]  # see pydantic-extra-types #239
Tid = Annotated[str, BeforeValidator(validate_tid)]
Uri = Annotated[str, BeforeValidator(validate_uri)]

# Any valid ATProto string format
ATProtoString = Annotated[
    Union[Handle, Did, Nsid, AtUri, Cid, DateTime, Tid, RecordKey, Uri, Language],
    Field(description='ATProto string format'),
]
