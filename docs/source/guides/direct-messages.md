# Direct messages

Bluesky direct messages launched on 22 May 2024, and the Python SDK has supported them since day one. You can list conversations, start new ones, send and read messages, react to them, and everything else the apps do.

DMs are not stored in your repository and they are not part of `app.bsky`. They live on a separate service, `chat.bsky`, which is why getting to them takes one extra step.

## App Password scope

:::{attention}
**You must grant access to direct messages when you create the App Password.** Tick **Allow access to your direct messages** in the [app password settings](https://bsky.app/settings/app-passwords). Without that grant every chat call fails with a `Bad token scope` error, no matter how the client is configured.
:::

The grant is baked into the password. If you created the password without it, you cannot add it later. Make a new one. See [Authentication](authentication.md).

## Proxy the client

Chat methods are served by a different service from the rest of the API, and the request has to say so with an `atproto-proxy` header. [with_bsky_chat_proxy](#atproto_client.client.client.Client.with_bsky_chat_proxy) sets it for you:

```python
dm_client = client.with_bsky_chat_proxy()
dm = dm_client.chat.bsky.convo
```

It returns a **clone** of the client that shares your session but carries the header on every request. The original client is untouched, so keep both: `client` for `app.bsky` and `com.atproto` calls, `dm_client` for chat. Because the header applies to all of the clone's requests, do not use the proxied client for ordinary API calls.

It is shorthand for `with_proxy(AtprotoServiceType.BSKY_CHAT, 'did:web:api.bsky.chat')`. See [Proxies and labelers](proxies-and-labelers.md) for the general mechanism and for talking to other services.

The chat namespace under the proxied client has five parts: `convo` for conversations and messages, `actor` for your own chat account, `group` for group conversations, `moderation`, and `notification`. Nearly everything you want is on `convo`.

## A full example

Listing conversations, creating one, sending a message and reacting to it:

```{literalinclude} ../../../examples/advanced_usage/direct_messages.py
:language: python
:caption: examples/advanced_usage/direct_messages.py
```

## Listing conversations

[list_convos](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.list_convos) returns `ConvoView`s under `.convos`, with a `cursor` for paging. See [Pagination](reading.md#pagination). It also filters: `kind` (`'direct'` or `'group'`), `status` (`'request'` or `'accepted'`), `read_state` (`'unread'`) and `lock_status`.

```python
for convo in dm.list_convos(models.ChatBskyConvoListConvos.Params(read_state='unread')).convos:
    print(convo.id, convo.unread_count)
```

A `ConvoView` gives you `id` (which every other convo method takes), `members`, `unread_count`, `muted`, `rev` and `last_message`.

:::{note}
For a group conversation, `members` is only a handful of important members, not the full roster. Use [get_convo_members](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.get_convo_members) when you need all of them.
:::

## Finding or starting a conversation

[get_convo_for_members](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.get_convo_for_members) takes a list of **DIDs** and returns the conversation with those people, creating it if it does not exist yet. Resolve handles first. An [IdResolver](#atproto_identity.resolver.IdResolver) caches the lookups.

```python
chat_to = IdResolver().handle.resolve('test.marshal.dev')
convo = dm.get_convo_for_members(
    models.ChatBskyConvoGetConvoForMembers.Params(members=[chat_to]),
).convo
```

[get_convo](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.get_convo) fetches one you already have the id for.

## Sending and reading messages

[send_message](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.send_message) takes a convo id and a `MessageInput`, and returns the `MessageView` it created, with `id`, `rev`, `sender`, `sent_at` and `text`.

```python
message = dm.send_message(
    models.ChatBskyConvoSendMessage.Data(
        convo_id=convo.id,
        message=models.ChatBskyConvoDefs.MessageInput(text='Hello from Python SDK!'),
    )
)
```

`MessageInput` is not text-only. It also takes `facets`, the same rich text facets as a post, so a [TextBuilder](#atproto_client.utils.text_builder.TextBuilder) works here too; an `embed` for quoting a record; and `reply_to` for threading. Text is capped at 10000 characters.

[get_messages](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.get_messages) reads a conversation back, newest first, with a cursor.

```python
for message in dm.get_messages(models.ChatBskyConvoGetMessages.Params(convo_id=convo.id)).messages:
    print(message.sender.did, message.text)
```

Entries are a union: a `MessageView`, or a `DeletedMessageView` with no `text` for a message that was removed. Check before reaching for `.text`.

## Reactions

[add_reaction](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.add_reaction) and [remove_reaction](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.remove_reaction) both take a convo id, a message id and a `value`, and return the updated message.

```python
dm.add_reaction(
    models.ChatBskyConvoAddReaction.Data(
        convo_id=convo.id,
        message_id=message.id,
        value='👍',
    )
)
```

`value` is a string of 1 to 64 characters. The server decides what it will accept, and in practice that is a single emoji.

Reactions come back on `MessageView.reactions` as `ReactionView`s, each with a `value`, a `sender` and a `created_at`.

## Managing conversations

Also on `convo`:

[update_read](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.update_read)
: Mark a conversation read, up to `message_id` or entirely.

[get_unread_counts](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.get_unread_counts)
: Unread accepted and request conversation counts, each capped at 100.

[mute_convo](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.mute_convo)
: Silence a conversation. [unmute_convo](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.unmute_convo) reverses it.

[list_convo_requests](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.list_convo_requests)
: Requests from people you have not chatted with before. [accept_convo](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.accept_convo) accepts one.

[leave_convo](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.leave_convo)
: Leave.

[delete_message_for_self](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.delete_message_for_self)
: Remove a message from your own view. It stays in everyone else's.

[get_log](#atproto_client.namespaces.sync_ns.ChatBskyConvoNamespace.get_log)
: A cursored log of chat events (new messages, reactions, reads) across all your conversations. This is how you follow chat without re-listing everything on a timer.

## See also

- [Authentication](authentication.md): app passwords and the scope that gates all of this.
- [Proxies and labelers](proxies-and-labelers.md): what `with_bsky_chat_proxy` does underneath.
- [Posting](posting.md): rich text facets, which messages accept as well.
