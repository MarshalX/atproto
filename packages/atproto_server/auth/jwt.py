import binascii
import json
import typing as t
from dataclasses import dataclass
from datetime import datetime, timezone

from atproto_crypto.verify import verify_signature

from atproto_server.auth.utils import base64url_decode
from atproto_server.exceptions import (
    TokenDecodeError,
    TokenExpiredSignatureError,
    TokenImmatureSignatureError,
    TokenInvalidAudienceError,
    TokenInvalidIssuedAtError,
    TokenInvalidSignatureError,
)

GetSigningKeyCallback = t.Callable[[str, bool], str]
GetSigningKeyCallbackAsync = t.Callable[[str, bool], t.Coroutine[t.Any, t.Any, str]]


@dataclass
class JwtPayload:
    exp: int  # expired at
    iat: t.Optional[int] = None  # created at
    scope: t.Optional[str] = None
    sub: t.Optional[str] = None  # DID
    iss: t.Optional[str] = None  # DID. In service token
    aud: t.Optional[str] = None  # DID
    jti: t.Optional[str] = None  # in refresh token only


def parse_jwt(jwt: t.Union[str, bytes]) -> t.Tuple[bytes, bytes, t.Dict[str, t.Any], bytes]:
    if isinstance(jwt, str):
        jwt = jwt.encode('UTF-8')

    if not isinstance(jwt, bytes):
        raise TokenDecodeError(f'Invalid token type. Token must be a {bytes}')

    try:
        signing_input, crypto_segment = jwt.rsplit(b'.', 1)
        header_segment, payload_segment = signing_input.split(b'.', 1)
    except ValueError as e:
        raise TokenDecodeError('Not enough segments') from e

    try:
        header_data = base64url_decode(header_segment)
    except (TypeError, binascii.Error) as e:
        raise TokenDecodeError('Invalid header padding') from e

    try:
        header = json.loads(header_data)
    except ValueError as e:
        raise TokenDecodeError(f'Invalid header string: {e}') from e

    if not isinstance(header, dict):
        raise TokenDecodeError('Invalid header string: must be a json object')

    try:
        payload = base64url_decode(payload_segment)
    except (TypeError, binascii.Error) as e:
        raise TokenDecodeError('Invalid payload padding') from e

    try:
        signature = base64url_decode(crypto_segment)
    except (TypeError, binascii.Error) as e:
        raise TokenDecodeError('Invalid crypto padding') from e

    return payload, signing_input, header, signature


def decode_jwt_payload(payload: t.Union[str, bytes]) -> JwtPayload:
    try:
        plain_payload = json.loads(payload)
    except ValueError as e:
        raise TokenDecodeError(f'Invalid payload string: {e}') from e
    if not isinstance(plain_payload, dict):
        raise TokenDecodeError('Invalid payload string: must be a json object')

    return JwtPayload(**plain_payload)


def get_jwt_payload(jwt: str) -> JwtPayload:
    payload, *_ = parse_jwt(jwt)
    return decode_jwt_payload(payload)


def _validate_exp(
    exp: int,
    now: float,
    leeway: float,
) -> None:
    try:
        exp = int(exp)
    except ValueError as e:
        raise TokenDecodeError('Expiration Time claim (exp) must be an integer.') from e

    if exp <= (now - leeway):
        raise TokenExpiredSignatureError('Signature has expired')


def _validate_iat(
    iat: int,
    now: float,
    leeway: float,
) -> None:
    try:
        iat = int(iat)
    except ValueError as e:
        raise TokenInvalidIssuedAtError('Issued At claim (iat) must be an integer.') from e
    if iat > (now + leeway):
        raise TokenImmatureSignatureError('The token is not yet valid (iat)')


def validate_jwt_payload(payload: JwtPayload, leeway: int = 0) -> None:
    now = datetime.now(tz=timezone.utc).timestamp()

    _validate_exp(payload.exp, now, leeway)
    _validate_iat(payload.iat, now, leeway)


def _verify_signature(signing_key: str, signing_input: bytes, signature: bytes) -> bool:
    try:
        return verify_signature(signing_key, signing_input, signature)
    except Exception as e:  # noqa: BLE001
        raise TokenInvalidSignatureError('Could not verify JWT signature') from e


def verify_jwt(
    jwt: str, get_signing_key_callback: GetSigningKeyCallback, own_did: t.Optional[str] = None
) -> JwtPayload:
    plain_payload, signing_input, header, signature = parse_jwt(jwt)

    payload = decode_jwt_payload(plain_payload)
    validate_jwt_payload(payload)

    if own_did and payload.aud != own_did:
        raise TokenInvalidAudienceError('Invalid subject')

    signing_key = get_signing_key_callback(payload.iss, False)
    if _verify_signature(signing_key, signing_input, signature):
        return payload

    fresh_signing_key = get_signing_key_callback(payload.iss, True)  # get signing key without a cache
    if fresh_signing_key == signing_key:
        raise TokenInvalidSignatureError('Could not verify JWT signature. Fresh signing key is equal to the old one')

    if _verify_signature(fresh_signing_key, signing_input, signature):
        return payload

    # this code should be unreachable
    # verifying methods must raise exception before
    raise TokenInvalidSignatureError('Invalid signature')


async def verify_jwt_async(
    jwt: str, get_signing_key_callback: GetSigningKeyCallbackAsync, own_did: t.Optional[str] = None
) -> JwtPayload:
    plain_payload, signing_input, header, signature = parse_jwt(jwt)

    payload = decode_jwt_payload(plain_payload)
    validate_jwt_payload(payload)

    if own_did and payload.aud != own_did:
        raise TokenInvalidAudienceError('Invalid subject')

    signing_key = await get_signing_key_callback(payload.iss, False)
    if _verify_signature(signing_key, signing_input, signature):
        return payload

    fresh_signing_key = await get_signing_key_callback(payload.iss, True)  # get signing key without a cache
    if fresh_signing_key == signing_key:
        raise TokenInvalidSignatureError('Could not verify JWT signature. Fresh signing key is equal to the old one')

    if _verify_signature(fresh_signing_key, signing_input, signature):
        return payload

    # this code should be unreachable
    # verifying methods must raise exception before
    raise TokenInvalidSignatureError('Invalid signature')
