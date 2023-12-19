# Getting Started

## The AT Protocol SDK

> ⚠️ Under construction. Until the 1.0.0 release, I am not going to care about backward compatibility between versions.

Code snippet:
```python
from atproto import Client, models
from atproto_client.utils import TextBuilder


def main():
    client = Client()
    profile = client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)

    text = TextBuilder().text('Hello World from ').link('Python SDK', 'https://atproto.blue')
    post = client.send_post(text)
    client.like(models.create_strong_ref(post))


if __name__ == '__main__':
    main()

```

<details>
  <summary>Code snippet of async version</summary>

```python
import asyncio

from atproto import AsyncClient, models
from atproto_client.utils import TextBuilder


async def main():
    client = AsyncClient()
    profile = await client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)

    text = TextBuilder().text('Hello World from ').link('Python SDK', 'https://atproto.blue')
    post = await client.send_post(text)
    await client.like(models.create_strong_ref(post))


if __name__ == '__main__':
    # use run() for a higher Python version
    asyncio.get_event_loop().run_until_complete(main())

```
</details>

```{toctree}
readme.content.md
```
