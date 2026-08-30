# Authentication

The AT Protocol has two kinds of authentication: client-server and service-to-service. This page covers client-server authentication: logging a client in, and keeping it logged in. For the service-to-service side, where your server verifies a token another service sent it, see [Building a feed generator](feed-generator.md).

## Logging in

[login](#atproto_client.client.client.Client.login) takes a handle and a password and returns a session. Under the hood it calls [create_session](#atproto_client.namespaces.sync_ns.ComAtprotoServerNamespace.create_session).

::::{tab-set}
:::{tab-item} Sync
```python
from atproto import Client

client = Client()
client.login('my-handle.bsky.social', 'my-password')
```
:::
:::{tab-item} Async
```python
from atproto import AsyncClient

client = AsyncClient()
await client.login('my-handle.bsky.social', 'my-password')
```
:::
::::

### Use an app password

Use an [app password](https://bsky.app/settings/app-passwords) rather than your account password. App passwords are scoped: an access token created with one cannot create further app passwords or change your email.

:::{attention}
Direct messages need their own grant. Tick **Allow access to your direct messages** when you create the app password, or every chat call fails with a `Bad token scope` error. See [Direct messages](direct-messages.md).
:::

### Email two-factor authentication

If the account has email 2FA enabled, `create_session` responds with an `AuthFactorTokenRequired` error and the server emails a code. Pass it back as `auth_factor_token`:

```python
client.login('my-handle.bsky.social', 'my-password', auth_factor_token='ABC12-DEF34')
```

The code is single-use. Export the session string afterwards so you do not need a new code on the next run.

### The profile lookup, and non-Bluesky PDSs

`login` returns `ProfileViewDetailed` and also stores it on `client.me`. That lookup is `app.bsky.actor.getProfile`, an AppView method rather than a protocol one, and not every PDS serves it.

The lookup never fails the login. When it does not succeed, `me` is `None` and a warning is emitted. On a PDS without `app.bsky`, pass `fetch_bsky_profile=False` to skip both the request and the warning:

```python
client.login('me.example.com', 'my-password', fetch_bsky_profile=False)
# client.me is None; client.com.atproto.* still works
```

### The client follows your PDS

`create_session` returns the account's DID document. The client reads the PDS endpoint out of it and repoints itself there, so a client constructed against `bsky.social` ends up talking to whichever PDS actually hosts the account. Self-hosted PDSs that do not publish an endpoint keep the URL you constructed the client with.

## Sessions and token refresh

A session holds two tokens. The access token authenticates requests and lasts about two hours; the refresh token buys a new pair and lasts about two months.

The SDK refreshes for you. Before every request it checks the access token's `exp` claim and calls [refresh_session](#atproto_client.namespaces.sync_ns.ComAtprotoServerNamespace.refresh_session) if it expires within the next 15 minutes. The check is guarded by a lock, so concurrent calls refresh once rather than racing.

You never have to think about this, as long as you keep the client instance alive.

:::{warning}
`createSession` is rate limited **by handle**: 30 requests per 5 minutes and 300 per day. A script that constructs a fresh `Client` and logs in on every `cron` tick will exhaust that and take your project down. Keep one client alive and `sleep`, or reuse the session string below.

Current limits are published at [bsky.network/docs/rate-limits](https://bsky.network/docs/rate-limits).
:::

## Reusing a session

If you cannot keep the client alive (a stateless server, a serverless function, a script that runs and exits), export the session and log in with it next time instead of with the password.

[export_session_string](#atproto_client.client.client.Client.export_session_string) returns the handle, DID, both tokens, and the PDS endpoint joined into one opaque string. Pass it back as `login(session_string=...)`.

```{literalinclude} ../../../examples/advanced_usage/session_reuse.py
:language: python
:caption: examples/advanced_usage/session_reuse.py
```

:::{warning}
The session string changes every time the access token is refreshed, so `export_session_string` returns something different depending on when you call it. Always export the **current** string, never a cached one.
:::

:::{attention}
Refreshing revokes the old refresh token instantly. Only the newest pair of tokens is valid. You cannot replay a refresh token.
:::

### Export on change, not at exit

Exporting at the end of the script only works if the script reaches the end. Subscribe to [on_session_change](#atproto_client.client.client.Client.on_session_change) instead and persist the string whenever it changes.

::::{tab-set}
:::{tab-item} Sync
```python
from atproto import Client, Session, SessionEvent

client = Client()


@client.on_session_change
def on_session_change(event: SessionEvent, session: Session) -> None:
    if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
        save_session(session.export())
```
:::
:::{tab-item} Async
```python
from atproto import AsyncClient, Session, SessionEvent

client = AsyncClient()


@client.on_session_change
async def on_session_change(event: SessionEvent, session: Session) -> None:
    if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
        await save_session(session.export())
```
:::
::::

The async client accepts both synchronous and asynchronous callbacks.

:::{warning}
Register a plain function or a coroutine function. A **bound method** or a callable object is accepted without complaint and then never invoked, because the dispatcher only recognises the two function forms. If your callback needs state, close over it rather than hanging it off `self`.
:::

The three events:

`SessionEvent.CREATE`
: `login(handle, password)` created a new session.

`SessionEvent.IMPORT`
: `login(session_string=...)` restored one.

`SessionEvent.REFRESH`
: the SDK swapped an expiring access token for a fresh pair.

Persist on `CREATE` and `REFRESH`. `IMPORT` hands you back what you just loaded.

:::{tip}
Store the session string, not the password. Use the password once, on the first login, and the session string from then on.
:::

## Inspecting the session

[Session](#atproto_client.client.session.Session) is a plain dataclass of five fields: `handle`, `did`, `access_jwt`, `refresh_jwt`, `pds_endpoint`. Two properties decode the tokens without verifying them, which is useful for reading `exp` or `scope`:

```python
session = Session.decode(session_string)
print(session.did, session.pds_endpoint)
print(session.access_jwt_payload.exp)
print(session.refresh_jwt_payload.scope)
```

:::{note}
These decode the payload only. To *verify* a token, which is what a service receiving one must do, use [verify_jwt](#atproto_server.auth.jwt.verify_jwt); see [Building a feed generator](feed-generator.md).
:::

## Logging out

There is no client-side logout. Drop the client instance, delete the stored session string, and call [delete_session](#atproto_client.namespaces.sync_ns.ComAtprotoServerNamespace.delete_session) if you want the server to revoke the tokens too.
