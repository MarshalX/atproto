"""`login()` authorizes with `com.atproto`; the Bluesky profile lookup must never fail it."""

import base64
import json
import time
import typing as t
import warnings

import pytest
from atproto_client import Client
from atproto_client.client.base import ClientBase
from atproto_client.exceptions import RequestException
from atproto_client.request import Response


def _jwt() -> str:
    def encode(payload: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')

    return f'{encode({"alg": "HS256"})}.{encode({"exp": int(time.time()) + 3600})}.sig'


_SESSION = {'did': 'did:plc:test', 'handle': 'alice.example.com'}


@pytest.fixture
def calls() -> t.List[str]:
    return []


@pytest.fixture
def client(calls: t.List[str], monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> Client:
    """A client whose PDS serves com.atproto but answers 501 for everything else."""
    token = _jwt()
    session = {**_SESSION, 'accessJwt': token, 'refreshJwt': token}

    def fake_invoke(self: t.Any, invoke_type: t.Any, **kwargs: t.Any) -> Response:
        nsid = kwargs.get('url', '').rsplit('/', 1)[-1]
        calls.append(nsid)
        if nsid == 'com.atproto.server.createSession':
            return Response(success=True, status_code=200, content=session, headers={})

        raise RequestException(Response(success=False, status_code=501, content=None, headers={}))

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
