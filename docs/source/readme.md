# Getting Started

## The AT Protocol SDK

> ⚠️ Under construction. Until the 1.0.0 release, I am not going to care about backward compatibility between versions.

Code snippet:
```python
from atproto import Client, models


def main():
    client = Client()
    profile = client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)
    
    response = client.send_post(text='Hello World from Python!')
    client.like(models.create_strong_ref(response))

    
if __name__ == '__main__':
    main()

```

<details>
  <summary>Code snippet of async version</summary>

```python
import asyncio

from atproto import AsyncClient, models


async def main():
    client = AsyncClient()
    profile = await client.login('my-handle', 'my-password')
    print('Welcome,', profile.display_name)

    response = await client.send_post(text='Hello World from Python!')
    await client.like(models.create_strong_ref(response))


if __name__ == '__main__':
    # use run() for a higher Python version
    asyncio.get_event_loop().run_until_complete(main())

```
</details>

```{toctree}
readme.content.md
```
