# Guides

Task-oriented documentation. If you are looking for the signature of a particular method, you want the [API reference](../atproto_client/index.md) instead.

New here? Start with [Quickstart](../getting-started/quickstart.md), then [Concepts](concepts.md).

## Start here

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`book;1em;sd-mr-1` Concepts
:link: concepts
:link-type: doc

DIDs, handles, records, lexicons and NSIDs: the vocabulary behind every method name.
:::

:::{grid-item-card} {octicon}`key;1em;sd-mr-1` Authentication
:link: authentication
:link-type: doc

App passwords, two-factor login, session reuse, and automatic token refresh.
:::

:::{grid-item-card} {octicon}`sync;1em;sd-mr-1` Sync and async
:link: async
:link-type: doc

The two clients, what differs between them, and running calls concurrently.
:::

::::

## Doing things on Bluesky

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`pencil;1em;sd-mr-1` Posting
:link: posting
:link-type: doc

Text, rich text, replies, images, video, embeds, and link cards.
:::

:::{grid-item-card} {octicon}`rss;1em;sd-mr-1` Reading content
:link: reading
:link-type: doc

Timelines, threads, profiles, and paging through a cursor.
:::

:::{grid-item-card} {octicon}`people;1em;sd-mr-1` The social graph
:link: social-graph
:link-type: doc

Likes, reposts, follows, mutes, blocks, lists, and starter packs.
:::

:::{grid-item-card} {octicon}`bell;1em;sd-mr-1` Notifications
:link: notifications
:link-type: doc

Reading notifications, unread counts, and polling for new ones.
:::

:::{grid-item-card} {octicon}`comment-discussion;1em;sd-mr-1` Direct messages
:link: direct-messages
:link-type: doc

Conversations, messages, and reactions, on a separate service the client proxies to.
:::

::::

## Working with the protocol

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`repo;1em;sd-mr-1` Records and repositories
:link: records-and-repos
:link-type: doc

Past the convenience methods: namespaces, record sugar, and raw repository operations.
:::

:::{grid-item-card} {octicon}`package;1em;sd-mr-1` Working with models
:link: models
:link-type: doc

NSID aliases, building models, `DotDict`, unknown types, and the record registry.
:::

:::{grid-item-card} {octicon}`checklist;1em;sd-mr-1` String formats
:link: string-formats
:link-type: doc

Handles, DIDs, NSIDs, AT-URIs, TIDs, and how to turn on strict validation.
:::

:::{grid-item-card} {octicon}`id-badge;1em;sd-mr-1` Identity
:link: identity
:link-type: doc

Resolving handles and DIDs, DID documents, and caching the results.
:::

::::

## Streaming the network

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`broadcast;1em;sd-mr-1` Firehose
:link: firehose
:link-type: doc

Every event on the network, signed and verifiable, as CAR-encoded commits.
:::

:::{grid-item-card} {octicon}`zap;1em;sd-mr-1` Jetstream
:link: jetstream
:link-type: doc

The same events as plain JSON, filtered server-side, plus archive replay.
:::

::::

## Configuration and operations

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`alert;1em;sd-mr-1` Errors and timeouts
:link: error-handling
:link-type: doc

The exception hierarchy, what maps to which status code, timeouts, and rate limits.
:::

:::{grid-item-card} {octicon}`arrow-switch;1em;sd-mr-1` Proxies and labelers
:link: proxies-and-labelers
:link-type: doc

Routing requests to another service, accepting labelers, and what `clone()` shares.
:::

:::{grid-item-card} {octicon}`gear;1em;sd-mr-1` HTTP and transport
:link: http-and-transport
:link-type: doc

Configuring `httpx`: timeouts, retries, proxies, and the low-level invoke methods.
:::

::::

## Building something bigger

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} {octicon}`server;1em;sd-mr-1` Building a feed generator
:link: feed-generator
:link-type: doc

A complete service, end to end: firehose ingest, the skeleton endpoint, service auth, and publishing the feed.
:::

:::{grid-item-card} {octicon}`file-code;1em;sd-mr-1` Custom lexicons
:link: ../cli/custom-lexicons
:link-type: doc

Generate typed models and a working client from lexicons of your own.
:::

::::

```{toctree}
:hidden:
:maxdepth: 1

concepts
authentication
async
posting
reading
social-graph
notifications
direct-messages
records-and-repos
models
string-formats
identity
firehose
jetstream
error-handling
proxies-and-labelers
http-and-transport
feed-generator
```
