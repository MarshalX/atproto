# OAuth

OAuth client for the AT Protocol: public, confidential and loopback clients, with PAR, PKCE and DPoP as the [OAuth specification](https://atproto.com/specs/oauth) requires.

[OAuthClient](#atproto_oauth.OAuthClient) / [AsyncOAuthClient](#atproto_oauth.AsyncOAuthClient)
: Starts an authorization, completes it from the callback, and restores or revokes stored sessions.

[OAuthSession](#atproto_oauth.OAuthSession) / [AsyncOAuthSession](#atproto_oauth.AsyncOAuthSession)
: The session of one account. Pass it to [login_oauth](#atproto_client.client.client.Client.login_oauth).

:::{tip}
For how to use these, covering the three kinds of client, session storage, token refresh and scopes, see the [OAuth guide](../guides/oauth.md).
:::

```{eval-rst}
.. automodule:: atproto_oauth
   :members:
   :inherited-members:
   :exclude-members: ScopesSet, ScopePermissionsTransition
```

## Submodules

```{toctree}
:maxdepth: 4

scopes
```
