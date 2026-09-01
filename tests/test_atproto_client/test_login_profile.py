"""`login()` authorizes with `com.atproto`; a PDS that does not serve the Bluesky profile lookup must not fail it."""

import base64
import json
import time
import typing as t
import warnings

import pytest
from atproto_client import Client
from atproto_client.client.base import ClientBase
from atproto_client.exceptions import (
    BadRequestError,
    InvokeTimeoutError,
    NetworkError,
    RequestException,
    UnauthorizedError,
)
from atproto_client.models.common import XrpcError
from atproto_client.request import Response


def _jwt() -> str:
    def encode(payload: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')

    return f'{encode({"alg": "HS256"})}.{encode({"exp": int(time.time()) + 3600})}.sig'


_SESSION = {'did': 'did:plc:test', 'handle': 'alice.example.com'}


def _response(status_code: int, error: t.Optional[str] = None) -> Response:
    content = XrpcError(error=error, message=None) if error else None
    return Response(success=False, status_code=status_code, content=content, headers={})


@pytest.fixture
def calls() -> t.List[str]:
    return []


@pytest.fixture
def profile_error(request: pytest.FixtureRequest) -> Exception:
    """What the PDS answers to the profile lookup; 501 unless a test parametrizes it."""
    return getattr(request, 'param', RequestException(_response(501)))


@pytest.fixture
def client(calls: t.List[str], profile_error: Exception, monkeypatch: pytest.MonkeyPatch) -> Client:
    """A client whose PDS serves com.atproto but fails everything else with ``profile_error``."""
    token = _jwt()
    session = {**_SESSION, 'accessJwt': token, 'refreshJwt': token}

    def fake_invoke(self: t.Any, invoke_type: t.Any, **kwargs: t.Any) -> Response:
        nsid = kwargs.get('url', '').rsplit('/', 1)[-1]
        calls.append(nsid)
        if nsid == 'com.atproto.server.createSession':
            return Response(success=True, status_code=200, content=session, headers={})

        raise profile_error

    monkeypatch.setattr(ClientBase, '_invoke', fake_invoke)
    return Client(base_url='https://pds.example.com')


def test_login_succeeds_without_app_bsky(client: Client) -> None:
    with pytest.warns(UserWarning, match='could not fetch the Bluesky profile'):
        assert client.login('alice.example.com', 'pw') is None

    assert client.me is None


def test_session_is_usable_after_a_failed_profile_lookup(client: Client) -> None:
    with pytest.warns(UserWarning):
        client.login('alice.example.com', 'pw')

    assert client._session is not None
    assert client._session.did == 'did:plc:test'


def test_opting_out_skips_the_request_and_the_warning(client: Client, calls: t.List[str]) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        assert client.login('alice.example.com', 'pw', fetch_bsky_profile=False) is None

    assert calls == ['com.atproto.server.createSession']


def test_profile_is_fetched_by_default(client: Client, calls: t.List[str]) -> None:
    with pytest.warns(UserWarning):
        client.login('alice.example.com', 'pw')

    assert calls == ['com.atproto.server.createSession', 'app.bsky.actor.getProfile']


@pytest.mark.parametrize(
    'profile_error',
    [
        pytest.param(RequestException(_response(404)), id='404'),
        pytest.param(RequestException(_response(501, 'MethodNotImplemented')), id='501'),
        pytest.param(BadRequestError(_response(400, 'XRPCNotSupported')), id='XRPCNotSupported'),
    ],
    indirect=True,
)
def test_a_pds_without_the_method_does_not_fail_the_login(client: Client) -> None:
    with pytest.warns(UserWarning):
        client.login('alice.example.com', 'pw')

    assert client.me is None


@pytest.mark.parametrize(
    'profile_error',
    [
        pytest.param(UnauthorizedError(_response(401, 'ExpiredToken')), id='unauthorized'),
        pytest.param(RequestException(_response(500, 'InternalServerError')), id='server_error'),
        pytest.param(NetworkError(), id='network'),
        pytest.param(InvokeTimeoutError(), id='timeout'),
    ],
    indirect=True,
)
def test_any_other_failure_of_the_lookup_propagates(client: Client, profile_error: Exception) -> None:
    """A dead session surfaces here, as it did before the lookup became optional."""
    with pytest.raises(type(profile_error)):
        client.login('alice.example.com', 'pw')
