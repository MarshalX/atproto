import re
import string
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

# patterns
DOMAIN_RE = re.compile(r'([a-z0-9][a-z0-9-]{0,62}(?<!-)\.){1,}[a-z][a-z0-9-]*(?<!-)')
DID_RE = re.compile(r'did:[a-z]+:[A-Za-z0-9._%:-]{1,2048}(?<!:)')
NSID_RE = re.compile(r'(?![0-9])((?!-)[a-z0-9-]{1,63}(?<!-)\.){2,}[a-zA-Z]{1,63}')
LANG_RE = re.compile(r'^(i|[a-z]{2,3})(-[A-Za-z0-9-]+)?$')
RKEY_RE = re.compile(r'^[A-Za-z0-9._:~-]{1,512}$')
TID_RE = re.compile(rf'^[{string.ascii_lowercase}234567]{{{TID_LENGTH}}}$')
CID_RE = re.compile(r'^[A-Za-z0-9+]{8,}$')
AT_URI_RE = re.compile(r'at://[^/]+(/[^/]+(/[^/]+)?)?')


def only_validate_if_strict(validate_fn: core_schema.WithInfoValidatorFunction) -> Callable:
    """Skip validation if not opting into strict validation."""

    def wrapper(v: str, info: ValidationInfo) -> str:
        if not (info and isinstance(info.context, Mapping) and info.context.get(_OPT_IN_KEY, False)):
            return v
        return validate_fn(v, info)

    return wrapper


@only_validate_if_strict
def validate_handle(v: str, info: ValidationInfo) -> str:
    if not DOMAIN_RE.match(v.lower()) or len(v) > MAX_HANDLE_LENGTH:
        raise ValueError(
            f'Invalid handle: must be a domain name (e.g. user.bsky.social) with max length {MAX_HANDLE_LENGTH}'
        )
    return v


@only_validate_if_strict
def validate_did(v: str, info: ValidationInfo) -> str:
    if not DID_RE.match(v):
        raise ValueError('Invalid DID: must be in format did:method:identifier (e.g. did:plc:1234abcd)')
    return v


@only_validate_if_strict
def validate_nsid(v: str, info: ValidationInfo) -> str:
    if not NSID_RE.match(v) or '.' not in v or len(v) > MAX_NSID_LENGTH:
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
    if len(v) >= MAX_URI_LENGTH or '/./' in v or '/../' in v or v.endswith(('/.', '/..')):
        raise ValueError(f'Invalid AT-URI: must be under {MAX_URI_LENGTH} chars and not contain /./ or /../ patterns')
    if not AT_URI_RE.match(v):
        raise ValueError(
            'Invalid AT-URI: must be in format at://authority/collection/record (e.g. at://user.bsky.social/posts/123)'
        )
    return v


@only_validate_if_strict
def validate_datetime(v: str, info: ValidationInfo) -> str:
    if 'T' not in v or not any(v.endswith(x) for x in ('Z', '+00:00')):
        raise ValueError('Invalid datetime format: must be ISO 8601 with timezone (e.g. 2023-01-01T12:00:00Z)')
    try:
        datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    except ValueError:
        raise ValueError(
            'Invalid datetime format: must be ISO 8601 with timezone (e.g. 2023-01-01T12:00:00Z)'
        ) from None


@only_validate_if_strict
def validate_tid(v: str, info: ValidationInfo) -> str:
    if not TID_RE.match(v):
        raise ValueError(f'Invalid TID format: must be exactly {TID_LENGTH} lowercase letters/numbers')
    if ord(v[0]) & 0x40:
        raise ValueError('Invalid TID: high bit cannot be 1')
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
