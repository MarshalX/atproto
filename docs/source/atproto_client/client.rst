Client
======

:obj:`~atproto_client.client.client.Client` is the entry point to the SDK. It wraps the XRPC endpoints of a PDS in methods
that take and return models, and it keeps the session for you: log in once and every later call
carries the credentials, refreshing them when they expire.

Sync and async
--------------

Every method exists in two clients with the same names, arguments and return types. Pick the one
that matches the program you are writing:

- :obj:`~atproto_client.client.client.Client` runs each call to completion before returning. Use it in scripts, one-off tasks
  and anything already written in blocking style.
- :obj:`~atproto_client.client.async_client.AsyncClient` returns coroutines, so calls have to be awaited. Use it inside an event
  loop, and whenever you want many requests in flight at once.

Switching between them is an import, an ``await`` and nothing else:

..  code-block:: python

    from atproto import Client

    client = Client()
    profile = client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)

..  code-block:: python

    import asyncio

    from atproto import AsyncClient


    async def main() -> None:
        client = AsyncClient()
        profile = await client.login('my-handle', 'my-password')
        print('Welcome,', profile.display_name)


    asyncio.run(main())

Both clients talk to ``https://bsky.social`` unless you pass another PDS as the first argument,
and both expose the generated lexicon namespaces directly, so anything missing from the
high-level methods is still reachable: ``client.app.bsky.feed.get_timeline(...)``.

Client
------

.. automodule:: atproto_client.client.client
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

AsyncClient
-----------

The method list is not repeated here: every method above exists on
:obj:`~atproto_client.client.async_client.AsyncClient` under the same name, with the same
arguments and the same return type, and returns a coroutine.

.. autoclass:: atproto_client.client.async_client.AsyncClient
   :no-members:

Session
-------

A session is what :obj:`~atproto_client.client.client.Client.login` returns you in exchange for
credentials, and what every later call authenticates with. Export it with
:obj:`~atproto_client.client.client.Client.export_session_string`, keep it somewhere durable, and
hand it back to :obj:`~atproto_client.client.client.Client.login` instead of the password.

The client refreshes the session on its own, so a stored string goes stale. Subscribe to the
change event and write the new one out each time:

..  code-block:: python

    from atproto import Client, Session, SessionEvent


    client = Client()


    @client.on_session_change
    def on_session_change(event: SessionEvent, session: Session) -> None:
        if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
            save_somewhere(session.export())

.. autoclass:: atproto_client.client.session.Session
   :members:
   :undoc-members:

.. autoclass:: atproto_client.client.session.SessionEvent
   :members:
   :undoc-members:
