# ATProto OAuth Flask Demo

simple flask application demonstrating OAuth authentication using the `atproto_oauth` package.

## features

- complete OAuth 2.1 authorization code flow
- PKCE and DPoP support
- localhost testing (no HTTPS required)
- authenticated API requests

## quick start

1. install dependencies:
```bash
uv sync
```

2. run the demo:
```bash
uv run python examples/oauth_flask_demo/app.py
```

3. visit http://127.0.0.1:5000

4. enter your bluesky handle (e.g., `user.bsky.social`)

5. authorize the app on bluesky

6. you'll be redirected back to see your profile info

## how it works

### 1. start authorization
```python
oauth_client = OAuthClient(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    scope='atproto',
    state_store=MemoryStateStore(),
    session_store=MemorySessionStore(),
)

auth_url, state = await oauth_client.start_authorization(handle)
```

### 2. handle callback
```python
oauth_session = await oauth_client.handle_callback(code, state, iss)
```

### 3. make authenticated requests
```python
response = await oauth_client.make_authenticated_request(
    session=oauth_session,
    method='GET',
    url=f'{pds_url}/xrpc/com.atproto.repo.describeRepo?repo={did}',
)
```

## production considerations

this is a **development demo** only. for production:

### use persistent stores
```python
# instead of memory stores
from your_app.stores import DatabaseStateStore, DatabaseSessionStore

oauth_client = OAuthClient(
    state_store=DatabaseStateStore(),
    session_store=DatabaseSessionStore(),
    ...
)
```

### use HTTPS
- deploy with proper TLS certificate
- update client_id to your public HTTPS URL
- create client metadata JSON file

### security
- use strong secret keys
- implement CSRF protection
- validate all inputs
- handle errors gracefully
- log security events

### client metadata
for production (non-localhost), create `/oauth-client-metadata.json`:

```json
{
  "client_id": "https://yourapp.com/oauth-client-metadata.json",
  "dpop_bound_access_tokens": true,
  "application_type": "web",
  "redirect_uris": ["https://yourapp.com/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "scope": "atproto",
  "token_endpoint_auth_method": "private_key_jwt",
  "token_endpoint_auth_signing_alg": "ES256",
  "jwks_uri": "https://yourapp.com/oauth/jwks.json",
  "client_name": "Your App Name",
  "client_uri": "https://yourapp.com"
}
```

### confidential client
for server-side apps, generate a client secret key:

```python
from atproto_oauth.dpop import DPoPManager

# generate once and store securely
client_secret_key = DPoPManager.generate_keypair()

oauth_client = OAuthClient(
    ...,
    client_secret_key=client_secret_key,
)
```

## troubleshooting

### "Invalid state parameter"
- state expired (default TTL: 10 minutes)
- user refreshed callback page
- solution: restart authorization flow

### "DID mismatch in token"
- identity changed during authorization
- solution: retry with fresh authorization

### "PDS request failed"
- token expired
- solution: implement automatic token refresh

## references

- [ATProto OAuth Spec](https://atproto.com/specs/oauth)
- [Bluesky OAuth Cookbook](https://github.com/bluesky-social/cookbook/tree/main/python-oauth-web-app)
- [atproto Python SDK](https://github.com/MarshalX/atproto)
