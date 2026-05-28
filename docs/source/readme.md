# Getting Started

## The AT Protocol SDK

> ⚠️ Under construction. Until the 1.0.0 release compatibility between versions is not guaranteed.

Code snippet:
```python
from atproto import Client, client_utils


def main():
    client = Client()
    profile = client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)

    text = client_utils.TextBuilder().text('Hello World from ').link('Python SDK', 'https://atproto.blue')
    post = client.send_post(text)
    client.like(post.uri, post.cid)


if __name__ == '__main__':
    main()

```

<details>
  <summary>Code snippet of async version</summary>

```python
import asyncio

from atproto import AsyncClient, client_utils


async def main():
    client = AsyncClient()
    profile = await client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)

    text = client_utils.TextBuilder().text('Hello World from ').link('Python SDK', 'https://atproto.blue')
    post = await client.send_post(text)
    await client.like(post.uri, post.cid)


if __name__ == '__main__':
    # use run() for a higher Python version
    asyncio.get_event_loop().run_until_complete(main())

```
</details>

```{toctree}
readme.content.md
```
