"""Tests for OAuth client implementation."""

import typing as t
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from atproto_oauth import OAuthClient, PromptType
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
