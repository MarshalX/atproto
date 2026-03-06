OAuth (authentication)
======================

The AT Protocol uses `OAuth 2.1 <https://atproto.com/specs/oauth>`_ for user authentication. OAuth replaces the older App Password flow and is the recommended way to authenticate users in new applications.

OAuth on AT Protocol uses several security mechanisms together: Pushed Authorization Requests (PAR), Proof Key for Code Exchange (PKCE), and Demonstrating Proof-of-Possession (DPoP). The ``atproto_oauth`` package handles all of these automatically.

Quick start
-----------

1. Register your app by hosting a ``client-metadata.json`` file at a public URL. See the `client metadata spec <https://atproto.com/specs/oauth#clients>`_ for the required fields.

2. Create an ``OAuthClient`` and start the authorization flow:

..  code-block:: python

    from atproto_oauth import OAuthClient
    from atproto_oauth.stores.memory import MemoryStateStore, MemorySessionStore

    client = OAuthClient(
        client_id='https://myapp.example.com/client-metadata.json',
        redirect_uri='https://myapp.example.com/callback',
        scope='atproto transition:generic',
        state_store=MemoryStateStore(),
        session_store=MemorySessionStore(),
    )

    # Start authorization — returns a URL to redirect the user to
    auth_url, state = await client.start_authorization('user.bsky.social')
    # Redirect the user to auth_url...

3. Handle the callback after the user authorizes your app:

..  code-block:: python

    # In your callback handler:
    session = await client.handle_callback(
        code=request.args['code'],
        state=request.args['state'],
        iss=request.args['iss'],
    )
    print(f'Authenticated as {session.did} ({session.handle})')

4. Make authenticated requests to the user's PDS:

..  code-block:: python

    response = await client.make_authenticated_request(
        session=session,
        method='GET',
        url=f'{session.pds_url}/xrpc/app.bsky.actor.getProfile',
        params={'actor': session.did},
    )

Session management
------------------

Access tokens expire. The ``OAuthSession.expires_at`` field tells you when. Use ``refresh_session`` to get new tokens before the old ones expire:

..  code-block:: python

    from datetime import datetime, timezone

    if session.expires_at and datetime.now(timezone.utc) >= session.expires_at:
        session = await client.refresh_session(session)

To revoke a session (log the user out):

..  code-block:: python

    await client.revoke_session(session)

Stores
------

The ``state_store`` holds temporary state during the authorization flow. The ``session_store`` holds active sessions with tokens.

The built-in ``MemoryStateStore`` and ``MemorySessionStore`` work for development but lose data on restart. For production, implement the ``StateStore`` and ``SessionStore`` abstract base classes with persistent storage (database, Redis, etc.):

..  code-block:: python

    from atproto_oauth.stores.base import StateStore, SessionStore

    class MySessionStore(SessionStore):
        async def save_session(self, session):
            # save to database
            ...

        async def get_session(self, did):
            # load from database
            ...

        async def delete_session(self, did):
            # delete from database
            ...

Confidential clients
--------------------

Server-side applications can use confidential client authentication with ``private_key_jwt`` for stronger security. Provide your signing key when creating the client:

..  code-block:: python

    from cryptography.hazmat.primitives.asymmetric import ec

    # Load or generate your client's signing key
    client_secret_key = ec.generate_private_key(ec.SECP256R1())

    client = OAuthClient(
        client_id='https://myapp.example.com/client-metadata.json',
        redirect_uri='https://myapp.example.com/callback',
        scope='atproto transition:generic',
        state_store=MemoryStateStore(),
        session_store=MemorySessionStore(),
        client_secret_key=client_secret_key,
    )

.. note::
    Your ``client-metadata.json`` must declare ``token_endpoint_auth_method`` as ``private_key_jwt`` and include the corresponding public key in ``jwks`` when using confidential client authentication.

.. automodule:: atproto_oauth
   :members:
   :undoc-members:
   :inherited-members:
