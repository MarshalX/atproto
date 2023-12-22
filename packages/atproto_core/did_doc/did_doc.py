import typing as t
from dataclasses import dataclass
from urllib.parse import urlparse

from pydantic import BaseModel, Field, ValidationError

_AT_URI_PREFIX = 'at://'
_AT_URI_PREFIX_LEN = len(_AT_URI_PREFIX)
_ATPROTO_KEY_ID = '#atproto'


@dataclass
class SigningKey:
    type: str
    public_key_multibase: str


def get_did(did_doc: 'DidDocument') -> str:
    return did_doc.id


def get_handle(did_doc: 'DidDocument') -> t.Optional[str]:
    aka = did_doc.also_known_as
    if not aka:
        return None

    for name in aka:
        if name.startswith(_AT_URI_PREFIX):
            return name[_AT_URI_PREFIX_LEN:]

    return None


def get_signing_key(did_doc: 'DidDocument') -> t.Optional['SigningKey']:
    did = get_did(did_doc)

    keys = did_doc.verification_method
    if not keys:
        return None

    for key in keys:
        if (key.id == _ATPROTO_KEY_ID or key.id == f'{did}{_ATPROTO_KEY_ID}') and key.public_key_multibase:
            return SigningKey(type=key.type, public_key_multibase=key.public_key_multibase)

    return None


def _validate_url(url: str) -> t.Optional[str]:
    try:
        parsed_url = urlparse(url)
    except Exception:  # noqa: BLE001
        return None

    if parsed_url.scheme not in {'http', 'https'}:
        return None
    if parsed_url.hostname is None:
        return None

    return url


def get_service_endpoint(did_doc: 'DidDocument', id_: str, type_: str) -> t.Optional[str]:
    did = get_did(did_doc)

    services = did_doc.service
    if not services:
        return None

    for service in services:
        if (service.id == id_ or service.id == f'{did}{id_}') and service.type == type_:
            return _validate_url(service.service_endpoint)

    return None


def get_pds_endpoint(did_doc: 'DidDocument') -> t.Optional[str]:
    return get_service_endpoint(did_doc, '#atproto_pds', 'AtprotoPersonalDataServer')


def get_feed_gen_endpoint(did_doc: 'DidDocument') -> t.Optional[str]:
    return get_service_endpoint(did_doc, '#bsky_fg', 'BskyFeedGenerator')


def get_notif_endpoint(did_doc: 'DidDocument') -> t.Optional[str]:
    return get_service_endpoint(did_doc, '#bsky_notif', 'BskyNotificationService')


class VerificationMethod(BaseModel):
    id: str
    type: str
    controller: str
    public_key_multibase: t.Optional[str] = Field(default=None, alias='publicKeyMultibase')


class Service(BaseModel):
    id: str
    type: str
    service_endpoint: t.Union[str, dict] = Field(alias='serviceEndpoint')


class DidDocument(BaseModel):
    id: str
    also_known_as: t.Optional[t.List[str]] = Field(default=None, alias='alsoKnownAs')
    verification_method: t.Optional[t.List['VerificationMethod']] = Field(default=None, alias='verificationMethod')
    service: t.Optional[t.List['Service']] = None

    get_signing_key = get_signing_key
    get_handle = get_handle
    get_service_endpoint = get_service_endpoint
    get_pds_endpoint = get_pds_endpoint
    get_feed_gen_endpoint = get_feed_gen_endpoint
    get_notif_endpoint = get_notif_endpoint


def is_valid_did_doc(did_doc: dict) -> bool:
    try:
        parse_did_doc(did_doc)
        return True
    except ValidationError:
        return False


def parse_did_doc(did_doc: dict) -> DidDocument:
    return DidDocument(**did_doc)
