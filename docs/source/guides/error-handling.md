# Error handling

Every exception the SDK raises inherits from [AtProtocolError](#atproto_core.exceptions.AtProtocolError). One `except` clause catches everything the SDK can throw:

```python
from atproto.exceptions import AtProtocolError

try:
    client.send_post(text='Hello')
except AtProtocolError as e:
    print('Something went wrong:', e)
```

That is the floor, not the goal. The interesting distinctions are below it.

## The hierarchy

```text
AtProtocolError
├── ModelError
│   └── ModelFieldNotFoundError
├── RequestErrorBase
│   ├── NetworkError
│   │   └── InvokeTimeoutError
│   ├── UnauthorizedError
│   ├── BadRequestError
│   └── RequestException
├── LoginRequiredError
├── InvalidAtUriError
├── InvalidNsidError
├── InvalidCARFile
└── DAGCBORDecodingError
```

[ModelError](#atproto_client.exceptions.ModelError)
: Data did not validate against the model it was supposed to fit. Raised by [get_or_create](#atproto_client.models.utils.get_or_create) in strict mode, and by every namespace method when the server's response does not match the lexicon. [ModelFieldNotFoundError](#atproto_client.exceptions.ModelFieldNotFoundError) is the narrower case of a field that is not there at all.

[RequestErrorBase](#atproto_client.exceptions.RequestErrorBase)
: The base of everything that comes back from an HTTP request. Carries a `.response`.

[LoginRequiredError](#atproto_client.exceptions.LoginRequiredError)
: Raised locally, before any request, by a method that needs a session when there is none. See [Authentication](authentication.md).

## Inspecting the failure

[RequestErrorBase](#atproto_client.exceptions.RequestErrorBase) carries `.response`, a [Response](#atproto_client.request.Response) with `success`, `status_code`, `content`, and `headers`.

When the server answered with JSON, which an AT Protocol service does for every error it generates itself, `content` is an `XrpcError` with two fields: `error`, the machine-readable name, and `message`, the human-readable text. Those names are what you branch on:

```python
from atproto.exceptions import RequestErrorBase

try:
    client.login('my-handle.bsky.social', 'my-password')
except RequestErrorBase as e:
    if e.response and e.response.content.error == 'AuthFactorTokenRequired':
        ...  # ask the user for their 2FA code
```

`str(e)` already summarizes as `<status> <error>: <message>`, so logging the exception is usually enough.

:::{warning}
`.response` is `None` when the failure happened before a response arrived: a DNS failure, a refused connection, a timeout. `.content` can also be raw `bytes` rather than an `XrpcError` when something in front of the PDS (a proxy, a CDN) generated the error page. Check before you reach into it.
:::

```{literalinclude} ../../../examples/advanced_usage/error_handling.py
:language: python
:caption: examples/advanced_usage/error_handling.py
```

## Which status maps to which exception

A non-2xx response is turned into an exception by status code:

| Status            | Exception                                                         |
| ----------------- | ----------------------------------------------------------------- |
| 400               | [BadRequestError](#atproto_client.exceptions.BadRequestError)     |
| 401, 403          | [UnauthorizedError](#atproto_client.exceptions.UnauthorizedError) |
| 409, 413, 502     | [NetworkError](#atproto_client.exceptions.NetworkError)           |
| any other non-2xx | [RequestException](#atproto_client.exceptions.RequestException)   |

Note what this means in practice:

- **429 is a `RequestException`**, not its own class. Rate limiting is detected by the status code and the headers, not the exception type.
- **409, 413, and 502 are `NetworkError`**, which is otherwise the transport-failure class. A swap-commit conflict (409) and a payload that is too large (413) land there because they are worth retrying the same way a 502 is.
- `UnauthorizedError` covers both "your token is wrong" (401) and "your token is fine but does not grant this" (403). The `error` name in the body separates them. A `Bad token scope` from a chat call means the app password lacks the direct-message grant.

Failures that never reach a status code are mapped from the underlying `httpx` exception instead: a timeout becomes [InvokeTimeoutError](#atproto_client.exceptions.InvokeTimeoutError), and any other network error becomes [NetworkError](#atproto_client.exceptions.NetworkError). Both are raised without a response, so `.response` is `None`.

## Timeouts

The SDK uses `httpx`, which enforces timeouts everywhere by default. The default is **5 seconds**. A request that exceeds it raises [InvokeTimeoutError](#atproto_client.exceptions.InvokeTimeoutError).

Set your own by constructing the [Request](#atproto_client.request.Request) yourself and passing it to the client. Every keyword argument is forwarded to the underlying `httpx` client:

::::{tab-set}
:::{tab-item} Sync
```python
from atproto import Client, Request
from httpx import Timeout

request = Request()  # default 5s everywhere
request = Request(timeout=Timeout(timeout=10.0))  # 10s everywhere
request = Request(timeout=None)  # no timeouts at all

client = Client(request=request)
```
:::
:::{tab-item} Async
```python
from atproto import AsyncClient, AsyncRequest
from httpx import Timeout

request = AsyncRequest()  # default 5s everywhere
request = AsyncRequest(timeout=Timeout(timeout=10.0))  # 10s everywhere
request = AsyncRequest(timeout=None)  # no timeouts at all

client = AsyncClient(request=request)
```
:::
::::

The usual reason to raise it is uploading blobs: videos, images, anything large. Five seconds is not much of a budget for a video.

Fine-tuning is documented in the [HTTPX timeout guide](https://www.python-httpx.org/advanced/timeouts/). A custom `Request` is also where proxies and retry transports go. See [HTTP and transport](http-and-transport.md).

## Rate limits

Rate-limited responses come back as 429, which means a [RequestException](#atproto_client.exceptions.RequestException). The budget is in the response headers, lowercased:

```python
from atproto.exceptions import RequestException

try:
    ...
except RequestException as e:
    if e.response and e.response.status_code == 429:
        print('Reset at:', e.response.headers.get('ratelimit-reset'))
```

The limits that bite hardest are per-handle rather than per-request: `createSession` allows 30 requests per 5 minutes and 300 per day, so a script that constructs a fresh client and logs in on every tick will exhaust it. Keep one client alive, or reuse the session string. See [Authentication](authentication.md).

Current limits are published at [bsky.network/docs/rate-limits](https://bsky.network/docs/rate-limits).

## Where each package's exceptions live

Every package defines its own module. `atproto.exceptions` re-exports all of them **except `atproto_jetstream.exceptions`**, which you have to import from its own package.

`atproto_core.exceptions`
: `AtProtocolError` and the parsing failures of the core primitives: `InvalidNsidError`, `InvalidAtUriError`, `InvalidCARFile`, `DAGCBORDecodingError`.

`atproto_client.exceptions`
: Everything on this page: the model and request errors.

`atproto_identity.exceptions`
: Resolution failures: `DidNotFoundError`, `DidPlcResolverError`, `DidWebResolverError`, `PoorlyFormattedDidError`, `UnsupportedDidMethodError`, `PoorlyFormattedDidDocumentError`, `UnsupportedDidWebPathError`, `AtprotoDataParseError`.

`atproto_crypto.exceptions`
: Key and signature failures: `DidKeyError` and its subclasses, `InvalidCompressedPubkeyError`, `UnsupportedSignatureAlgorithmError`.

`atproto_server.exceptions`
: JWT verification failures: `InvalidTokenError` and its subclasses, including `TokenExpiredSignatureError` and `TokenInvalidSignatureError`. See [Building a feed generator](feed-generator.md).

`atproto_lexicon.exceptions`
: `LexiconParsingError`.

`atproto_subscription.exceptions`
: [SubscriptionError](#atproto_subscription.exceptions.SubscriptionError) and [FrameDecodingError](#atproto_subscription.exceptions.FrameDecodingError), the base of both streaming clients.

`atproto_firehose.exceptions`
: `FirehoseError` and `FirehoseDecodingError`, aliases of the two above, kept for backward compatibility.

`atproto_jetstream.exceptions` (not re-exported; import it directly)
: `JetstreamError`, `JetstreamDecodingError`, plus two conditions worth handling separately: `JetstreamConsumerTooSlowError` (the server dropped you for falling behind) and `JetstreamCursorTooOldError` (your cursor is below the server's retention floor).
