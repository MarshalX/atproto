# Concepts

The AT Protocol's vocabulary shows up in every method name and model in this SDK. This page is a short translation of that vocabulary into Python, enough to read the rest of the documentation, with a link to the real specification for each term.

:::{note}
This is not a protocol tutorial and does not try to be. The protocol is documented properly at [atproto.com](https://atproto.com/guides/understanding-atproto), and there is a full [glossary](https://atproto.com/guides/glossary). Everything below is here only so the SDK's naming makes sense.
:::

## Identity

**Handle**
: A domain name that identifies an account: `marshal.dev`, `alice.bsky.social`. Handles are human-readable and can change. Resolve one with [IdResolver](#atproto_identity.resolver.IdResolver):

  ```python
  from atproto import IdResolver

  did = IdResolver().handle.resolve('marshal.dev')
  ```

  [Handle spec](https://atproto.com/specs/handle)

**DID**
: The stable identifier behind a handle: `did:plc:...` or `did:web:...`. It never changes, so this is what you store in your database, and it is what every method wanting a "repo" argument expects. `client.me.did` after login.

  [DID spec](https://atproto.com/specs/did)

**DID document**
: What a DID resolves to: the account's current handle, its signing key, and the PDS hosting it. The SDK models it as [DidDocument](#atproto_core.did_doc.did_doc.DidDocument), with `get_pds_endpoint()` and `get_signing_key()` accessors. The client reads it at login to find your PDS.

  See [Identity](identity.md).

## Storage

**PDS**
: Personal Data Server, the host that stores an account's repository and serves its API. Not necessarily `bsky.social`; the client follows whichever one your DID document names.

**Repository**
: The account's data, as a signed key-value store of records. Everything you create (posts, likes, follows, your profile) is a record in your repository.

  [Repository spec](https://atproto.com/specs/repository)

**Collection**
: A namespace within a repository, named by NSID. All your posts live in the `app.bsky.feed.post` collection.

**Record**
: One JSON document in a collection, validated against a lexicon. In the SDK a record is a Pydantic model: `models.AppBskyFeedPost.Record`.

**Record key (rkey)**
: A record's identifier within its collection. Usually a timestamp-based `TID`, but some records use a literal key: your profile is always at rkey `self`.

  [Record key spec](https://atproto.com/specs/record-key)

**AT-URI**
: The address of a record: `at://did:plc:.../app.bsky.feed.post/3k5z...`. The SDK models it as [AtUri](#atproto_core.uri.uri.AtUri), which is how you get from a URI back to its parts:

  ```python
  from atproto import AtUri

  uri = AtUri.from_str('at://did:plc:abc/app.bsky.feed.post/3k5z')
  uri.hostname, uri.collection, uri.rkey
  ```

  [AT-URI spec](https://atproto.com/specs/at-uri-scheme)

**CID**
: A content hash identifying an exact version of a record. Write methods that modify or delete something take both a URI and a CID, so the server can tell you are acting on the version you think you are.

**Blob**
: Binary content, images and video, stored separately from records. You upload one with `upload_blob` and get back a [BlobRef](#atproto_client.models.blob_ref.BlobRef) to embed in a record. See [Posting](posting.md).

  [Blob spec](https://atproto.com/specs/blob)

## Schemas

**Lexicon**
: A JSON schema describing a record type or an API method. Every model and every namespace method in this SDK is generated from one. The network's lexicons ship with the SDK; yours can be compiled the same way. See [Custom lexicons](../cli/custom-lexicons.md).

  [Lexicon guide](https://atproto.com/guides/lexicon) · [spec](https://atproto.com/specs/lexicon)

**NSID**
: The reverse-domain name of a lexicon: `app.bsky.feed.post`, `com.atproto.repo.createRecord`. NSIDs are the organising principle of the whole SDK. They become namespace paths (`client.app.bsky.feed.post`), model aliases (`models.AppBskyFeedPost`), and constants (`models.ids.AppBskyFeedPost`).

  [NSID spec](https://atproto.com/specs/nsid)

**XRPC**
: The HTTP convention the protocol uses: every lexicon method is a `GET` (query) or `POST` (procedure) at `/xrpc/<nsid>`. `client.app.bsky.feed.get_timeline(...)` is one of these.

  [XRPC spec](https://atproto.com/specs/xrpc)

## The network

**AppView**
: A service that aggregates the network into something readable: timelines, threads, follower counts. `app.bsky.*` methods are AppView methods; `com.atproto.*` methods are protocol ones your PDS serves. This is why a non-Bluesky PDS may not answer `app.bsky.actor.getProfile`.

**Relay**
: A service that aggregates every PDS's events into one stream. That stream is the [firehose](firehose.md).

  [bsky.network/docs/relay](https://bsky.network/docs/relay)

**Jetstream**
: A lighter-weight view of the same events as plain JSON, filtered server-side. No signatures, so no cryptographic verifiability, but far cheaper to consume. See [Jetstream](jetstream.md).

**Feed generator**
: A service you run that returns a list of post URIs, which Bluesky then renders as a custom feed. See [Building a feed generator](feed-generator.md).

**Labeler**
: A moderation service that publishes labels on accounts and records. See [Proxies and labelers](proxies-and-labelers.md).

## Naming conventions in this SDK

Lexicons are camelCase; Python is not. The generator translates consistently:

| Lexicon                          | Python                                |
| -------------------------------- | ------------------------------------- |
| `app.bsky.feed.getTimeline`      | `client.app.bsky.feed.get_timeline()` |
| `app.bsky.feed.post`             | `models.AppBskyFeedPost`              |
| `createdAt` field                | `created_at` attribute                |
| `app.bsky.feed.post` NSID string | `models.ids.AppBskyFeedPost`          |

One wrinkle: fields whose name collides with a Python keyword get a trailing underscore, so the lexicon's `validate` becomes `validate_`.

See [Working with models](models.md) for the full story.
