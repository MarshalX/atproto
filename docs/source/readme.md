# Getting Started

## The AT Protocol SDK

> ⚠️ Under construction. The SDK was built from scratch for 40 hours. Somewhere I speedran. I have a list of things that will break backward compatibility. Until the 1.0.0 release, I am not going to care about it.

Code snippet:
```python
from atproto import Client


def main():
    client = Client()
    profile = client.login('my-handle', 'my-password')
    print('Welcome,', profile.displayName)
    
    post_ref = client.send_post(text='Hello World from Python!')
    client.like(post_ref)

    
if __name__ == '__main__':
    main()

```

<details>
  <summary>Code snippet of async version</summary>

```python
import asyncio

from atproto import AsyncClient


async def main():
    client = AsyncClient()
    profile = await client.login('my-handle', 'my-password')
    print('Welcome,', profile.displayName)
    
    post_ref = await client.send_post(text='Hello World from Python!')
    await client.like(post_ref)

    
if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

```
</details>

```{toctree}
readme.content.md
```
