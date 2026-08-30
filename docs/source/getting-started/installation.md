# Installation

```bash
pip install atproto
```

Python 3.9 or newer is required.

That single package pulls in everything: the XRPC clients, the generated models for every lexicon the network publishes, the firehose and Jetstream clients, the identity resolvers, the crypto and JWT helpers, and the [`atp` code generator](../cli/index.md).

## Verify it

```bash
python -c "import atproto; print(atproto.__version__)"
atp --help
```

## What you actually installed

The distribution is one PyPI package built from several importable ones. You rarely need to know this, since `from atproto import ...` re-exports what the others provide, but it explains the module paths you will see in tracebacks and in this documentation.

| Package                | What lives there                                                           |
| ---------------------- | -------------------------------------------------------------------------- |
| `atproto`              | Import shortcuts to everything below. Import from here.                    |
| `atproto_client`       | The XRPC clients, generated models, namespaces, and the rich text builder. |
| `atproto_core`         | NSID, AT-URI, CID, CAR files, DAG-CBOR, DID documents.                     |
| `atproto_identity`     | Handle and DID resolvers, with caching.                                    |
| `atproto_crypto`       | Multibase, `did:key`, signature verification.                              |
| `atproto_server`       | Server-side helpers, notably JWT verification.                             |
| `atproto_subscription` | The websocket subscription runtime the streaming clients are built on.     |
| `atproto_firehose`     | The firehose clients and their deployment defaults.                        |
| `atproto_jetstream`    | The Jetstream v2 client and its archive replay.                            |
| `atproto_lexicon`      | The lexicon parser.                                                        |
| `atproto_codegen`      | The code generator.                                                        |
| `atproto_cli`          | The `atp` command.                                                         |

:::{tip}
Import from `atproto` rather than from the individual packages. It is the stable surface, and it saves you from tracking which package a name currently lives in.

```python
from atproto import AsyncClient, CAR, Client, IdResolver, client_utils, models
```
:::

## Pinning

The SDK is pre-1.0 and does not guarantee compatibility between versions yet. Pin it:

```
atproto~=0.1
```

This matters more than usual if you generate code from [custom lexicons](../cli/custom-lexicons.md): generated packages are only guaranteed to work with the SDK version that produced them.

## Optional extras

Ruff is needed only if you run the code generator. It is deliberately not a dependency:

```bash
pip install ruff
```

## Next

- [Quickstart](quickstart.md): log in and send a post.
- [Guides](../guides/index.md): the task-oriented documentation.
- [Examples](../examples/index.md): every runnable example in the repository.
