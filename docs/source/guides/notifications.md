# Notifications

Likes, replies, follows and mentions arrive as notifications from the AppView. The SDK exposes the `app.bsky.notification` namespace; there is no higher-level wrapper on the client, so you call the namespace methods directly.

## Listing notifications

[list_notifications](#atproto_client.namespaces.sync_ns.AppBskyNotificationNamespace.list_notifications) returns the most recent notifications for the logged-in account.

```python
response = client.app.bsky.notification.list_notifications()
for notification in response.notifications:
    print(notification.reason, notification.author.handle, notification.is_read)
```

Each `Notification` carries:

`reason`
: Why you were notified. See [Reasons](#reasons).

`author`
: The `ProfileView` of whoever caused it.

`uri` and `cid`
: The record that caused it: the like record, the reply post, the follow record.

`reason_subject`
: The AT-URI of *your* record it happened to. On a `like` or `reply`, this is the post of yours that was liked or replied to. Absent for a `follow`, which has no subject.

`record`
: The raw record behind `uri`, as an unknown type. See [Working with models](models.md) for how to narrow it.

`is_read`
: Whether it is below the `seen_at` mark. See [Marking as seen](#marking-as-seen).

`indexed_at`
: When the AppView indexed it. Notifications come back newest first.

The parameters: `cursor` and `limit` for paging (see [Pagination](reading.md#pagination)), `reasons` to filter to a subset of reason strings, `priority` for the priority-only view, and `seen_at` to compute `is_read` against a time other than your stored mark.

## Reasons

`reason` is an open string. The server can add new values, so treat anything you do not recognise as a notification you skip rather than a crash. The values the SDK currently knows are:

`like`
: Someone liked your post.

`repost`
: Someone reposted your post.

`follow`
: Someone followed you.

`mention`
: Someone mentioned you in a post, with a mention facet.

`reply`
: Someone replied to your post.

`quote`
: Someone quoted your post.

`starterpack-joined`
: Someone signed up through your starter pack. The pack is on `starter_pack`.

`verified` / `unverified`
: Your verification status changed.

`like-via-repost` / `repost-via-repost`
: Someone liked or reposted your post from somebody else's repost of it.

`subscribed-post`
: An account you subscribed to activity notifications for has posted.

`contact-match`
: A contact of yours joined.

## The unread count

[get_unread_count](#atproto_client.namespaces.sync_ns.AppBskyNotificationNamespace.get_unread_count) returns just a number, which is much cheaper than listing when all you want is a badge.

```python
print(client.app.bsky.notification.get_unread_count().count)
```

It takes the same `priority` and `seen_at` parameters as `list_notifications`.

## Marking as seen

[update_seen](#atproto_client.namespaces.sync_ns.AppBskyNotificationNamespace.update_seen) takes a single `seen_at` timestamp and moves the server-side mark to it. Everything indexed before that point becomes `is_read=True`, and the unread count drops accordingly.

```python
client.app.bsky.notification.update_seen({'seen_at': client.get_current_time_iso()})
```

`get_current_time_iso` gives you a correctly formatted UTC timestamp.

:::{warning}
Take the timestamp **before** you fetch, not after you finish processing. Anything that arrives while your loop is running is indexed after the mark you captured, so it stays unread and you pick it up on the next pass. Stamping the time at the end silently drops those.
:::

## Polling

There is no push transport. The SDK has no websocket, no long-poll and no callback registration for notifications. You poll `list_notifications` on a timer, or you watch the firehose.

The pattern is: capture the time, fetch, act on everything with `is_read=False`, mark seen with the time you captured, sleep.

```{literalinclude} ../../../examples/process_notifications.py
:language: python
:caption: examples/process_notifications.py
```

The async version does the same thing, but hands each notification to a callback and runs the callbacks concurrently with `asyncio.gather`:

```{literalinclude} ../../../examples/advanced_usage/notifications_callback.py
:language: python
:caption: examples/advanced_usage/notifications_callback.py
```

:::{tip}
Three seconds is fine for one account. Polling is rate limited like any other request, so if you are running a bot across many accounts, back off. The current limits are at [bsky.network/docs/rate-limits](https://bsky.network/docs/rate-limits).
:::

Neither example pages. `list_notifications` returns one page, so a backlog longer than the page size needs the cursor loop from [Pagination](reading.md#pagination). Otherwise `update_seen` marks notifications read that you never looked at.

## The firehose instead

Polling costs you latency and a request per tick. If you want the events as they happen, or you are watching more than your own account, subscribe to the firehose and filter the record stream yourself: a like on your post is an `app.bsky.feed.like` commit whose `subject.uri` is in your repository.

That is more work, because you get every record on the network rather than a list addressed to you, with no `is_read` or seen mark to lean on. But it scales in a way polling does not. See [Firehose](firehose.md).

## See also

- [Reading](reading.md): fetching the post a notification points at.
- [Social graph](social-graph.md): the likes and follows on the other end.
- [Firehose](firehose.md): the streaming alternative.
