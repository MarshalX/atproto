import pytest
from atproto_server.auth.jwt import get_jwt_payload, parse_jwt, validate_jwt_payload
from atproto_server.exceptions import TokenDecodeError, TokenExpiredSignatureError

# expired token
_TEST_JWT = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJpc3MiOiJkaWQ6cGxjOmt2d3ZjbjVpcWZvb29wbXl6dmI0cXpiYSIsImF1ZCI6ImRpZDp3ZWI6ZmVlZC5hdHByb3RvLmJsdWUiLCJleHAiOjE3MDQ4NDExMzh9.50SlT6vw26HsDXVDM4D2D53_Dvzd6bjp3TDc5EyDVD4ob9i3EEB7fmaKE0XR4egMS9Kf9eMdVqH5gJNCaIah4Q'  # noqa: E501


def test_parse_jwt_empty() -> None:
    with pytest.raises(TokenDecodeError):
        parse_jwt('')


def test_parse_jwt() -> None:
    payload, signing_input, header, signature = parse_jwt(_TEST_JWT)

    assert header['typ'] == 'JWT'
    assert header['alg'] == 'ES256K'

    assert payload
    assert signing_input
    assert len(signature) == 64


def test_get_jwt_payload() -> None:
    payload = get_jwt_payload(_TEST_JWT)
    assert payload.iss == 'did:plc:kvwvcn5iqfooopmyzvb4qzba'
    assert payload.aud == 'did:web:feed.atproto.blue'
    assert payload.exp == 1704841138


def test_validate_jwt_payload_expired() -> None:
    payload = get_jwt_payload(_TEST_JWT)
    with pytest.raises(TokenExpiredSignatureError):
        validate_jwt_payload(payload)
