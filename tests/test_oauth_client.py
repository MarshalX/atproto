"""Tests for OAuth client implementation."""

import typing as t
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from atproto_oauth import OAuthClient, OAuthState, PromptType
from atproto_oauth.stores.memory import MemorySessionStore, MemoryStateStore


@pytest.fixture
def oauth_client() -> OAuthClient:
    """Create an OAuth client for testing."""
    return OAuthClient(
        client_id='https://example.com/client-metadata.json',
        redirect_uri='https://example.com/callback',
        scope='atproto',
        state_store=MemoryStateStore(),
        session_store=MemorySessionStore(),
    )


def test_prompt_type_values() -> None:
    """Test that PromptType includes all valid values."""
    valid_prompts: list[PromptType] = ['login', 'select_account', 'consent', 'none']
    assert len(valid_prompts) == 4


def test_prompt_type_is_exported() -> None:
    """Test that PromptType is exported from the package."""
    from atproto_oauth import PromptType as ImportedPromptType

    assert ImportedPromptType is PromptType


@pytest.mark.asyncio
@pytest.mark.parametrize('prompt', ['login', 'select_account', 'consent', 'none', None])
async def test_prompt_passed_to_par_request(oauth_client: OAuthClient, prompt: t.Optional[str]) -> None:
    """Test that prompt parameter flows through to _send_par_request."""
    oauth_client._id_resolver.handle.resolve = AsyncMock(return_value='did:plc:test123')
    oauth_client._id_resolver.did.resolve_atproto_data = AsyncMock(
        return_value=MagicMock(handle='test.bsky.social', pds='https://pds.example.com')
    )

    captured_prompt: t.Optional[str] = None

    async def mock_send_par(
        authserver_meta: t.Any,
        login_hint: str,
        pkce_challenge: str,
        dpop_key: t.Any,
        state: str,
        prompt: t.Optional[str] = None,
    ) -> tuple[str, str]:
        nonlocal captured_prompt
        captured_prompt = prompt
        return 'urn:ietf:params:oauth:request_uri:test', 'nonce123'

    oauth_client._send_par_request = mock_send_par  # type: ignore[method-assign]

    with (
        patch(
            'atproto_oauth.client.discover_authserver_from_pds_async',
            new=AsyncMock(return_value='https://auth.example.com'),
        ),
        patch(
            'atproto_oauth.client.fetch_authserver_metadata_async',
            new=AsyncMock(
                return_value=MagicMock(
                    issuer='https://auth.example.com',
                    authorization_endpoint='https://auth.example.com/authorize',
                    pushed_authorization_request_endpoint='https://auth.example.com/par',
                )
            ),
        ),
    ):
        await oauth_client.start_authorization('test.bsky.social', prompt=prompt)
        assert captured_prompt == prompt


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('prompt', 'expect_in_params'),
    [
        ('login', True),
        ('select_account', True),
        ('consent', True),
        ('none', True),
        (None, False),
    ],
)
async def test_prompt_in_par_params(
    oauth_client: OAuthClient,
    prompt: t.Optional[str],
    expect_in_params: bool,
) -> None:
    """Test that prompt is included in PAR params only when provided."""
    authserver_meta = MagicMock(
        issuer='https://auth.example.com',
        pushed_authorization_request_endpoint='https://auth.example.com/par',
    )

    captured_params: dict[str, str] = {}

    async def mock_make_token_request(
        token_url: str,
        params: dict[str, str],
        dpop_key: t.Any,
        dpop_nonce: str,
        issuer: t.Optional[str] = None,
    ) -> tuple[str, MagicMock]:
        nonlocal captured_params
        captured_params = params.copy()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {'request_uri': 'urn:test:uri'}
        return 'nonce', response

    oauth_client._make_token_request = mock_make_token_request  # type: ignore[method-assign]

    await oauth_client._send_par_request(
        authserver_meta=authserver_meta,
        login_hint='test.bsky.social',
        pkce_challenge='challenge123',
        dpop_key=MagicMock(),
        state='state123',
        prompt=prompt,
    )

    if expect_in_params:
        assert 'prompt' in captured_params
        assert captured_params['prompt'] == prompt
    else:
        assert 'prompt' not in captured_params


