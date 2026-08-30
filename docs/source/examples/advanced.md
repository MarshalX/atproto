# Advanced usage

Longer examples that go past the high-level client: session handling, pagination, the embed models, transport configuration, and error handling.

## Reuse a session across runs

`createSession` is rate limited by handle. If your program starts and exits repeatedly, export the session string and log in with that instead of the password. See [Authentication](../guides/authentication.md).

```{literalinclude} ../../../examples/advanced_usage/session_reuse.py
:language: python
:caption: examples/advanced_usage/session_reuse.py
```

## Page through a cursor

There is no pagination helper. Responses carry a `cursor` you feed back in until the server stops returning one.

```{literalinclude} ../../../examples/advanced_usage/handle_cursor_pagination.py
:language: python
:caption: examples/advanced_usage/handle_cursor_pagination.py
```

## Rich text by hand

`TextBuilder` covers most cases. This is what it builds underneath, if you need the facets themselves.

```{literalinclude} ../../../examples/advanced_usage/send_rich_text.py
:language: python
:caption: examples/advanced_usage/send_rich_text.py
```

## Turn bare URLs into links

Detecting URLs in arbitrary text and computing their byte offsets. Note that facet indices are byte offsets into the UTF-8 encoding, not character offsets.

```{literalinclude} ../../../examples/advanced_usage/auto_hyperlinks.py
:language: python
:caption: examples/advanced_usage/auto_hyperlinks.py
```

## Embed an external link or a record

```{literalinclude} ../../../examples/advanced_usage/send_embed.py
:language: python
:caption: examples/advanced_usage/send_embed.py
```

## Build a link card from OGP tags

Fetch the target page, read its Open Graph tags, upload the thumbnail as a blob, and attach the result as an external embed.

```{literalinclude} ../../../examples/advanced_usage/send_ogp_link_card.py
:language: python
:caption: examples/advanced_usage/send_ogp_link_card.py
```

## Resolve a bsky.app URL to a post

A web URL carries a handle and a record key. Getting the record means resolving the handle to a DID first.

```{literalinclude} ../../../examples/advanced_usage/get_bsky_post_by_url.py
:language: python
:caption: examples/advanced_usage/get_bsky_post_by_url.py
```

## Update your profile

The profile is a record like any other, at rkey `self`. Read it, change it, put it back. Do not create a new one, or you will drop the fields you did not set.

```{literalinclude} ../../../examples/advanced_usage/update_profile.py
:language: python
:caption: examples/advanced_usage/update_profile.py
```

## Add someone to a list

```{literalinclude} ../../../examples/advanced_usage/add_user_to_list.py
:language: python
:caption: examples/advanced_usage/add_user_to_list.py
```

## Poll for notifications

```{literalinclude} ../../../examples/advanced_usage/notifications_callback.py
:language: python
:caption: examples/advanced_usage/notifications_callback.py
```

## Direct messages

Chat lives on a separate service, so the client has to be proxied to it. The app password needs the direct-messages grant. See [Direct messages](../guides/direct-messages.md).

```{literalinclude} ../../../examples/advanced_usage/direct_messages.py
:language: python
:caption: examples/advanced_usage/direct_messages.py
```

## Proxies and labelers

```{literalinclude} ../../../examples/advanced_usage/proxy_and_labelers.py
:language: python
:caption: examples/advanced_usage/proxy_and_labelers.py
```

## Configure the transport

Timeouts, retries, and anything else `httpx` exposes. See [HTTP and transport](../guides/http-and-transport.md).

```{literalinclude} ../../../examples/advanced_usage/custom_request.py
:language: python
:caption: examples/advanced_usage/custom_request.py
```

## Handle errors

See [Errors and timeouts](../guides/error-handling.md).

```{literalinclude} ../../../examples/advanced_usage/error_handling.py
:language: python
:caption: examples/advanced_usage/error_handling.py
```

## Validate string formats

Handles, DIDs, NSIDs, AT-URIs and the rest are validated only when you opt in. See [String formats](../guides/string-formats.md).

```{literalinclude} ../../../examples/advanced_usage/validate_string_formats.py
:language: python
:caption: examples/advanced_usage/validate_string_formats.py
```
