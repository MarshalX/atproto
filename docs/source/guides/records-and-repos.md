# Records and repositories

The high-level client (`send_post`, `like`, `get_profile`) is sugar. Each of those methods builds a model and calls an XRPC method underneath. It covers the common Bluesky cases and nothing else, so as soon as you touch a lexicon it does not know about, you drop a level.

There are three levels, and one script can mix them freely:

1. High-level methods on [Client](#atproto_client.client.client.Client).
2. **Namespaces**: the generated, one-to-one mapping of every lexicon the SDK ships.
3. [invoke_query](#atproto_client.client.base.ClientBase.invoke_query) and [invoke_procedure](#atproto_client.client.base.ClientBase.invoke_procedure), which take a raw NSID string. See [HTTP and transport](http-and-transport.md).

Level 2 is the real API. This page is about it.

## Namespaces

Namespaces are classes that group sub-namespaces, queries, and procedures, following the NSID structure of the lexicons. [ClientRaw](#atproto_client.client.raw.ClientRaw), which `Client` inherits from, attaches seven roots:

`app`
: Application lexicons: what an app exposes to the people using it. `app.bsky` is the Bluesky microblogging app: profiles, posts, feeds, and the social graph.

`chat`
: Private messaging. `chat.bsky` is Bluesky direct messages, which need a proxied client. See [Proxies and labelers](proxies-and-labelers.md).

`com`
: The protocol itself under `com.atproto` (identities, repositories, servers, sync), plus the lexicons of third-party services such as `com.germnetwork`.

`internal`
: Internal Bluesky endpoints that are not part of the public API and may change without notice.

`network`
: Infrastructure services behind the network. Currently `network.bsky.jetstream`.

`site`
: `site.standard`, the vocabulary for websites published on atproto.

`tools`
: `tools.ozone`, the moderation tooling of the network.

Navigate down to the method you want. The leaf is always the query or procedure:

```python
from atproto import Client

client = Client()

client.com.atproto.server.create_session(...)
client.com.atproto.sync.get_blob(...)
client.app.bsky.feed.get_likes(...)
client.app.bsky.graph.get_follows(...)
client.tools.ozone.moderation.get_event(...)
```

Procedures take a `data` argument; queries take `params`, or nothing when the lexicon defines no parameters. Both are covered in [Working with models](models.md).

:::{tip}
The SDK is fully type hinted. Autocompletion from the dot is the fastest way to find a method, and the method's own type hints tell you which model to pass.
:::

## Record sugar

Some sub-namespaces carry a record instead of a method group. Records are not defined in the lexicon as endpoints. The SDK generates them as a convenience layer over `com.atproto.repo.*` for every collection the lexicons declare a record type for:

```python
client.app.bsky.feed.post
client.app.bsky.feed.like
client.app.bsky.graph.follow
client.app.bsky.graph.block
client.app.bsky.actor.profile
client.site.standard.document
# ... and one for every other record type
```

Each of them exposes four methods, with the collection NSID already filled in:

[create](#atproto_client.namespaces.sync_ns.AppBskyFeedPostRecord.create)
: `create(repo, record, rkey=None, swap_commit=None, validate=True, **kwargs)`. Wraps `com.atproto.repo.createRecord`. Returns a `CreateRecordResponse` with `uri` and `cid`.

[get](#atproto_client.namespaces.sync_ns.AppBskyFeedPostRecord.get)
: `get(repo, rkey, cid=None, **kwargs)`. Wraps `com.atproto.repo.getRecord`. Returns a `GetRecordResponse` with `uri`, `cid`, and a typed `value`.

[list](#atproto_client.namespaces.sync_ns.AppBskyFeedPostRecord.list)
: `list(repo, cursor=None, limit=None, reverse=None, **kwargs)`. Wraps `com.atproto.repo.listRecords`. Returns a `ListRecordsResponse` whose `records` is a dict of AT-URI to record, plus a `cursor`.

[delete](#atproto_client.namespaces.sync_ns.AppBskyFeedPostRecord.delete)
: `delete(repo, rkey, swap_commit=None, swap_record=None, **kwargs)`. Wraps `com.atproto.repo.deleteRecord`. Returns a `bool`.

`swap_commit` and `swap_record` are compare-and-swap guards: pass a CID and the write fails unless the repo (or the record) is still at that CID. `rkey` on `create` lets you pick the record key instead of letting the server mint a TID.

:::{note}
`validate` defaults to `True` on `create`, which asks the server to *require* Lexicon validation. The protocol's own default is to validate only for known lexicons. Pass `validate=False` when you are writing a record whose lexicon the PDS does not have.
:::

```python
from atproto import AtUri, Client, models

client = Client()
client.login('my-handle.bsky.social', 'my-password')

posts = client.app.bsky.feed.post.list(client.me.did, limit=10)
for uri, post in posts.records.items():
    print(uri, post.text)

post = client.app.bsky.feed.post.get(client.me.did, AtUri.from_str(uri).rkey)
print(post.value.text)

record = models.AppBskyFeedPost.Record(text='Hello', created_at=client.get_current_time_iso())
new_post = client.app.bsky.feed.post.create(client.me.did, record)
print(new_post.uri, new_post.cid)

client.app.bsky.feed.post.delete(client.me.did, AtUri.from_str(new_post.uri).rkey)
```

### What the sugar does not cover

The sugar is create, read, list, delete. Everything else on the repository is a plain namespace call on [com.atproto.repo](#atproto_client.namespaces.sync_ns.ComAtprotoRepoNamespace):

[put_record](#atproto_client.namespaces.sync_ns.ComAtprotoRepoNamespace.put_record)
: **Updating a record.** There is no `update` in the sugar. `putRecord` writes a record at a known `rkey`, creating it if it does not exist.

[apply_writes](#atproto_client.namespaces.sync_ns.ComAtprotoRepoNamespace.apply_writes)
: Several creates, updates, and deletes committed atomically.

[describe_repo](#atproto_client.namespaces.sync_ns.ComAtprotoRepoNamespace.describe_repo)
: The handle, DID document, and the list of collections a repo actually holds.

[upload_blob](#atproto_client.namespaces.sync_ns.ComAtprotoRepoNamespace.upload_blob) and [list_missing_blobs](#atproto_client.namespaces.sync_ns.ComAtprotoRepoNamespace.list_missing_blobs)
: Blobs are uploaded separately and referenced from a record.

Updating a post's text, for example:

```python
from atproto import AtUri, Client, models

client = Client()
client.login('my-handle.bsky.social', 'my-password')

uri = AtUri.from_str('at://did:plc:.../app.bsky.feed.post/3k...')
current = client.app.bsky.feed.post.get(uri.hostname, uri.rkey)

updated = current.value
updated.text = 'Edited text'

client.com.atproto.repo.put_record(
    models.ComAtprotoRepoPutRecord.Data(
        repo=uri.hostname,
        collection=uri.collection,
        rkey=uri.rkey,
        record=updated,
        swap_record=current.cid,  # fail if someone else wrote first
    )
)
```

## Three equivalent ways to post an image

The same write, at each of the three levels:

```python
from atproto import Client, models

client = Client()
client.login('my-handle.bsky.social', 'my-password')

with open('cat.jpg', 'rb') as f:
    img_data = f.read()

upload = client.upload_blob(img_data)
images = [models.AppBskyEmbedImages.Image(alt='Img alt', image=upload.blob)]
embed = models.AppBskyEmbedImages.Main(images=images)

# 1. low-level: com.atproto.repo.createRecord, collection spelled out
client.com.atproto.repo.create_record(
    models.ComAtprotoRepoCreateRecord.Data(
        repo=client.me.did,
        collection=models.ids.AppBskyFeedPost,
        record=models.AppBskyFeedPost.Record(
            created_at=client.get_current_time_iso(), text='Text of the post', embed=embed
        ),
    )
)

# 2. record sugar: the collection is implied by the namespace path
post = models.AppBskyFeedPost.Record(
    text='Text of the post', embed=embed, created_at=client.get_current_time_iso()
)
client.app.bsky.feed.post.create(client.me.did, post)

# 3. high-level client: the blob upload and the embed are built for you
client.send_image(text='Text of the post', image=img_data, image_alt='Img alt')
```

All three produce the same record. Pick the highest level that does what you need.

## AT-URIs

Records are addressed by AT-URI: `at://<handle-or-did>/<collection>/<rkey>`. The SDK returns them as strings and [AtUri](#atproto_core.uri.AtUri) takes them apart:

```python
from atproto import AtUri

uri = AtUri.from_str('at://did:plc:bv6ggog3tya2z3vxsub7hnal/app.bsky.feed.post/3k2a...')

uri.hostname    # 'did:plc:bv6ggog3tya2z3vxsub7hnal'  # the repo
uri.collection  # 'app.bsky.feed.post'
uri.rkey        # '3k2a...'
```

`hostname` is the repo the record lives in: a DID or a handle, whichever the URI carries. It is what you pass as `repo` to any of the record or `com.atproto.repo` methods. `collection` and `rkey` are empty strings, not `None`, when the URI does not reach that deep, so `at://alice.example.com` parses fine and yields `''` for both.

Build one with [make](#atproto_core.uri.AtUri.make), and turn it back into a string with `str()` or [href](#atproto_core.uri.AtUri.href):

```python
uri = AtUri.make('did:plc:bv6ggog3tya2z3vxsub7hnal', 'app.bsky.feed.post', '3k2a...')
print(str(uri))  # at://did:plc:bv6ggog3tya2z3vxsub7hnal/app.bsky.feed.post/3k2a...
```

[from_str](#atproto_core.uri.AtUri.from_str) raises [InvalidAtUriError](#atproto_core.exceptions.InvalidAtUriError) on input that is not an AT-URI. `AtUri` is hashable and compares by its string form, so it works as a dict key.

:::{note}
`AtUri.http` is a misnomer, since it never returns an HTTP URL, and is deprecated. Use `href`.
:::

The scheme itself is specified at [atproto.com/specs/at-uri-scheme](https://atproto.com/specs/at-uri-scheme); repositories and records are at [atproto.com/specs/repository](https://atproto.com/specs/repository).
