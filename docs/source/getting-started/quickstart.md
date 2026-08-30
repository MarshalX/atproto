# Quickstart

Log in, post, and read something back. Five minutes.

If you have not installed the SDK yet, see [Installation](installation.md).

## Create a client

Everything starts with a client. There are two, differing only in the import and in whether you `await` the calls. If you are not already using `asyncio`, use the sync one.

::::{tab-set}
:::{tab-item} Sync
```python
from atproto import Client

client = Client()
```
:::
:::{tab-item} Async
```python
from atproto import AsyncClient

client = AsyncClient()
```
:::
::::

By default the client talks to `bsky.social`. Pass a base URL to point it somewhere else:

```python
client = Client('https://pds.example.com')
```

You rarely need to. After you log in, the client reads your account's PDS out of its DID document and repoints itself there automatically.

The rest of this page shows the sync version. The async one is identical with `await` in front.

## Log in

```python
client = Client()
profile = client.login('my-handle.bsky.social', 'my-app-password')
print('Welcome,', profile.display_name)
```

:::{warning}
Use an [app password](https://bsky.app/settings/app-passwords), not your account password. And do not hardcode it: read it from the environment or a secrets store.

`createSession` is also rate limited by handle at 30 requests per 5 minutes. If your program runs repeatedly, save and reuse the session instead of logging in each time. See [Authentication](../guides/authentication.md).
:::

## Send a post

```python
client.send_post(text='Hello World from the Python SDK!')
```

Links, mentions, and hashtags are byte ranges over the text rather than markup, so building them by hand is fiddly. `TextBuilder` does it for you:

```python
from atproto import Client, client_utils

client = Client()
client.login('my-handle.bsky.social', 'my-app-password')

text = client_utils.TextBuilder().text('Hello World from ').link('Python SDK', 'https://atproto.blue')
post = client.send_post(text)
```

## Like what you just posted

`send_post` returns a reference to the record it created. Most write methods do, and you need that reference to act on the record later:

```python
post = client.send_post(text='Hello World from the Python SDK!')
client.like(post.uri, post.cid)
```

## Read a timeline

```python
timeline = client.get_timeline(algorithm='reverse-chronological')
for feed_view in timeline.feed:
    print(feed_view.post.author.handle, '-', feed_view.post.record.text)
```

## All together

::::{tab-set}
:::{tab-item} Sync
```python
from atproto import Client, client_utils


def main() -> None:
    client = Client()
    profile = client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)

    text = client_utils.TextBuilder().text('Hello World from ').link('Python SDK', 'https://atproto.blue')
    post = client.send_post(text)
    client.like(post.uri, post.cid)


if __name__ == '__main__':
    main()
```
:::
:::{tab-item} Async
```python
import asyncio

from atproto import AsyncClient, client_utils


async def main() -> None:
    client = AsyncClient()
    profile = await client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)

    text = client_utils.TextBuilder().text('Hello World from ').link('Python SDK', 'https://atproto.blue')
    post = await client.send_post(text)
    await client.like(post.uri, post.cid)


if __name__ == '__main__':
    asyncio.run(main())
```
:::
::::

## What you just used, and what is underneath it

`send_post`, `like`, `get_timeline` and their siblings are convenience methods. They are not the AT Protocol API. They are a small hand-written layer over it, covering the things people do most often.

Underneath sits the real thing: every lexicon the network publishes, generated into typed namespaces and Pydantic models. When the convenience layer does not cover what you need, you drop into it:

```python
client.com.atproto.repo.create_record(...)
client.app.bsky.graph.get_follows(...)
client.chat.bsky.convo.list_convos(...)
```

Nothing is hidden from you. See [Records and repositories](../guides/records-and-repos.md) and [Working with models](../guides/models.md).

## Where to go next

- [Concepts](../guides/concepts.md): the protocol vocabulary you will meet in every method name.
- [Guides](../guides/index.md): posting, reading, streaming, error handling, and the rest.
- [Examples](../examples/index.md): every runnable example in the repository.
- [Custom lexicons](../cli/custom-lexicons.md): if your project has lexicons of its own.