@pytest.mark.asyncio
async def test_handle_callback_sets_expires_at(oauth_client: OAuthClient) -> None:
    """Test that handle_callback computes expires_at from expires_in."""
    from cryptography.hazmat.primitives.asymmetric import ec

    dpop_key = ec.generate_private_key(ec.SECP256R1())

    # Store a state so handle_callback can find it
    state = OAuthState(
        state='test-state',
        pkce_verifier='verifier123',
        redirect_uri='https://example.com/callback',
        scope='atproto',
        authserver_iss='https://auth.example.com',
        dpop_private_key=dpop_key,
        dpop_authserver_nonce='nonce',
        did='did:plc:test123',
        handle='test.bsky.social',
        pds_url='https://pds.example.com',
    )
    await oauth_client.state_store.save_state(state)

    token_response_data = {
        'access_token': 'access-token-123',
        'token_type': 'DPoP',
        'scope': 'atproto',
        'sub': 'did:plc:test123',
        'refresh_token': 'refresh-token-123',
        'expires_in': 3600,
    }

    async def mock_make_token_request(
        token_url: str, params: dict, dpop_key: t.Any, dpop_nonce: str, issuer: t.Optional[str] = None
    ) -> tuple[str, MagicMock]:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = token_response_data
        return 'nonce-updated', response

    oauth_client._make_token_request = mock_make_token_request  # type: ignore[method-assign]

    # Mock the identity resolver for re-verification step
    mock_atproto_data = MagicMock(pds='https://pds.example.com')
    oauth_client._id_resolver.did.resolve_atproto_data = AsyncMock(return_value=mock_atproto_data)

    with (
        patch(
            'atproto_oauth.client.fetch_authserver_metadata_async',
            new=AsyncMock(
                return_value=MagicMock(
                    issuer='https://auth.example.com',
                    token_endpoint='https://auth.example.com/token',
                )
            ),
        ),
        patch(
            'atproto_oauth.client.discover_authserver_from_pds_async',
            new=AsyncMock(return_value='https://auth.example.com'),
        ),
    ):
        before = datetime.now(timezone.utc)
        session = await oauth_client.handle_callback(
            code='auth-code-123', state='test-state', iss='https://auth.example.com'
        )
        after = datetime.now(timezone.utc)

    assert session.expires_at is not None
    expected_min = before + timedelta(seconds=3600)
    expected_max = after + timedelta(seconds=3600)
    assert expected_min <= session.expires_at <= expected_max


@pytest.mark.asyncio
async def test_handle_callback_no_expires_in(oauth_client: OAuthClient) -> None:
    """Test that expires_at is None when server omits expires_in."""
    from cryptography.hazmat.primitives.asymmetric import ec

    dpop_key = ec.generate_private_key(ec.SECP256R1())

    state = OAuthState(
        state='test-state-2',
        pkce_verifier='verifier123',
        redirect_uri='https://example.com/callback',
        scope='atproto',
        authserver_iss='https://auth.example.com',
        dpop_private_key=dpop_key,
        dpop_authserver_nonce='nonce',
        did='did:plc:test123',
        handle='test.bsky.social',
        pds_url='https://pds.example.com',
    )
    await oauth_client.state_store.save_state(state)

    token_response_data = {
        'access_token': 'access-token-456',
        'token_type': 'DPoP',
        'scope': 'atproto',
        'sub': 'did:plc:test123',
    }

    async def mock_make_token_request(
        token_url: str, params: dict, dpop_key: t.Any, dpop_nonce: str, issuer: t.Optional[str] = None
    ) -> tuple[str, MagicMock]:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = token_response_data
        return 'nonce-updated', response

    oauth_client._make_token_request = mock_make_token_request  # type: ignore[method-assign]

    # Mock the identity resolver for re-verification step
    mock_atproto_data = MagicMock(pds='https://pds.example.com')
    oauth_client._id_resolver.did.resolve_atproto_data = AsyncMock(return_value=mock_atproto_data)

    with (
        patch(
            'atproto_oauth.client.fetch_authserver_metadata_async',
            new=AsyncMock(
                return_value=MagicMock(
                    issuer='https://auth.example.com',
                    token_endpoint='https://auth.example.com/token',
                )
            ),
        ),
        patch(
            'atproto_oauth.client.discover_authserver_from_pds_async',
            new=AsyncMock(return_value='https://auth.example.com'),
        ),
    ):
        session = await oauth_client.handle_callback(
            code='auth-code-456', state='test-state-2', iss='https://auth.example.com'
        )

    assert session.expires_at is None
