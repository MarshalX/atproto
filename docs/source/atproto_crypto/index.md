# Crypto

Signature verification and key parsing. This package exists so that a service can check that a request really came from the account that claims to have sent it: you resolve the issuer's signing key from its DID document, and verify the signature against it.

You need it directly only when you are handling raw signatures. Verifying an inbound service-auth JWT, the common case, goes through [Server](../atproto_server/index.md), which uses this package underneath. See [Building a feed generator](../guides/feed-generator.md).

## Verifying a signature

[verify_signature](#atproto_crypto.verify.verify_signature) takes the public key as a `did:key` string, the bytes that were signed, and the signature:

```python
from atproto import verify_signature

is_valid = verify_signature(did_key, signing_input, signature)
```

It returns a `bool`. A key whose algorithm is not supported raises `UnsupportedSignatureAlgorithmError`; a malformed `did:key` raises one of the `DidKeyError` subclasses.

## did:key and multikeys

A `did:key` is `did:key:` followed by a multikey: the compressed public key, prefixed with a multicodec identifying its curve, encoded as base58btc multibase. [parse_did_key](#atproto_crypto.did.parse_did_key) unwraps both layers and decompresses the key:

```python
from atproto_crypto.did import parse_did_key

multikey = parse_did_key(did_key)  # 'did:key:zQ3s...' or 'did:key:zDna...'
print(multikey.jwt_alg)  # ES256K or ES256
print(len(multikey.key_bytes))  # 65: the decompressed public key
```

[Multikey](#atproto_crypto.did.Multikey) is that pair, `jwt_alg` and `key_bytes`, with [from_str](#atproto_crypto.did.Multikey.from_str) and [to_str](#atproto_crypto.did.Multikey.to_str) for the multikey form without the `did:key:` prefix.

Going the other way:

[format_did_key](#atproto_crypto.did.format_did_key)
: Compress a public key and format it as `did:key:...`.

[format_multikey](#atproto_crypto.did.format_multikey)
: The same without the `did:key:` prefix.

[format_did_key_multikey](#atproto_crypto.did.format_did_key_multikey)
: Prefix a multikey that is already compressed.

[get_multikey_alg](#atproto_crypto.did.get_multikey_alg)
: Read the algorithm out of a multikey without decompressing the key.

[get_did_key](#atproto_crypto.did.get_did_key)
: Convert a DID document verification method, its `type` and `publicKeyMultibase`, into a `did:key`. This is what [DidDocument.get_did_key](#atproto_core.did_doc.DidDocument.get_did_key) calls, and it accepts the three types the protocol uses: `EcdsaSecp256r1VerificationKey2019`, `EcdsaSecp256k1VerificationKey2019` and `Multikey`. It returns `None` for anything else.

[Multibase](multibase.rst) has the raw base58btc encode and decode, if you need the layer below.

## Supported algorithms

| Curve                          | JWT alg  | Multicodec prefix |
| ------------------------------ | -------- | ----------------- |
| `p256` (NIST P-256, secp256r1) | `ES256`  | `0x8024`          |
| `secp256k1`                    | `ES256K` | `0xe701`          |

Both are ECDSA over SHA-256, and both are verify-only here: this package does not generate keys or sign. Signatures must be in the compact 64-byte form, and only the low-S variant is accepted; a high-S signature over otherwise valid data verifies as `False`, per [the cryptography spec](https://atproto.com/specs/cryptography#ecdsa-signature-malleability).

```{eval-rst}
.. automodule:: atproto_crypto
   :members:
   :undoc-members:
   :show-inheritance:
```

## Submodules

```{toctree}
:maxdepth: 4

did
multibase
verify
```
