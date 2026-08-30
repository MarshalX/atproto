# Server

The service side of authentication. When another service calls your service, such as an AppView asking your feed generator for a skeleton, it sends a service-auth JWT signed with the calling account's repository signing key. This package verifies that token.

You need it if you are running something that receives AT Protocol requests. If you are only making requests, [the client](../atproto_client/index.md) handles tokens for you; see [Authentication](../guides/authentication.md).

## Verifying a token

[verify_jwt](#atproto_server.auth.jwt.verify_jwt) does the whole check: decode, validate the time claims, check the audience, resolve the issuer's signing key and verify the signature. You supply the key lookup, because that is a network call the SDK will not make behind your back:

```python
from atproto import IdResolver, verify_jwt

resolver = IdResolver()


def get_signing_key(did: str, force_refresh: bool) -> str:
    return resolver.did.resolve_atproto_key(did, force_refresh)


payload = verify_jwt(jwt, get_signing_key, own_did='did:web:feed.example.com')
print(payload.iss)  # the DID that signed the request
```

[verify_jwt_async](#atproto_server.auth.jwt.verify_jwt_async) is the same with an awaited callback. Pair it with `AsyncIdResolver`. Give the resolver a cache; [Resolving identities](../guides/identity.md) covers that.

The callback is called with `force_refresh=False` first. If the signature does not verify, it is called again with `force_refresh=True` and the signature is re-checked against the fresh key. That is what makes verification survive a key rotation: a token signed with the new key still verifies even though your cache holds the old one. If the fresh key is identical to the cached one, no second attempt is made and `TokenInvalidSignatureError` is raised.

:::{attention}
Pass `own_did`. Without it the audience is not checked, and a token minted for a different service, one the same account genuinely issued to someone else, verifies against yours. The check is exact equality between `aud` and `own_did`.
:::

`leeway` widens the `exp` and `iat` windows by that many seconds, for clock skew between you and the issuer.

## The pieces underneath

[parse_jwt](#atproto_server.auth.jwt.parse_jwt)
: Splits the token into payload bytes, signing input, header and signature, base64url-decoding each. No validation beyond structure.

[get_jwt_payload](#atproto_server.auth.jwt.get_jwt_payload)
: Parses and decodes the payload into a [JwtPayload](#atproto_server.auth.jwt.JwtPayload) with `iss`, `sub`, `aud`, `exp`, `iat`, `scope` and anything else the token carries. It does **not** verify the signature. Use it to read a token you already trust, never to decide whether to trust one.

[validate_jwt_payload](#atproto_server.auth.jwt.validate_jwt_payload)
: Checks `exp` and `iat` against the current time. Claims that are absent are not checked.

[decode_jwt_payload](#atproto_server.auth.jwt.decode_jwt_payload)
: Turns already-decoded payload bytes into a `JwtPayload`.

`verify_jwt` calls all of them in order, so you rarely need them individually. Reading `exp` off your own session token is the usual reason to.

## Exceptions

Everything is raised from `atproto_server.exceptions` and inherits `AtProtocolError`:

| Exception                     | Raised when                                            |
| ----------------------------- | ------------------------------------------------------ |
| `InvalidTokenError`           | base of the four below it                              |
| `TokenDecodeError`            | the token is malformed, or `iss` is missing            |
| `TokenInvalidSignatureError`  | the signature did not verify, even against a fresh key |
| `TokenInvalidAudienceError`   | `aud` does not equal `own_did`                         |
| `TokenExpiredSignatureError`  | `exp` is in the past                                   |
| `TokenImmatureSignatureError` | `iat` is in the future                                 |
| `TokenInvalidIssuedAtError`   | `iat` is not an integer                                |

`TokenInvalidSignatureError` is a subclass of `TokenDecodeError`; the rest inherit `InvalidTokenError` directly. Catching `InvalidTokenError` covers every reason a token can be rejected, which is usually the one thing your handler cares about.

A worked service that verifies inbound tokens is in [Building a feed generator](../guides/feed-generator.md).

```{eval-rst}
.. automodule:: atproto_server
   :members:
   :undoc-members:
   :inherited-members:
```

## Submodules

```{toctree}
:maxdepth: 4

auth
```
