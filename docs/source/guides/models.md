# Working with models

Models are the dataclasses behind every namespace call: the input of a procedure, the parameters of a query, the output either returns, and every type the lexicons describe. They are generated from the lexicons, so there is one for each definition and no hand-written surface to learn.

This page is the companion to [Records and repositories](records-and-repos.md), which covers the namespaces that consume these models.

## Finding a model

Everything lives under `models`, keyed by an NSID-based alias: the NSID in PascalCase, dots removed:

```python
from atproto import models

models.ComAtprotoIdentityResolveHandle
models.AppBskyFeedPost
models.AppBskyActorGetProfile
# ... one per lexicon
```

Each alias is a module, and the classes inside it follow the lexicon's own shape:

`Params` / `ParamsDict`
: Query parameters.

`Data` / `DataDict`
: Procedure input.

`Response`
: Method output.

`Record`
: A record type, for the lexicons that define one.

`Main`, and any other named definition
: The types the lexicon declares under `defs`.

`CreateRecordResponse`, `GetRecordResponse`, `ListRecordsResponse`
: Sugar responses used by the record methods. See [Record sugar](records-and-repos.md#record-sugar).

The reliable way to find the one you need is the method's own type hint. Every namespace method annotates its arguments and its return with the full dotted path:

```python
def resolve_handle(
    self, params: t.Union[models.ComAtprotoIdentityResolveHandle.Params, ...], ...
) -> 'models.ComAtprotoIdentityResolveHandle.Response': ...
```

:::{tip}
`models.` plus the method name in PascalCase is almost always the alias. Autocompletion after the dot gets you the rest.
:::

### NSID constants

`models.ids` holds the NSID string for every alias, under the same name. Use it instead of typing collection names by hand:

```python
from atproto import models

models.ids.AppBskyFeedPost  # 'app.bsky.feed.post'
models.ids.ComAtprotoRepoCreateRecord  # 'com.atproto.repo.createRecord'
```

## Building an instance

Params and data models can be built two ways. Both are accepted everywhere a namespace method takes one.

Class-based, which is type checked:

```python
from atproto import Client, models

client = Client()
params = models.ComAtprotoIdentityResolveHandle.Params(handle='marshal.dev')
print(client.com.atproto.identity.resolve_handle(params))
```

Dict-based, which is shorter. The SDK builds the model for you:

```python
from atproto import Client

client = Client()
print(client.com.atproto.identity.resolve_handle({'handle': 'marshal.dev'}))
```

The dict form is type checked too: alongside every `Params` and `Data` the generator emits a `ParamsDict` / `DataDict` `TypedDict`, and that is what the method's union accepts.

Models nest as deeply as the lexicons do. An image post is a `Record` holding a `Main` embed holding a list of `Image`, each holding a `BlobRef` you got back from `upload_blob`. Follow the type hints down.

## Converting a model

[get_model_as_dict](#atproto_client.models.utils.get_model_as_dict)
: Model to `dict`. Uses the lexicon's field names (`by_alias=True`) and drops `None` fields, so the result is what goes over the wire, not the Python attribute names.

[get_model_as_json](#atproto_client.models.utils.get_model_as_json)
: The same, as a JSON string.

[get_or_create](#atproto_client.models.utils.get_or_create)
: Raw data to a model. The inverse of the two above.

[get_response_model](#atproto_client.models.utils.get_response_model)
: A [Response](#atproto_client.request.Response) from a low-level invoke to a typed model. This is what the generated namespace methods call on the way out. It special-cases `bool` (returns `response.success`) and `bytes` (returns the raw body).

Both converters also accept a [DotDict](#atproto_client.models.dot_dict.DotDict) and a [BlobRef](#atproto_client.models.blob_ref.BlobRef).

### get_or_create

[get_or_create](#atproto_client.models.utils.get_or_create) turns a dict into a model instance and passes an existing instance through untouched. Two keyword arguments change how forgiving it is:

`strict` (default `True`)
: With `strict=True`, data that does not validate against `model` raises [ModelError](#atproto_client.exceptions.ModelError). With `strict=False`, it falls back to a `DotDict` instead of raising.

`strict_string_format` (default `False`)
: Validates the AT Protocol string formats: handles, DIDs, NSIDs, AT-URIs, CIDs, datetimes. Off by default, because a server is free to send a value this SDK's rules would reject. See [String formats](string-formats.md).

Passing `model=None` asks the SDK to resolve the model itself. That works for records only: the `$type` field is looked up in the record registry, and `None` comes back if nothing matches.

```python
from atproto import models
from atproto_client.models.utils import get_or_create

data = {'$type': 'app.bsky.feed.post', 'text': 'Hello', 'createdAt': '2024-01-01T00:00:00Z'}

post = get_or_create(data, models.AppBskyFeedPost.Record)  # explicit
post = get_or_create(data)  # resolved from $type
```

### Strong references

Many lexicons ask for a `com.atproto.repo.strongRef`, a `uri` plus a `cid` pinning one exact version of a record. [create_strong_ref](#atproto_client.models.utils.create_strong_ref) builds one from anything that has both fields, which includes every create-record response:

```python
from atproto import Client
from atproto_client.models.utils import create_strong_ref

client = Client()
client.login('my-handle.bsky.social', 'my-password')

response = client.send_post(text='Hello World from Python!')
strong_ref = create_strong_ref(response)
```

It raises [ModelError](#atproto_client.exceptions.ModelError) if the model has no `cid` and `uri`.

## Checking a record's type

A method that returns records returns them typed as a union, so you have to narrow before you can read fields. [is_record_type](#atproto_client.models.utils.is_record_type) does that, and accepts the expected type in three forms:

```python
from atproto import models
from atproto_client.models import ids, is_record_type

is_record_type(record.value, ids.AppBskyFeedPost)  # NSID string
is_record_type(record.value, models.AppBskyFeedPost)  # the generated module
is_record_type(record.value, models.AppBskyFeedPost.Record)  # the Record class
```

The module and class forms narrow the type for static type checkers. The NSID form cannot, because a string carries no type information, so it returns a plain `bool`.

:::{warning}
Narrowing is not a runtime guarantee. A custom or extended record that failed validation is decoded to a `DotDict`, and `is_record_type` still matches it by comparing the `$type` field. So the check can pass on a value that is not an instance of the `Record` class. If you rely on typed attribute access afterwards, also check `isinstance(value, models.AppBskyFeedPost.Record)`.
:::

## DotDict

[DotDict](#atproto_client.models.dot_dict.DotDict) is the SDK's fallback for JSON it cannot describe with a generated model. You get one when:

- A record's `$type` is not in the record registry, meaning a lexicon this SDK does not ship.
- A record matches a known `$type` but fails validation.
- A union member carries a `$type` released after this version of the SDK.
- You called `get_or_create(..., strict=False)` and the data did not fit.

It wraps the dict and supports both attribute and item access, at any depth:

```python
model.author.display_name
model['author']['displayName']
model['author'].displayName
```

Keys are matched in both cases: ask for `display_name` and it also tries `displayName`, and the other way round. Missing keys return `None` rather than raising. `to_dict()` unwraps it back to a plain `dict`.

:::{note}
`DotDict` stores keys in camelCase, the wire format, so a new key you assign with a snake_case name is stored camelCased. Existing keys keep whatever case they arrived with.
:::

## Unknown types and open unions

Two mechanisms let a model hold something the lexicons did not describe.

An **open union** is a `ref` union declared open in the lexicon. It is generated as a union of the known members plus a `DotDict` fallback, discriminated on `$type` ([UnknownUnionFallback](#atproto_client.models.unknown_union.UnknownUnionFallback)). A `$type` that matches no member degrades to a `DotDict` without failing the surrounding model. But a `$type` that *does* match a member and then fails validation still raises. New embed and view types released after your SDK version arrive this way instead of breaking the response.

An **unknown field**, the lexicon's `unknown` type and what `record` fields are, is generated as `UnknownType` and resolved through the record registry at validation time ([UnknownRecordFallback](#atproto_client.models.unknown_union.UnknownRecordFallback)). If a record model is registered for the `$type`, you get that model; otherwise, a `DotDict`.

Because the lookup is a runtime registry rather than a union frozen at import time, a record type that a package generated from your own lexicons defines decodes to its own model.

## The record registry

`atproto_client.models.record_registry` maps a record NSID to the model that decodes it.

[register_record_types](#atproto_client.models.record_registry.register_record_types)
: Registers a package's records, by name. No model module is imported until a record of that type is actually decoded.

[resolve_record_type](#atproto_client.models.record_registry.resolve_record_type)
: Returns the model for an NSID, importing it on first use, or `None` if nothing is registered.

The SDK registers its own records when `atproto_client.models` is imported. A package generated from custom lexicons registers its records the same way, from its own `type_conversion` module, which means **importing the generated package is what makes its records decode**. Until you import it, records of those types come back as `DotDict`.

```python
import my_lexicons.models  # registers the record types it defines

# from here on, a record with $type 'com.example.thing' decodes to
# my_lexicons.models.ComExampleThing.Record instead of a DotDict
```

See [Generating models from custom lexicons](../cli/custom-lexicons.md).

## Lazy model loading

The SDK ships thousands of generated models. Importing all of them eagerly would cost seconds of start-up time to build pydantic schemas you will never touch, so `atproto_client.models` does not import them: it installs a module-level `__getattr__` from [make_lazy_accessors](#atproto_client.models.models_loader.make_lazy_accessors).

The first `models.AppBskyFeedPost` resolves the alias through `models.ids`, imports exactly that module, injects the names pydantic needs to resolve its forward references, and caches it on the package. Later accesses are plain attribute lookups. `dir(models)` still lists every alias.

You rarely need to know this, except in two cases:

- The import cost is paid on first *use*, not at import time. To pay it up front instead, before forking worker processes or to keep it out of your first request's latency, call [load_models](#atproto_client.models.models_loader.load_models).
- `from atproto import models` is the way in. `from atproto.models import AppBskyFeedPost` does **not** work, because `atproto.models` is a re-exported attribute, not a submodule, so there is nothing for the import system to find. `from atproto_client.models import AppBskyFeedPost` does work, through the same `__getattr__`.

```python
from atproto_client.models.models_loader import load_models

load_models()  # import and build every generated model now
```
