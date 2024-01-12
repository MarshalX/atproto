import typing as t

import pytest
from atproto_server.auth.jwt import get_jwt_payload, parse_jwt, validate_jwt_payload, verify_jwt, verify_jwt_async
from atproto_server.exceptions import TokenDecodeError, TokenExpiredSignatureError, TokenInvalidAudienceError

_TEST_JWT_EXPIRED = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJpc3MiOiJkaWQ6cGxjOmt2d3ZjbjVpcWZvb29wbXl6dmI0cXpiYSIsImF1ZCI6ImRpZDp3ZWI6ZmVlZC5hdHByb3RvLmJsdWUiLCJleHAiOjE3MDQ4NDExMzh9.50SlT6vw26HsDXVDM4D2D53_Dvzd6bjp3TDc5EyDVD4ob9i3EEB7fmaKE0XR4egMS9Kf9eMdVqH5gJNCaIah4Q'  # noqa: E501
# exp in 2033
_TEST_JWT_INVALID_SIGN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJpc3MiOiJkaWQ6cGxjOmt2d3ZjbjVpcWZvb29wbXl6dmI0cXpiYSIsImF1ZCI6ImRpZDp3ZWI6ZmVlZC5hdHByb3RvLmJsdWUiLCJleHAiOjIwMDAwMDAwMDB9.50SlT6vw26HsDXVDM4D2D53_Dvzd6bjp3TDc5EyDVD4ob9i3EEB7fmaKE0XR4egMS9Kf9eMdVqH5gJNCaIah4Q'  # noqa: E501


if t.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_parse_jwt_empty() -> None:
    with pytest.raises(TokenDecodeError):
        parse_jwt('')


def test_parse_jwt() -> None:
    payload, signing_input, header, signature = parse_jwt(_TEST_JWT_EXPIRED)

    assert header['typ'] == 'JWT'
    assert header['alg'] == 'ES256K'

    assert payload
    assert signing_input
    assert len(signature) == 64


def test_get_jwt_payload() -> None:
    payload = get_jwt_payload(_TEST_JWT_EXPIRED)
    assert payload.iss == 'did:plc:kvwvcn5iqfooopmyzvb4qzba'
    assert payload.aud == 'did:web:feed.atproto.blue'
    assert payload.exp == 1704841138


def test_validate_jwt_payload_expired() -> None:
    payload = get_jwt_payload(_TEST_JWT_EXPIRED)
    with pytest.raises(TokenExpiredSignatureError):
        validate_jwt_payload(payload)


def test_validate_jwt_payload_valid() -> None:
    payload = get_jwt_payload(_TEST_JWT_INVALID_SIGN)
    validate_jwt_payload(payload)


def test_verify_jwt_valid_signature(monkeypatch: 'MonkeyPatch') -> None:
    def get_signing_key(_: str, __: bool) -> str:
        return 'did:key:zQ3shc6V2kvUxn7hNmPy9JMToKT7u2NH27SnKNxGL1GcBcS4j'

    # allow expired token
    monkeypatch.setattr('atproto_server.auth.jwt._validate_exp', lambda *_: True)

    verify_jwt(_TEST_JWT_EXPIRED, get_signing_key)


def test_verify_jwt_aud_validation(monkeypatch: 'MonkeyPatch') -> None:
    expected_iss = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'
    expected_aud = 'did:web:feed.atproto.blue'

    def get_signing_key(iss: str, _: bool) -> str:
        assert iss == expected_iss
        return 'blabla'

    # allow invalid signature
    monkeypatch.setattr('atproto_server.auth.jwt._verify_signature', lambda *_: True)

    verify_jwt(_TEST_JWT_INVALID_SIGN, get_signing_key)
    verify_jwt(_TEST_JWT_INVALID_SIGN, get_signing_key, expected_aud)

    with pytest.raises(TokenInvalidAudienceError):
        verify_jwt(_TEST_JWT_INVALID_SIGN, get_signing_key, 'blabla')


@pytest.mark.asyncio
async def test_verify_jwt_aud_validation_async(monkeypatch: 'MonkeyPatch') -> None:
    expected_iss = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'
    expected_aud = 'did:web:feed.atproto.blue'

    async def get_signing_key(iss: str, _: bool) -> str:
        assert iss == expected_iss
        return 'blabla'

    # allow invalid signature
    monkeypatch.setattr('atproto_server.auth.jwt._verify_signature', lambda *_: True)

    await verify_jwt_async(_TEST_JWT_INVALID_SIGN, get_signing_key)
    await verify_jwt_async(_TEST_JWT_INVALID_SIGN, get_signing_key, expected_aud)

    with pytest.raises(TokenInvalidAudienceError):
        await verify_jwt_async(_TEST_JWT_INVALID_SIGN, get_signing_key, 'blabla')
