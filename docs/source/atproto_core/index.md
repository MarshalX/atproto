# Core

The pieces of the AT Protocol that are neither a client nor a server: identifier types, the binary formats repositories are stored and streamed in, and the DID document. Every other package in the SDK depends on this one, and most of it is re-exported from `atproto` directly.

You reach for it when you are handling protocol data rather than calling a method: decoding a firehose commit, parsing an `at://` URI out of a link, reading the PDS endpoint off a DID document.

## What lives here

[CAR](#atproto_core.car.CAR)
: Content Addressable aRchive. Repository exports and firehose commit blocks are CAR files. [from_bytes](#atproto_core.car.CAR.from_bytes) decodes one into [root](#atproto_core.car.CAR.root), the CID of the commit, and [blocks](#atproto_core.car.CAR.blocks), a mapping of CID to raw record data.

[CID](#atproto_core.cid.CID)
: Content Identifier, the `CID` type of [libipld](https://github.com/MarshalX/python-libipld). DAG-CBOR links decode to it. Equal only to another `CID`: compare with a string as `cid == CID(s)`.

[NSID](#atproto_core.nsid.NSID)
: NameSpaced ID, the reverse-domain identifier of every lexicon (`app.bsky.feed.post`). [validate_nsid](#atproto_core.nsid.validate_nsid) checks one without building it.

[STAR](#atproto_core.star.STAR)
: The archive that the repo of an account in a space is exported as. [from_bytes](#atproto_core.star.STAR.from_bytes) decodes one into [meta](#atproto_core.star.STAR.meta), a DAG-CBOR map, and [pairs](#atproto_core.star.STAR.pairs) of key and value in the order of the file.

[AtUri](#atproto_core.uri.AtUri)
: The `at://` scheme. Splits a record URI into [host](#atproto_core.uri.AtUri.hostname), [collection](#atproto_core.uri.AtUri.collection) and [rkey](#atproto_core.uri.AtUri.rkey).

[SpaceRef](#atproto_core.uri.SpaceRef)
: The reference to a space, `at://<did>/space/<type>/<skey>`. [from_str](#atproto_core.uri.SpaceRef.from_str) parses one, and [record_uri](#atproto_core.uri.SpaceRef.record_uri) builds the URI of a record in the space.

[decode_dag](#atproto_core.cbor.decode_dag), [decode_dag_multi](#atproto_core.cbor.decode_dag_multi) and [encode_dag](#atproto_core.cbor.encode_dag)
: DAG-CBOR, the codec records are stored in. `decode_dag_multi` reads several concatenated items out of one buffer, which is how subscription frames carry a header and a body. `encode_dag` writes the canonical form, the one that the CID of a record is computed over, and `canonical=True` makes the decoders reject any other. A link decodes to a [CID](#atproto_core.cid.CID), and a `CID` encodes as a link.

[DidDocument](#atproto_core.did_doc.DidDocument)
: The resolved identity document, with the getters that pull the atproto-specific parts out of it: [get_pds_endpoint](#atproto_core.did_doc.DidDocument.get_pds_endpoint), [get_feed_gen_endpoint](#atproto_core.did_doc.DidDocument.get_feed_gen_endpoint), [get_signing_key](#atproto_core.did_doc.DidDocument.get_signing_key), [get_kem_key](#atproto_core.did_doc.DidDocument.get_kem_key), [get_handle](#atproto_core.did_doc.DidDocument.get_handle).

Decoding a repository export touches most of them at once:

```python
from atproto import CAR, Client

client = Client()
client.login('my-handle', 'my-password')

repo = client.com.atproto.sync.get_repo({'did': client.me.did})
car = CAR.from_bytes(repo)

print(car.root)
print(len(car.blocks))
```

The same decoding applied to live commits is covered in [Firehose](../guides/firehose.md); resolving a DID into a document is covered in [Resolving identities](../guides/identity.md).

## Exceptions

[AtProtocolError](#atproto_core.exceptions.AtProtocolError) is defined here, and it is the root of every exception the SDK raises. Client, firehose, identity, crypto, server and lexicon errors all inherit from it. One `except AtProtocolError` catches anything the SDK can throw. See [Exceptions](../exceptions.rst).

```{eval-rst}
.. automodule:: atproto_core
   :members:
   :undoc-members:
   :inherited-members:
```

## Submodules

```{toctree}
:maxdepth: 4

nsid
cid
uri
car
star
cbor
did_doc
```
