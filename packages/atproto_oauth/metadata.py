"""Authorization server metadata discovery."""

import httpx

from atproto_oauth.exceptions import UnsupportedAuthServerError
from atproto_oauth.models import AuthServerMetadata
from atproto_oauth.security import is_safe_url, validate_authserver_metadata


async def discover_authserver_from_pds_async(pds_url: str, timeout: float = 5.0) -> str:
    """Discover authorization server URL from PDS.

    Args:
        pds_url: PDS endpoint URL.
        timeout: Request timeout in seconds.

    Returns:
        Authorization server URL.

    Raises:
        ValueError: If PDS URL is unsafe or response is invalid.
        httpx.HTTPError: If request fails.
    """
    if not is_safe_url(pds_url):
        raise ValueError(f'Unsafe PDS URL: {pds_url}')

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(f'{pds_url}/.well-known/oauth-protected-resource')
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError(f'PDS returned non-200 status: {response.status_code}')

        data = response.json()
        if not isinstance(data, dict) or 'authorization_servers' not in data:
            raise ValueError('Invalid oauth-protected-resource response')

        auth_servers = data['authorization_servers']
        if not auth_servers or not isinstance(auth_servers, list):
            raise ValueError('No authorization servers found')

        return auth_servers[0]


def discover_authserver_from_pds(pds_url: str, timeout: float = 5.0) -> str:
    """Discover authorization server URL from PDS (synchronous).

    Args:
        pds_url: PDS endpoint URL.
        timeout: Request timeout in seconds.

    Returns:
        Authorization server URL.
    """
    if not is_safe_url(pds_url):
        raise ValueError(f'Unsafe PDS URL: {pds_url}')

    with httpx.Client(timeout=timeout) as client:
        response = client.get(f'{pds_url}/.well-known/oauth-protected-resource')
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError(f'PDS returned non-200 status: {response.status_code}')

        data = response.json()
        if not isinstance(data, dict) or 'authorization_servers' not in data:
            raise ValueError('Invalid oauth-protected-resource response')

        auth_servers = data['authorization_servers']
        if not auth_servers or not isinstance(auth_servers, list):
            raise ValueError('No authorization servers found')

        return auth_servers[0]


async def fetch_authserver_metadata_async(authserver_url: str, timeout: float = 5.0) -> AuthServerMetadata:
    """Fetch and validate authorization server metadata.

    Args:
        authserver_url: Authorization server URL.
        timeout: Request timeout in seconds.

    Returns:
        Validated metadata object.

    Raises:
        ValueError: If URL is unsafe.
        UnsupportedAuthServerError: If metadata doesn't meet requirements.
        httpx.HTTPError: If request fails.
    """
    if not is_safe_url(authserver_url):
        raise ValueError(f'Unsafe authorization server URL: {authserver_url}')

    fetch_url = f'{authserver_url}/.well-known/oauth-authorization-server'

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(fetch_url)
        response.raise_for_status()

        metadata_dict = response.json()

        # Validate against ATProto requirements
        try:
            validate_authserver_metadata(metadata_dict, fetch_url)
        except ValueError as e:
            raise UnsupportedAuthServerError(str(e)) from e

        # Parse into model
        return AuthServerMetadata(
            issuer=metadata_dict['issuer'],
            authorization_endpoint=metadata_dict['authorization_endpoint'],
            token_endpoint=metadata_dict['token_endpoint'],
            pushed_authorization_request_endpoint=metadata_dict['pushed_authorization_request_endpoint'],
            response_types_supported=metadata_dict['response_types_supported'],
            grant_types_supported=metadata_dict['grant_types_supported'],
            code_challenge_methods_supported=metadata_dict['code_challenge_methods_supported'],
            token_endpoint_auth_methods_supported=metadata_dict['token_endpoint_auth_methods_supported'],
            token_endpoint_auth_signing_alg_values_supported=metadata_dict[
                'token_endpoint_auth_signing_alg_values_supported'
            ],
            scopes_supported=metadata_dict['scopes_supported'],
            dpop_signing_alg_values_supported=metadata_dict['dpop_signing_alg_values_supported'],
            authorization_response_iss_parameter_supported=metadata_dict[
                'authorization_response_iss_parameter_supported'
            ],
            require_pushed_authorization_requests=metadata_dict['require_pushed_authorization_requests'],
            client_id_metadata_document_supported=metadata_dict['client_id_metadata_document_supported'],
            revocation_endpoint=metadata_dict.get('revocation_endpoint'),
            jwks_uri=metadata_dict.get('jwks_uri'),
            require_request_uri_registration=metadata_dict.get('require_request_uri_registration'),
        )


def fetch_authserver_metadata(authserver_url: str, timeout: float = 5.0) -> AuthServerMetadata:
    """Fetch and validate authorization server metadata (synchronous).

    Args:
        authserver_url: Authorization server URL.
        timeout: Request timeout in seconds.

    Returns:
        Validated metadata object.
    """
    if not is_safe_url(authserver_url):
        raise ValueError(f'Unsafe authorization server URL: {authserver_url}')

    fetch_url = f'{authserver_url}/.well-known/oauth-authorization-server'

    with httpx.Client(timeout=timeout) as client:
        response = client.get(fetch_url)
        response.raise_for_status()

        metadata_dict = response.json()

        # Validate against ATProto requirements
        try:
            validate_authserver_metadata(metadata_dict, fetch_url)
        except ValueError as e:
            raise UnsupportedAuthServerError(str(e)) from e

        # Parse into model
        return AuthServerMetadata(
            issuer=metadata_dict['issuer'],
            authorization_endpoint=metadata_dict['authorization_endpoint'],
            token_endpoint=metadata_dict['token_endpoint'],
            pushed_authorization_request_endpoint=metadata_dict['pushed_authorization_request_endpoint'],
            response_types_supported=metadata_dict['response_types_supported'],
            grant_types_supported=metadata_dict['grant_types_supported'],
            code_challenge_methods_supported=metadata_dict['code_challenge_methods_supported'],
            token_endpoint_auth_methods_supported=metadata_dict['token_endpoint_auth_methods_supported'],
            token_endpoint_auth_signing_alg_values_supported=metadata_dict[
                'token_endpoint_auth_signing_alg_values_supported'
            ],
            scopes_supported=metadata_dict['scopes_supported'],
            dpop_signing_alg_values_supported=metadata_dict['dpop_signing_alg_values_supported'],
            authorization_response_iss_parameter_supported=metadata_dict[
                'authorization_response_iss_parameter_supported'
            ],
            require_pushed_authorization_requests=metadata_dict['require_pushed_authorization_requests'],
            client_id_metadata_document_supported=metadata_dict['client_id_metadata_document_supported'],
            revocation_endpoint=metadata_dict.get('revocation_endpoint'),
            jwks_uri=metadata_dict.get('jwks_uri'),
            require_request_uri_registration=metadata_dict.get('require_request_uri_registration'),
        )
