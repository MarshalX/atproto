# HTTP and transport

Underneath the models and namespaces there is one HTTP client. Everything the SDK sends goes through a [Request](#atproto_client.request.Request) (or an [AsyncRequest](#atproto_client.request.AsyncRequest)), which wraps `httpx` and turns responses into either a [Response](#atproto_client.request.Response) or an exception.

You reach it as `client.request`, and you can supply your own.

## Configuring the transport

Both `Request` classes forward every keyword argument to the `httpx` client they construct, so anything `httpx.Client` accepts works:

::::{tab-set}
:::{tab-item} Sync
```python
import httpx
from atproto import Client, Request

request = Request(
    timeout=httpx.Timeout(30.0),
    transport=httpx.HTTPTransport(retries=3),
    proxy='http://localhost:8080',
)

client = Client(request=request)
```
:::
:::{tab-item} Async
```python
import httpx
from atproto import AsyncClient, AsyncRequest

request = AsyncRequest(
    timeout=httpx.Timeout(30.0),
    transport=httpx.AsyncHTTPTransport(retries=3),
    proxy='http://localhost:8080',
)

client = AsyncClient(request=request)
```
:::
::::

The SDK sets `follow_redirects=True` itself; everything else is yours.

Three settings are worth knowing about:

`timeout`
: Defaults to `httpx`'s 5 seconds on every phase. Covered in [Error handling](error-handling.md#timeouts), along with the exception you get when it fires.

`transport`
: `httpx` has no retry logic in its client. Retries live in the transport. `HTTPTransport(retries=n)` retries connection failures only, not responses. For retry-on-5xx you need a transport of your own that wraps `handle_request`.

`proxy` / `mounts`
: An HTTP proxy in the ordinary networking sense. Unrelated to `atproto-proxy`, which is service routing inside the protocol. See [Proxies and labelers](proxies-and-labelers.md).

:::{warning}
A [clone](proxies-and-labelers.md#cloning), which is what `with_proxy` and `with_labelers` return, builds a **fresh** `Request` with default arguments. Your timeout, transport and proxy do not carry over. Give a proxied client its own configured `Request` if it needs one.
:::

```{literalinclude} ../../../examples/advanced_usage/custom_request.py
:language: python
:caption: examples/advanced_usage/custom_request.py
```

## Lifecycle

Each `Request` owns an `httpx` client, and with it a connection pool. Closing it releases the sockets:

::::{tab-set}
:::{tab-item} Sync
```python
client.request.close()
```
:::
:::{tab-item} Async
```python
await client.request.close()
```
:::
::::

Nothing closes it for you, and the client has no context-manager protocol of its own. In a long-running process this rarely matters: one client, one pool, held for the lifetime of the process is the right shape. It matters when you create clients per task, or per clone: each holds its own pool. Close what you create.

## The base URL

A client talks to `https://bsky.social/xrpc` unless you say otherwise. Pass another PDS as the first constructor argument, or repoint an existing client with [update_base_url](#atproto_client.client.client.Client.update_base_url):

```python
client = Client('https://pds.example.com')
client.update_base_url('https://other-pds.example.com')
client.update_base_url()  # back to the default
```

Both go through the same normalization: if what you pass does not already end in `/xrpc`, that suffix is appended (after stripping a trailing slash). So all four of these end up identical:

```text
https://pds.example.com
https://pds.example.com/
https://pds.example.com/xrpc
https://pds.example.com/xrpc  ← what the client stores
```

`login` calls `update_base_url` itself, with the PDS endpoint read out of the account's DID document. That is why a client constructed against `bsky.social` ends up talking to whichever PDS actually hosts the account. See [Authentication](authentication.md).

## Invoking a method directly

Namespace methods are thin: build a model, call [invoke_query](#atproto_client.client.base.ClientBase.invoke_query) or [invoke_procedure](#atproto_client.client.base.ClientBase.invoke_procedure), parse the result. You can call those two yourself when the SDK has no generated method for an NSID: an endpoint your own service defines, or one added to the network since your SDK version.

```python
response = client.invoke_query(
    'com.atproto.identity.resolveHandle',
    params=models.ComAtprotoIdentityResolveHandle.Params(handle='marshal.dev'),
    output_encoding='application/json',
)
```

The signature of both is `(nsid, params=None, data=None, **kwargs)`. `nsid` is appended to the base URL; queries become `GET`, procedures become `POST`. Two keyword arguments are consumed by the SDK rather than forwarded to `httpx`:

`input_encoding`
: The request's `Content-Type`. Sets the header only if you did not set one yourself. When it is `application/json` and `data` is a model, the model is serialized to JSON for you; for any other encoding, pass `data` as `bytes` and it goes through untouched, which is how blob uploads work.

`output_encoding`
: The response's expected `Content-Type`. Declarative only: the SDK reads the actual `Content-Type` off the response to decide whether to parse JSON.

Everything else (`headers`, `content`, and the rest) is passed straight to `httpx`.

:::{note}
`params` and `data` must be model instances, not plain dicts: they are serialized with [get_model_as_dict](#atproto_client.models.utils.get_model_as_dict) and [get_model_as_json](#atproto_client.models.utils.get_model_as_json), which need a model. Build one with [get_or_create](#atproto_client.models.utils.get_or_create) if all you have is a dict. The generated namespace methods do this for you, which is why *they* accept dicts.
:::

## The Response dataclass

Low-level invokes return a [Response](#atproto_client.request.Response), not a model. Four fields:

`success`
: `True`. A non-2xx status raised instead of returning. See [Error handling](error-handling.md). It exists because a lexicon whose output is `bool` is answered with this field.

`status_code`
: The HTTP status. Always 2xx here.

`content`
: The body. Parsed into a `dict` when the response's `Content-Type` contains `application/json`, otherwise the raw `bytes`.

`headers`
: The response headers as a plain `dict` with **lowercased keys**. Repeated headers are joined into one comma-separated value.

To turn one into a model, use [get_response_model](#atproto_client.models.utils.get_response_model), the same function the generated methods call:

```python
from atproto import models
from atproto_client.models.utils import get_response_model

result = get_response_model(response, models.ComAtprotoIdentityResolveHandle.Response)
print(result.did)
```

The same `Response` is what an exception's `.response` carries when a request fails, with `success=False` and `content` holding the server's `XrpcError`.
