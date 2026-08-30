# Custom lexicons

The models, namespaces, and clients that ship with this SDK are not hand-written. They are generated from the JSON lexicons in `lexicons/`, the ones `atproto.com` and `bsky.app` publish.

Nothing about that is specific to Bluesky. Point the generator at lexicons of your own and it produces the same thing for them: Pydantic models, typed namespaces, record sugar, subscription clients, and a `Client` subclass that talks to your service. You do not fork the SDK and you do not edit anything under `atproto_client/`.

:::{note}
This page is about the Python side. For what a lexicon *is* and how to write one, read [the lexicon guide](https://atproto.com/guides/lexicon) and [the lexicon spec](https://atproto.com/specs/lexicon) on atproto.com.
:::

## A worked example

The SDK's own test fixtures make a good tutorial, and they are in the repository under `examples/custom_lexicons/lexicons/`. Three files describing a small "statusphere" service: a record, a query, and a subscription.

The record is the interesting one, because it references lexicons it does not own:

```{literalinclude} ../../../examples/custom_lexicons/lexicons/xyz.statusphere.status.json
:language: json
:caption: examples/custom_lexicons/lexicons/xyz.statusphere.status.json
```

`subject` points at `com.atproto.repo.strongRef`, `aboutPost` at `app.bsky.feed.post`, `author` at `app.bsky.actor.defs#profileViewBasic`, and `embed` is a union of two Bluesky embed types. None of those are yours. Resolving them correctly is most of what the generator does.

The query and the subscription round it out:

::::{tab-set}
:::{tab-item} Query
```{literalinclude} ../../../examples/custom_lexicons/lexicons/xyz.statusphere.getStatuses.json
:language: json
:caption: examples/custom_lexicons/lexicons/xyz.statusphere.getStatuses.json
```
:::
:::{tab-item} Subscription
```{literalinclude} ../../../examples/custom_lexicons/lexicons/xyz.statusphere.subscribeStatuses.json
:language: json
:caption: examples/custom_lexicons/lexicons/xyz.statusphere.subscribeStatuses.json
```
:::
::::

## Generating

From `examples/custom_lexicons/`:

```bash
atp gen --lexicon-dir ./lexicons custom --output-dir ./statusphere --package statusphere
```

```
Generating statusphere:
- models...
- namespaces...
- subscriptions...
Done! Package written to ./statusphere
```

:::{important}
`--lexicon-dir` belongs to `gen`, not to `custom`, so it goes **before** the subcommand. Putting it after fails with `Error: '--lexicon-dir' is required. Pass it before the subcommand`.
:::

Name the output directory after the package. `--package statusphere` makes the generated code import itself as `statusphere`, so the directory it lives in has to be called `statusphere` and has to be importable, either on `sys.path` or inside your project.

[Ruff must be installed](index.md#ruff-is-required); the generator formats what it writes.

## What lands on disk

```
statusphere/
├── __init__.py
├── client.py                          # attach_namespaces() + StatusphereClient(Client)
├── async_client.py                    # attach_async_namespaces() + AsyncStatusphereClient
├── subscriptions.py                   # message unions, parsers, sync + async clients
├── models/
│   ├── __init__.py                    # the _Ids table and the lazy accessors
│   ├── type_conversion.py             # record registration for $type resolution
│   ├── unknown_type.py
│   └── xyz/statusphere/
│       ├── status.py                  # Record + the *RecordResponse models
│       ├── get_statuses.py            # Params / ParamsDict / Response
│       └── subscribe_statuses.py      # Params + the message defs
└── namespaces/
    ├── __init__.py
    ├── sync_ns.py                     # XyzNamespace, XyzStatusphereNamespace, XyzStatusphereStatusRecord
    └── async_ns.py                    # the async mirror
```

Sync and async are always both generated. `--no-client` drops only `client.py` and `async_client.py`. You still get `namespaces/async_ns.py` and `subscriptions.py`.

## Using it

Two ways in. Either instantiate the generated client, or graft the namespaces onto a client you already have:

```{literalinclude} ../../../examples/custom_lexicons/use_generated_client.py
:language: python
:caption: examples/custom_lexicons/use_generated_client.py
```

### The generated client

`StatusphereClient` subclasses the SDK's [Client](#atproto_client.client.client.Client), so it keeps everything: login and session refresh, the transport, the headers machinery, and all seven built-in namespace roots. It adds `xyz` on top.

The class name is derived from `--package`: underscores become word boundaries and each word is capitalised, then `Client` is appended. `--package my_pkg` gives you `MyPkgClient` and `AsyncMyPkgClient`.

### attach_namespaces

`attach_namespaces(client)` sets one attribute per root authority in your package. It is annotated `client: t.Any` on purpose, because the namespaces it attaches only ever call `invoke_query` and `invoke_procedure`, which is the whole of the `XrpcClient` protocol in `atproto_client.namespaces.base`. Anything satisfying those two methods works: a stock `Client`, your own subclass, or a transport you wrote yourself.

Use it when the client already exists and you do not want to switch classes.

### Record sugar

Records in your lexicons get the same generated helpers the built-in ones get: `create`, `get`, `list`, `delete`, with `rkey`, `swap_commit`, `swap_record` and `validate` where they apply:

```python
client.xyz.statusphere.status.create(client.me.did, status_record)
client.xyz.statusphere.status.list(client.me.did, limit=10)
client.xyz.statusphere.status.get(client.me.did, rkey)
client.xyz.statusphere.status.delete(client.me.did, rkey)
```

These are ordinary `com.atproto.repo.*` calls underneath, so they work against any PDS. See [Records and repositories](../guides/records-and-repos.md).

## How the pieces fit

Three mechanisms make a generated package compose with the SDK rather than duplicate it. You do not have to configure any of them, but knowing they exist explains the behaviour.

### Two tiers of lexicons

The generator reads two sets of lexicons:

`emit_lexicon_dirs`
: from `--lexicon-dir`. Code is generated for these.

`ref_lexicon_dirs`
: from `--sdk-lexicons`, defaulting to the SDK's own `lexicons/`. Parsed so that `$ref`s can be resolved, never emitted.

That split is why `"ref": "com.atproto.repo.strongRef"` in your lexicon becomes a reference to the SDK's existing model instead of generating a second copy of it, or worse a reference to a class that does not exist.

Pass `--sdk-lexicons` when you are generating against a network whose base lexicons differ from the ones the SDK ships.

### Models chain to the SDK's

`statusphere/models/__init__.py` ends with:

```python
__getattr__, __dir__ = make_lazy_accessors(__name__, fallback='atproto_client.models')
```

Your package resolves its own NSID aliases and falls through to the SDK for everything else. So `statusphere.models.XyzStatusphereStatus` comes from your package and `statusphere.models.ComAtprotoRepoStrongRef` comes from the SDK, through the same attribute access. Nothing is imported until it is touched.

### Records resolve by $type at runtime

`models/type_conversion.py` registers a name-only map:

```python
RECORD_TYPES = {
    'xyz.statusphere.status': 'XyzStatusphereStatus',
}
register_record_types('statusphere.models', RECORD_TYPES)
```

The registry stores names rather than classes, so no model module is imported until a record with that `$type` actually shows up.

The consequence worth knowing: **importing your package is what makes its records decode.** A custom record sitting in an `unknown` field of an SDK model, or arriving over the firehose, deserializes to your `Record` class if your package has been imported, and degrades to a [DotDict](#atproto_client.models.dot_dict.DotDict) if it has not.

## Subscriptions

A `subscription` lexicon whose `message.schema` has `refs` gets the full treatment in `subscriptions.py`:

- a `XyzStatusphereSubscribeStatusesMessage` union of the message models,
- a `#fragment`-keyed map from frame type to model,
- `parse_xyz_statusphere_subscribe_statuses_message(frame)`,
- and `XyzStatusphereSubscribeStatusesClient` plus its async twin.

```python
from statusphere.subscriptions import (
    XyzStatusphereSubscribeStatusesClient,
    parse_xyz_statusphere_subscribe_statuses_message,
)

client = XyzStatusphereSubscribeStatusesClient('wss://statusphere.example.com/xrpc', params={'cursor': 42})


def on_message(frame) -> None:
    print(parse_xyz_statusphere_subscribe_statuses_message(frame))


client.start(on_message)
```

The generated client takes `base_uri` and `recv_timeout` rather than hardcoding a host, because deployment values are not part of a lexicon. The SDK's own `FirehoseSubscribeReposClient` is one of these with today's relay defaults filled in. See [Firehose](../guides/firehose.md).

:::{note}
A subscription that declares a `subprotocol` gets the union, the type map, and the parser, but **no client**, because the transport is not the standard one. Jetstream is the example; its client is hand-written for that reason.
:::

## Limitations

The generator does not yet cover everything a lexicon can express:

- **Top-level defs that are bare primitives**. A def that is an `integer`, `boolean`, `bytes`, `cid-link`, `blob`, or `unknown` rather than an `object`, `string`, `token`, or `array` is skipped silently. Wrap it in an object if you need it.
- **`permission` and `permission-set` defs** are not generated.

Neither blocks generating a working package; they mean those particular defs produce no code.

## Keeping generated code out of your diffs

The output is deterministic, so both options work:

- **Commit it.** Your package is importable without a build step, and reviewers see what changed when a lexicon changes.
- **Generate it in CI.** Add the `atp gen custom` invocation to your build and gitignore the output directory. Pin the `atproto` version: generated code is only guaranteed to work with the SDK version that produced it.
