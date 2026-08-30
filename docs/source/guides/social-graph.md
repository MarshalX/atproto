# Social graph

Likes, reposts, follows, mutes, blocks, lists and starter packs. Some of these have client methods; the rest you write as records through the `app.bsky.graph` namespace.

## Keep the URI, or you cannot undo it

[like](#atproto_client.client.client.Client.like), [repost](#atproto_client.client.client.Client.repost) and [follow](#atproto_client.client.client.Client.follow) all create a record in **your** repository, and all return a `CreateRecordResponse` with `uri` and `cid`.

That `uri` is the like, not the post. It is the only handle on the record you just wrote, and [unlike](#atproto_client.client.client.Client.unlike), [unrepost](#atproto_client.client.client.Client.unrepost) and [unfollow](#atproto_client.client.client.Client.unfollow) take it, not the post URI and not the DID of the account you followed. Throw the response away and you have no way to undo the action without going back and finding the record again.

```python
post = client.get_posts([post_uri]).posts[0]

like = client.like(uri=post.uri, cid=post.cid)  # like.uri is the *like* record
client.unlike(like.uri)  # not post.uri
```

The un- methods return a boolean.

:::{note}
`unlike`, `unrepost` and `unfollow` are also exposed as `delete_like`, `delete_repost` and `delete_follow`. Same methods, different names.
:::

If you did lose the URI, the like record is still in your repository. List the collection and find the one whose `subject.uri` matches:

```python
records = client.app.bsky.feed.like.list(client.me.did)
for uri, record in records.records.items():
    if record.subject.uri == post_uri:
        client.unlike(uri)
```

## Likes and reposts

`like` and `repost` both take the subject's `uri` **and** `cid`. The CID pins the exact version of the record, which is why you need a hydrated post (or a `CreateRecordResponse`) rather than just a URI.

```{literalinclude} ../../../examples/like_post.py
:language: python
:caption: examples/like_post.py
```

```{literalinclude} ../../../examples/unlike_post.py
:language: python
:caption: examples/unlike_post.py
```

`like` is not limited to posts. The subject can be any record, so you can like a feed generator or a starter pack the same way.

```{literalinclude} ../../../examples/repost_post.py
:language: python
:caption: examples/repost_post.py
```

A repost is a distinct record from a quote post. `repost` boosts the post as-is; quoting it means sending a new post with an `AppBskyEmbedRecord.Main` embed, covered in [Posting](posting.md).

## Follows

[follow](#atproto_client.client.client.Client.follow) takes the **DID** of the account, not a handle. Resolve the handle first if that is what you have.

```python
did = client.resolve_handle('atproto.blue').did
follow = client.follow(did)
client.unfollow(follow.uri)
```

Read the graph back with [get_follows](#atproto_client.client.client.Client.get_follows) and [get_followers](#atproto_client.client.client.Client.get_followers), both of which take an `actor` (handle or DID) and page with a cursor. See [Pagination](reading.md#pagination).

To ask about relationships without walking the whole list, use [get_relationships](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_relationships), which compares one actor against up to 30 others in a single call.

## Mutes

[mute](#atproto_client.client.client.Client.mute) and [unmute](#atproto_client.client.client.Client.unmute) take an actor (handle or DID) and return a boolean. There is nothing to keep afterwards: a mute is server-side state, not a record, so unmuting takes the same actor you muted.

```python
client.mute('spam.example.com')
client.unmute('spam.example.com')
```

Mutes are private and only affect what you see. [get_mutes](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_mutes) lists them.

## Blocks

There is no `block` method on the client. A block is a public record in your repository, so you create and delete it through the `app.bsky.graph.block` record namespace directly:

::::{tab-set}
:::{tab-item} Sync
```python
from atproto import AtUri, Client, models

client = Client()
client.login('my-handle', 'my-password')

block = client.app.bsky.graph.block.create(
    client.me.did,
    models.AppBskyGraphBlock.Record(
        subject='did:plc:kvwvcn5iqfooopmyzvb4qzba',
        created_at=client.get_current_time_iso(),
    ),
)

# to unblock, delete the record
client.app.bsky.graph.block.delete(client.me.did, AtUri.from_str(block.uri).rkey)
```
:::
:::{tab-item} Async
```python
from atproto import AsyncClient, AtUri, models

client = AsyncClient()
await client.login('my-handle', 'my-password')

block = await client.app.bsky.graph.block.create(
    client.me.did,
    models.AppBskyGraphBlock.Record(
        subject='did:plc:kvwvcn5iqfooopmyzvb4qzba',
        created_at=client.get_current_time_iso(),
    ),
)

await client.app.bsky.graph.block.delete(client.me.did, AtUri.from_str(block.uri).rkey)
```
:::
::::

`subject` must be a DID. The `create` call returns the same `uri` / `cid` pair the sugar methods return, and `delete` takes the repository and the record key, which you get by parsing the URI with [AtUri](#atproto_core.uri.AtUri).

:::{warning}
Blocks are public. The record sits in your repository where anyone can read it, and it appears on the firehose like any other record. Mute if you want the effect to stay private.
:::

[get_blocks](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_blocks) lists the accounts you block.

## Lists

A list is two record types working together. `app.bsky.graph.list` is the list itself (name, purpose, description) and each member is a separate `app.bsky.graph.listitem` record pointing at the list URI and a subject DID. Adding someone to a list means creating a listitem; removing them means deleting it.

The `purpose` decides what the list does, and it is a plain string: `'app.bsky.graph.defs#curatelist'` is a curation list you can use as a feed, `'app.bsky.graph.defs#modlist'` is a moderation list you can mute or block in bulk, and `'app.bsky.graph.defs#referencelist'` is a list that only exists to be pointed at, which is what a starter pack uses.

```python
new_list = client.app.bsky.graph.list.create(
    client.me.did,
    models.AppBskyGraphList.Record(
        name='People I argue with',
        purpose='app.bsky.graph.defs#curatelist',
        description='A curation list.',
        created_at=client.get_current_time_iso(),
    ),
)
```

:::{note}
`models.AppBskyGraphDefs.Curatelist`, `Modlist` and `Referencelist` are `typing.Literal` **type aliases**, for annotating your own code. They are not constants, so do not pass them as the value of `purpose`.
:::

This example resolves a handle, adds the account to an existing moderation list, reads the list back to confirm, and deletes the listitem again:

```{literalinclude} ../../../examples/advanced_usage/add_user_to_list.py
:language: python
:caption: examples/advanced_usage/add_user_to_list.py
```

Two things in there are worth calling out. The repository you write the listitem to is the **list owner's** DID, parsed out of the list URI, not necessarily your own. And the `sleep(3)` is real: the AppView indexes the write asynchronously, so [get_list](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_list) can still return the old membership immediately after a successful create.

The read side:

[get_list](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_list)
: One list, hydrated, plus its members under `.items`. Pages with a cursor.

[get_lists](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_lists)
: Every list an actor created. `purposes` filters to `'modlist'` or `'curatelist'`.

[mute_actor_list](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.mute_actor_list)
: Mute everyone on a moderation list, by list URI. [unmute_actor_list](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.unmute_actor_list) reverses it.

[get_list_mutes](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_list_mutes)
: The lists you have muted. [get_list_blocks](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_list_blocks) does the same for the ones you have blocked.

Blocking a whole list is itself a record, `app.bsky.graph.listblock`, created through `client.app.bsky.graph.listblock.create`.

## Starter packs

A starter pack is an `app.bsky.graph.starterpack` record: a name, a `list` AT-URI pointing at the list of people it contains, and up to three feeds. Create the list first, then the pack that references it.

```python
pack = client.app.bsky.graph.starterpack.create(
    client.me.did,
    models.AppBskyGraphStarterpack.Record(
        name='Python devs on atproto',
        list=new_list.uri,
        description='People building on the protocol in Python.',
        created_at=client.get_current_time_iso(),
    ),
)
```

Read them with [get_starter_pack](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_starter_pack) (one, by AT-URI), [get_starter_packs](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_starter_packs) (several) and [get_actor_starter_packs](#atproto_client.namespaces.sync_ns.AppBskyGraphNamespace.get_actor_starter_packs) (everything one account made).

## Your own profile

Your profile is a record too: `app.bsky.actor.profile`, always at `rkey='self'`. There is no `update_profile` method: you read the current record, change the fields you care about, and put it back.

```{literalinclude} ../../../examples/advanced_usage/update_profile.py
:language: python
:caption: examples/advanced_usage/update_profile.py
```

The `swap_record` argument carries the CID you read, which makes the write fail rather than clobber a concurrent change. Note that the example keeps `avatar` and `banner` by copying them across, because a `put_record` replaces the whole record and any field you omit is gone. New avatars and banners are blobs; upload them first, as in [Posting](posting.md#blobs).

## See also

- [Records and repos](records-and-repos.md): the `create` / `delete` machinery the blocks, lists and starter packs on this page are built on.
- [Posting](posting.md): quote posts, which are a different thing from reposts.
- [Reading](reading.md): `get_likes` and `get_reposted_by` on the other side of these records.
- [Notifications](notifications.md): finding out when someone likes or follows you.
