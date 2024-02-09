## Auth

The AT Protocol has two kinds of authentication: client-server and service-to-service.
This page describes the basics of client-server authentication.

### Login

Login takes a username (handle) and password and returns a session.
Sessions are presented with access and refresh tokens.

Depending on account status and password, the access token permissions are varied.
For example, access tokens created with app-password have limited permissions to create new app-passwords, change email, etc.

The session is created via the [login](#atproto_client.client.client.Client.login) method. 
Under the hood, the SDK uses [create_session](#atproto_client.namespaces.sync_ns.ServerNamespace.create_session) method.

```python
from atproto_client import Client

client = Client()
client.login('username', 'password')
```

The access and refresh tokens are stored in the client object and are used for subsequent requests.
SDK will automatically refresh the access token when it expires. 
So, you don't need to worry about it at all.

It works amazingly well until you don't recreate the client instance many times.
If it's possible, try to keep the client instance alive as long as possible.
For example, instead of starting the script by `cron` every 5 minutes, keep it running and use the `sleep` function.

This is incredibly important because API is rate-limited, and you can reach the limit. 
Which can lead to a temporary outage of your project.

The current rate limits are provided in the [API documentation](https://www.docs.bsky.app/docs/advanced-guides/rate-limits).

- `createSession`:
  - Rate limited by handle
  - 30 requests per 5 minutes (30/5 min)
  - 300 requests per day (300/day)

If you can't keep the client instance alive, for example, a stateless server, you should reuse the created session.
See below how to do it.

### Session string

We have two types of tokens: access and refresh.
The access token is used to authenticate requests to the server.
The refresh token is used to get a new access token when the old one expires.

The access token is valid for ~2 hours, and the refresh token is valid for ~2 months.

SDK will automatically refresh the access token when it expires using [refresh_session](#atproto_client.namespaces.sync_ns.ServerNamespace.refresh_session) method.

You are always able to export the current session to persistent storage and import it later.
To export the session, use the [export_session_string](#atproto_client.client.client.Client.export_session_string) method.

Example how to export the session to a file:
```python
from atproto_client import Client


client = Client()
client.login('username', 'password')

session_string = client.export_session_string()
with open('session.txt', 'w') as f:
    f.write(session_string)
```

To import the session from persistent storage, use the `session_string` argument of the [login](#atproto_client.client.client.Client.login) method.

```python
from atproto_client import Client


client = Client()
with open('session.txt') as f:
    session_string = f.read()
    
client.login(session_string=session_string)
```

:::{warning}
Because of automatic token refreshing, the session string changes every time the access token is refreshed! 
The `export_session_string` method can return different session strings depending on the time of the call. 
This is expected behavior that you should be aware of.
:::

:::{attention}
On the token refresh, the old refresh token will be revoked instantly.
You must use only the fresh pair of tokens (access + refresh).
It's not possible to reuse the same refresh token multiple times.
:::

According to the warnings above, you should always export the session string at the end of the script.
Alternatively, to avoid unhandled errors in your project, or to not deal with the life cycle of your application, 
you can subscribe to the `on_session_changed` event and export the session string from it.

```python
from atproto import Client, SessionEvent, Session


client = Client()

@client.on_session_change
def on_session_change(event: SessionEvent, session: Session):
    print(event, session)
```

For asynchronous code:

```python
from atproto import AsyncClient, SessionEvent, Session


client = AsyncClient()

@client.on_session_change
async def on_session_change(event: SessionEvent, session: Session):
    print(event, session)
```


Possible events are:
- `SessionEvent.CREATE` - when the session is created
- `SessionEvent.REFRESH` - when the session is refreshed
- `SessionEvent.IMPORT` - when the session is imported from a string

CREATE:
```python
# this will trigger the on_session_change with SessionEvent.CREATE event
client.login('username', 'password')
```

IMPORT:
```python
# this will trigger the on_session_change with SessionEvent.IMPORT event
client.login(session_string='exportedSession')
```

REFRESH:
```python
# whenever SDK will refresh the access token, 
# the on_session_change will be triggered 
# with SessionEvent.REFRESH event
```

You should save the session string to a persistent storage, like a file or database, on the `SessionEvent.CREATE` and `SessionEvent.REFRESH` events.

Not a production-ready code, but you can use it as a starting point:

```python
from typing import Optional

from atproto_client import Client, Session, SessionEvent


def get_session() -> Optional[str]:
    try:
        with open('session.txt') as f:
            return f.read()
    except FileNotFoundError:
        return None


def save_session(session_string: str) -> None:
    with open('session.txt', 'w') as f:
        f.write(session_string)


def on_session_change(event: SessionEvent, session: Session) -> None:
    print('Session changed:', event, repr(session))
    if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
        print('Saving changed session')
        save_session(session.export())


def init_client() -> Client:
    client = Client()
    client.on_session_change(on_session_change)

    session_string = get_session()
    if session_string:
        print('Reusing session')
        client.login(session_string=session_string)
    else:
        print('Creating new session')
        client.login('username', 'password')

    return client


if __name__ == '__main__':
    client = init_client()
    # do something with the client
    print('Client is ready to use!')
```

:::{tip}
Don't store the password in the file or database.
The best scenario is to use a password only at the first login.
Later, use the session string to authenticate and store it in a persistent storage.
:::
