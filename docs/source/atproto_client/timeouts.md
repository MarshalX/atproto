## Timeouts

SDK uses `HTTPX` under the hood. Which enforce timeouts everywhere by default. The default timeout is **5 seconds**, but you can set it to whatever you want. You can set the timeout for all requests by using custom [Request](#atproto_client.request.Request) instance.

The [InvokeTimeoutError](#atproto_client.exceptions.InvokeTimeoutError) will be raised if the request takes longer than the timeout.

The most common case where you want to increase the timeout is when you are uploading blobs (videos, images, large files).

Learn more about fine-tuning the timeout in the [HTTPX documentation](https://www.python-httpx.org/advanced/timeouts/).

```python
from atproto import Client, Request
from httpx import Timeout


request = Request()  # Use a default 5s timeout everywhere.
request = Request(timeout=Timeout(timeout=10.0))  # Use a default 10s timeout everywhere.
request = Request(timeout=None)  # Disable all timeouts by default.

client = Client(request=request)

# ... invoke methods
```

:::{tip}
Using custom `Request` instance is the best way to configure `HTTPX` client. You can use it for other options as well, like `proxies`, `transport` for retrying policies, etc.
:::

For async interfaces, you can set the timeout in the same way. The [AsyncRequest](#atproto_client.request.AsyncRequest) instance is passed to the `AsyncClient` constructor.

```python
from atproto import AsyncClient, AsyncRequest
from httpx import Timeout

async_request = AsyncRequest()  # Use a default 5s timeout everywhere.
async_request = AsyncRequest(timeout=Timeout(timeout=10.0))  # Use a default 10s timeout everywhere.
async_request = AsyncRequest(timeout=None)  # Disable all timeouts by default.

async_client = AsyncClient(request=async_request)

# ... invoke methods
```
