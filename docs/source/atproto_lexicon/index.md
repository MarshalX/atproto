# Lexicon

A lexicon is the schema of an AT Protocol record, query, procedure or subscription: a JSON document describing what a `app.bsky.feed.post` contains or what `com.atproto.repo.createRecord` takes and returns. The format is the protocol's. See [atproto.com/specs/lexicon](https://atproto.com/specs/lexicon).

This package parses those documents into typed models. It does not generate code, make requests or validate records; it is the reader that everything else is built on.

## Parsing

[lexicon_parse_file](#atproto_lexicon.parser.lexicon_parse_file) reads one document, [lexicon_parse_dir](#atproto_lexicon.parser.lexicon_parse_dir) walks a tree of them:

```python
from atproto_lexicon.parser import lexicon_parse_dir, lexicon_parse_file

doc = lexicon_parse_file('lexicons/app/bsky/feed/post.json')
print(doc.id)  # app.bsky.feed.post
print(list(doc.defs))  # ['main', ...]

docs = lexicon_parse_dir('lexicons')
```

`lexicon_parse_dir` with no argument reads the lexicons vendored in this repository. Both accept `soft_fail=True`, which skips documents that do not parse instead of raising `LexiconParsingError`, which is useful when you point them at a directory you do not control.

A parsed document is a [LexiconDoc](#atproto_lexicon.models.LexiconDoc): `lexicon` (the format version), `id` (the NSID), `defs` (a mapping of definition name to definition), and optionally `description` and `revision`. Each definition is one of the `Lex*` models in [Models](models.rst): `LexRecord`, `LexXrpcQuery`, `LexXrpcProcedure`, `LexSubscription`, `LexObject`, and the primitives they are built from.

## What consumes it

This is the front end of the SDK's code generator. `atproto_codegen` parses the lexicon tree with `lexicon_parse_dir` and emits everything under `atproto_client.models`, the namespace methods on the client, and the generated subscription clients. Every model you use in this SDK started as one of these documents.

That is also why you would use this package yourself: to generate the same bindings for a lexicon that is not Bluesky's. See [Custom lexicons](../cli/custom-lexicons.md).

```{eval-rst}
.. automodule:: atproto_lexicon
   :members:
   :undoc-members:
   :inherited-members:
```

## Submodules

```{toctree}
:maxdepth: 4

parser
models
```
