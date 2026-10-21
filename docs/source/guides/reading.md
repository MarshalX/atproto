# Reading

Fetching feeds, posts, threads and profiles. Almost everything on this page is an AppView query (`app.bsky.*`), so it runs against a Bluesky-style AppView rather than against a bare PDS.

## Timelines and feeds

[get_timeline](#atproto_client.client.client.Client.get_timeline) returns the home timeline of the logged-in account.

```{literalinclude} ../../../examples/home_timeline.py
:language: python
:caption: examples/home_timeline.py
```

Each entry is a `FeedViewPost` with three parts worth knowing:

`post`
: The post itself. `post.record` is the `app.bsky.feed.post` record (so `post.record.text`), `post.author` is the profile that wrote it, and `post.uri` / `post.cid` are what you need to like, repost or quote it.

`reason`
: Why the post is in the feed at all. A `ReasonRepost`, whose `by` is the reposter, when someone reposted it, a `ReasonPin` when it is pinned, and `None` when it is simply the author's own post.

`reply`
: Present when the post is a reply; holds the root and parent posts.

`algorithm` selects the feed. `'reverse-chronological'` is the plain Following feed.

[get_author_feed](#atproto_client.client.client.Client.get_author_feed) returns one account's posts. `actor` is a handle or a DID.

```{literalinclude} ../../../examples/profile_posts.py
:language: python
:caption: examples/profile_posts.py
```

`filter` narrows what comes back and defaults to `'posts_with_replies'`. The other accepted values are `'posts_no_replies'`, `'posts_with_media'`, `'posts_and_author_threads'` and `'posts_with_video'`. `include_pins` defaults to `False`.

## Single posts

Three methods, and which one you want depends on what you are holding.

[get_post](#atproto_client.client.client.Client.get_post) reads the raw record straight out of a repository with `com.atproto.repo.getRecord`. It takes the record key, not a URI, and the second argument is the repository (handle or DID). Omit it and it reads from your own. The response is a `GetRecordResponse`, so the record is under `.value`. This is the only one of the three that does not need an AppView, but it also returns no view data: no like counts, no author profile, no embeds resolved.

[get_posts](#atproto_client.client.client.Client.get_posts) takes a list of AT-URIs and returns hydrated `PostView`s under `.posts`: counts, author, viewer state and all. Use it whenever you have URIs.

[get_post_thread](#atproto_client.client.client.Client.get_post_thread) takes one AT-URI and returns the post with its ancestors and replies. `depth` controls how many levels of replies come back and `parent_height` how many levels of parents.

```python
thread = client.get_post_thread(uri=post.uri, depth=2)
print(thread.thread.post.record.text)
for reply in thread.thread.replies or []:
    print('-', reply.post.record.text)
```

:::{note}
`thread.thread` is a union: a `ThreadViewPost` when the post is visible, but a `NotFoundPost` or a `BlockedPost` otherwise. Check `py_type`, or guard on the attribute you are about to touch, before assuming there is a `.post` there. See [Working with models](models.md).
:::

## Profiles

[get_profile](#atproto_client.client.client.Client.get_profile) takes one handle or DID and returns a `ProfileViewDetailed` directly, not wrapped in a response model. [get_profiles](#atproto_client.client.client.Client.get_profiles) takes a list and returns them under `.profiles`.

```python
profile = client.get_profile('atproto.blue')
print(profile.display_name, profile.followers_count, profile.posts_count)
```

The profile of the logged-in account is already on the client as `client.me` after `login`. See [Authentication](authentication.md) for when it is `None`.

## Who liked or reposted a post

[get_likes](#atproto_client.client.client.Client.get_likes) and [get_reposted_by](#atproto_client.client.client.Client.get_reposted_by) both take the post's `uri`, an optional `cid`, and `cursor` / `limit`.

```python
likes = client.get_likes(uri=post.uri, cid=post.cid)
for like in likes.likes:
    print(like.actor.handle, like.created_at)

reposts = client.get_reposted_by(uri=post.uri, cid=post.cid)
for actor in reposts.reposted_by:
    print(actor.handle)
```

Note the asymmetry: `get_likes` gives you like records (`actor` plus `created_at`), while `get_reposted_by` gives you profiles directly.

## Pagination

Every paged method works the same way. The response carries a `cursor` alongside the data, and you pass that cursor back on the next call to get the next page. When the server has nothing more to give, `cursor` comes back `None` (or missing).

[paginate](#atproto_client.utils.pagination.paginate) runs that loop for you. Give it a namespace method and its params. It returns a lazy iterator over the response models, and `.items()` iterates over the items of every page instead:

```{literalinclude} ../../../examples/paginate_follows.py
:language: python
:caption: examples/paginate_follows.py
```

```python
for page in client_utils.paginate(client.app.bsky.feed.get_timeline, {'limit': 100}, max_pages=5):
    print(len(page.feed), page.cursor)
```

It works with every query that takes and returns a `cursor`: `get_timeline`, `get_author_feed`, `get_likes`, `get_reposted_by`, `get_follows`, `get_followers`, `list_notifications`, `list_convos` and the rest. The types follow the method. Pages are the method's `Response` model, and items are whatever its list attribute holds (`ProfileView` for `get_follows`, `FeedViewPost` for `get_timeline`). A method that does not page is a type error. With an [AsyncClient](#atproto_client.client.async_client.AsyncClient) method you get an async iterator, used with `async for`.

Pass `cursor` in the params to start from a saved position. Each request starts after the last page fetched, and the paginator's `cursor` attribute holds the next one. If a loop stops on an exception, such as a rate limit, iterating the same paginator again continues from there.

:::{warning}
Requests happen as you iterate, one per page, and nothing stops a `list(...)` over a huge feed. Cap it with `max_pages`. `limit` is capped server-side, usually at 100, and a tight loop over thousands of pages will hit [rate limits](https://bsky.network/docs/rate-limits).
:::

To write the loop yourself, break on a falsy cursor, not on an empty page. A page can come back with fewer items than `limit`, or with none at all, and still have a cursor pointing at more data. `paginate` also stops if the server repeats a cursor.

```{literalinclude} ../../../examples/advanced_usage/handle_cursor_pagination.py
:language: python
:caption: examples/advanced_usage/handle_cursor_pagination.py
```

## Resolving a bsky.app URL

A URL like `https://bsky.app/profile/test.marshal.dev/post/3laqsdrwwgc24` is not an AT-URI. It holds a *handle* and a record key, and an AT-URI needs a DID. So there are two steps: split the URL, then resolve the handle to a DID with an [IdResolver](#atproto_identity.resolver.IdResolver).

```{literalinclude} ../../../examples/advanced_usage/get_bsky_post_by_url.py
:language: python
:caption: examples/advanced_usage/get_bsky_post_by_url.py
```

That example goes straight to `get_post(rkey, did)`, which returns the raw record. If you want the hydrated view instead, build the URI and call `get_posts`:

```python
did = IdResolver().handle.resolve(handle)
uri = f'at://{did}/app.bsky.feed.post/{rkey}'
post = client.get_posts([uri]).posts[0]
print(post.like_count, post.author.display_name)
```

Going the other way, [AtUri](#atproto_core.uri.AtUri) parses an AT-URI back into its parts:

```python
from atproto import AtUri

uri = AtUri.from_str('at://did:plc:.../app.bsky.feed.post/3laqsdrwwgc24')
print(uri.host, uri.collection, uri.rkey)
```

:::{tip}
`client.resolve_handle(handle)` resolves a handle through your PDS instead, and returns a response with a `.did`. `IdResolver` does the resolution itself over DNS and well-known HTTP, and caches it, which is the better choice when you are resolving many handles.
:::

## See also

- [Posting](posting.md): creating the records this page reads back.
- [Social graph](social-graph.md): follows, followers and lists.
- [Firehose](firehose.md): streaming new records instead of polling for them.
