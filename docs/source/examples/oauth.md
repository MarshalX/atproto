# OAuth

Logging in with OAuth instead of a password. For the prose on clients, scopes, session storage and token refresh, see [OAuth](../guides/oauth.md).

## Log in from the command line

A loopback client needs no hosted metadata. The session is kept in a file, so the browser opens only on the first run.

```{literalinclude} ../../../examples/oauth/loopback_cli.py
:language: python
:caption: examples/oauth/loopback_cli.py
```
