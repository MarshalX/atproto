# OAuth

OAuth lets a user authorize your application without giving it a password. The user signs in on their own server, approves a list of permissions, and your application receives tokens that are bound to a key only it holds. App passwords are the older mechanism, described in [Authentication](authentication.md).

The rules are the protocol's, not this SDK's. See [atproto.com/specs/oauth](https://atproto.com/specs/oauth) and, for scopes, [atproto.com/specs/permission](https://atproto.com/specs/permission).

## The shape of it

Two objects do the work:

- An [OAuthClient](#atproto_oauth.OAuthClient) represents your application. It starts authorizations, completes them, and stores the resulting sessions.
- An [OAuthSession](#atproto_oauth.OAuthSession) represents one account that authorized your application. You pass it to [login_oauth](#atproto_client.client.client.Client.login_oauth), and from then on the client behaves as usual.

Every flow has the same three steps. You send the user to the URL `authorize` returns, they come back to your redirect URI with query parameters, and `callback` turns those into a session:

```python
url = oauth_client.authorize('alice.bsky.social')
result = oauth_client.callback(query_params)
client.login_oauth(result.session)
```

The session signs every request and refreshes its tokens on its own. Nothing else about [Client](#atproto_client.client.client.Client) changes: namespaces, `send_post`, `clone()` and proxies all work.

## Pick a kind of client

There is no registration. A client is identified by a URL that serves its metadata, and the three constructors differ in where that metadata comes from.

| Constructor | For | Needs |
|---|---|---|
| [loopback](#atproto_oauth.OAuthClient.loopback) | command line tools, development | nothing |
| [public](#atproto_oauth.OAuthClient.public) | applications that cannot keep a secret | the metadata hosted at an HTTPS URL |
| [confidential](#atproto_oauth.OAuthClient.confidential) | web services | hosted metadata and a signing key |

Authorization servers give confidential clients longer sessions, because a compromised key can be withdrawn.

### A command line tool

A loopback client uses `http://localhost` as its client ID and receives the redirect on a port of the local machine. [login_with_browser](#atproto_oauth.OAuthClient.login_with_browser) does the three steps for you: it listens on a free port, opens the browser, waits for the user and returns the session.

```python
from atproto import Client, OAuthClient, models

oauth_client = OAuthClient.loopback(scope=f'atproto repo:{models.ids.AppBskyFeedPost}?action=create')
session = oauth_client.login_with_browser('alice.bsky.social')

client = Client()
client.login_oauth(session)
```

The full example also keeps the session in a file, so the browser is needed only once:

```{literalinclude} ../../../examples/oauth/loopback_cli.py
:language: python
:caption: examples/oauth/loopback_cli.py
```

The browser ends on a short page that says whether the authorization went through. Pass `page` to show your own. It receives the query parameters of the redirect and returns HTML:

```python
def page(params):
    if 'error' in params:
        return '<h1>Login was cancelled</h1>'

    return '<h1>Logged in. You can close this tab.</h1>'


session = oauth_client.login_with_browser('alice.bsky.social', page=page)
```

The parameters come from the network. Escape any of them you put into the page, for example with `html.escape`.

If you need more control, such as your own waiting loop or user interface, run the steps yourself with [LoopbackCallbackServer](#atproto_oauth.LoopbackCallbackServer). This is what `login_with_browser` does:

```python
from atproto import LoopbackCallbackServer

with LoopbackCallbackServer(oauth_client.client_metadata['redirect_uris']) as server:
    url = oauth_client.authorize('alice.bsky.social', redirect_uri=server.redirect_uri)
    print(url)

    session = oauth_client.callback(server.wait(timeout=300)).session
```

### A web service

Publish the metadata and the public keys at the URLs you declared, and wire two routes: one that starts the authorization and one that receives the callback. The sketch below uses Flask; the SDK does not depend on it.

```python
import json
import os
import secrets

from atproto import Client, OAuthClient, models
from atproto.exceptions import OAuthCallbackError
from flask import Flask, jsonify, redirect, request, session

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']

oauth_client = OAuthClient.confidential(
    client_id='https://app.example.com/oauth-client-metadata.json',
    redirect_uri='https://app.example.com/oauth/callback',
    scope=f'atproto repo:{models.ids.AppBskyFeedPost}?action=create',
    keys=[json.loads(os.environ['OAUTH_PRIVATE_JWK'])],
    metadata={'client_name': 'Example', 'jwks_uri': 'https://app.example.com/oauth/jwks.json'},
    state_store=state_store,  # your database, see "Storing sessions"
    session_store=session_store,
)


@app.get('/oauth-client-metadata.json')
def client_metadata():
    return jsonify(oauth_client.client_metadata)


@app.get('/oauth/jwks.json')
def jwks():
    return jsonify(oauth_client.jwks)


@app.post('/login')
def login():
    session['oauth_state'] = secrets.token_urlsafe()
    return redirect(oauth_client.authorize(request.form['handle'], state=session['oauth_state']))


@app.get('/oauth/callback')
def callback():
    try:
        result = oauth_client.callback(request.args.to_dict())
    except OAuthCallbackError:
        return 'Login failed', 400

    # the login must finish in the browser that started it
    expected_state = session.pop('oauth_state', None)
    if not expected_state or not result.state or not secrets.compare_digest(result.state, expected_state):
        result.session.revoke()
        return 'Login failed', 400

    session['did'] = result.session.did
    return redirect('/')


@app.post('/post')
def post():
    client = Client()
    client.login_oauth(oauth_client.restore(session['did']))
    client.send_post(request.form['text'])
    return redirect('/')
```

The message of a callback error can carry text from the query string, so the sketch does not echo it into the page. The `state` check matters. Without it, an attacker can start a login with their own account and hand the callback URL to someone else, whose browser would then be signed in as the attacker.

Generate the key once with [generate_p256_jwk](#atproto_crypto.jwk.generate_p256_jwk) and keep it secret:

```python
import json

from atproto_crypto.jwk import generate_p256_jwk

print(json.dumps(generate_p256_jwk(kid='key-1')))
```

To rotate, put the new key first in `keys` and keep the old one after it. New sessions use the first key; a session keeps the key it started with, which the specification requires. Remove the old key once the sessions that used it are gone.

### Async

[AsyncOAuthClient](#atproto_oauth.AsyncOAuthClient) has the same methods as coroutines and produces an [AsyncOAuthSession](#atproto_oauth.AsyncOAuthSession) for [AsyncClient](#atproto_client.client.async_client.AsyncClient). Its stores and callbacks may be synchronous or asynchronous.

```python
from atproto import AsyncClient, AsyncOAuthClient

oauth_client = AsyncOAuthClient.loopback()
session = await oauth_client.restore('did:plc:kvwvcn5iqfooopmyzvb4qzba')

client = AsyncClient()
await client.login_oauth(session)
```

A session works only with the client of its kind. Using an `OAuthSession` with `AsyncClient` raises an error on the first request.

## Scopes

A scope is the list of permissions your application asks for. `atproto` is mandatory. The rest should be as narrow as the application allows:

```python
scope = f'atproto repo:{models.ids.AppBskyFeedPost}?action=create blob:image/*'
```

A lexicon can bundle permissions into a permission set, which is requested by its NSID. Those of the bundled lexicons are in `models.ids`:

```python
from atproto import models
from atproto_oauth.scopes import IncludeScope

full_app = IncludeScope(models.ids.AppBskyAuthFullApp, aud='did:web:api.bsky.app#bsky_appview')
scope = f'atproto {full_app}'
```

`transition:generic` grants roughly what an app password does. The protocol marks it as transitional; prefer granular permissions in new applications.

The user may approve less than you asked for. Check what was granted instead of assuming:

```python
if session.permissions.allows_repo(collection=models.ids.AppBskyFeedPost, action='create'):
    ...
```

[permissions](#atproto_oauth.OAuthSession.permissions) understands both granular permissions and the transitional scopes.

[login_oauth](#atproto_client.client.client.Client.login_oauth) does not fetch the profile of the account, because a narrow scope does not cover `app.bsky.actor.getProfile`. Pass `fetch_bsky_profile=True` if yours does. Without a profile, `client.me` is `None`; methods such as `send_post` use the DID of the session.

## Storing sessions

A session holds tokens and a private key, and it changes every time the tokens are refreshed. The OAuth client writes it to a store, keyed by DID, on every change. By default that store is in memory, so sessions are lost when the process exits.

A store is any object with `get`, `set` and `delete`:

```python
import json

from atproto import OAuthSessionData


class RedisSessionStore:
    def __init__(self, redis):
        self._redis = redis

    def get(self, key):
        value = self._redis.get(f'oauth-session:{key}')
        return OAuthSessionData.from_dict(json.loads(value)) if value else None

    def set(self, key, value):
        self._redis.set(f'oauth-session:{key}', json.dumps(value.to_dict()))

    def delete(self, key):
        self._redis.delete(f'oauth-session:{key}')
```

There are two stores. `session_store` holds sessions. `state_store` holds authorization requests between `authorize` and `callback`; a web service running more than one process needs a shared one, with [OAuthStateData](#atproto_oauth.OAuthStateData) in place of `OAuthSessionData`.

For a script used by one person, [JsonFileStore](#atproto_oauth.JsonFileStore) keeps sessions in a file.

:::{warning}
Treat a stored session like a password. Anyone who reads it can act as the account until the session is revoked.
:::

To get a session back later, ask the OAuth client for it by DID:

```python
session = oauth_client.restore('did:plc:kvwvcn5iqfooopmyzvb4qzba')
```

A handle works too and is resolved to a DID first, which suits a script. A web service should restore by the DID it stored at login, because a handle can move to another account.

`on_session_updated` and `on_session_deleted` tell you when a session changed or went away, for example because the user revoked it from their account settings. They run while the OAuth client holds the lock of that account, so they must not call the OAuth client for the same account. An exception raised by one propagates to the caller.

## Token refresh

You do not refresh tokens yourself. The session refreshes them shortly before they expire, and again if the server rejects one, then repeats the request.

Refresh tokens are single-use, so two refreshes at the same time would destroy the session. Within one OAuth client this cannot happen. If several processes share a session store, pass `lock`, a function that returns a lock for a DID that all of them respect:

```python
oauth_client = OAuthClient.confidential(..., lock=lambda did: redis.lock(f'oauth-refresh:{did}'))
```

When a session can no longer be refreshed, it is deleted from the store and `on_session_deleted` is called. From then on [restore](#atproto_oauth.OAuthClient.restore) and requests through a client that still holds the session raise [TokenRefreshError](#atproto_oauth.exceptions.TokenRefreshError). The request during which the PDS rejected the tokens fails with [UnauthorizedError](#atproto_client.exceptions.UnauthorizedError). Either way, send the user through `authorize` again.

## Logging out

```python
session.revoke()
```

This revokes the tokens on the server and deletes the session from the store. [logout_oauth](#atproto_client.client.client.Client.logout_oauth) only detaches the session from a client.

## What differs from password login

- [on_session_change](#atproto_client.client.methods_mixin.session.SessionDispatchMixin.on_session_change) is not called. Use the callbacks of the OAuth client.
- [export_session_string](#atproto_client.client.methods_mixin.session.SessionMethodsMixin.export_session_string) raises. The session lives in the session store.
- Requests go to the PDS of the account, and follow it if the account moves.

## Security notes

The handle, the PDS and the authorization server of an account are all chosen by whoever is logging in, so a service that logs users in requests URLs it does not control. The OAuth client accepts a handle, a `did:plc`, a `did:web` that names a host, or the `https://` URL of a PDS, and nothing else. It refuses anything but HTTPS URLs of public hosts and does not follow redirects.

:::{warning}
A hostname that resolves to a private address is not detected. If your service can reach internal systems, also restrict its outbound network access.
:::

In a web application, bind every login to the browser that started it with `state`, as the example above does.

`allow_http=True` relaxes these checks for a local development environment. Do not use it in production.
