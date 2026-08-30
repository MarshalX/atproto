# Basics

The shortest complete programs in the repository. Each one logs in and does a single thing.

For the prose that explains these, see [Posting](../guides/posting.md), [Reading content](../guides/reading.md), and [The social graph](../guides/social-graph.md).

## Send a post

```{literalinclude} ../../../examples/send_post.py
:language: python
:caption: examples/send_post.py
```

## Reply to a post

Replies need a `ReplyRef` naming both the post you are replying to and the root of the thread.

```{literalinclude} ../../../examples/send_reply.py
:language: python
:caption: examples/send_reply.py
```

## Send rich text

Links, mentions, and hashtags are byte ranges over the post text, not markup. `TextBuilder` computes them for you.

```{literalinclude} ../../../examples/send_rich_text.py
:language: python
:caption: examples/send_rich_text.py
```

## Send an image

Always set alt text.

```{literalinclude} ../../../examples/send_image.py
:language: python
:caption: examples/send_image.py
```

## Send several images

```{literalinclude} ../../../examples/send_images.py
:language: python
:caption: examples/send_images.py
```

## Send a video

```{literalinclude} ../../../examples/send_video.py
:language: python
:caption: examples/send_video.py
```

## Delete a post

```{literalinclude} ../../../examples/delete_post.py
:language: python
:caption: examples/delete_post.py
```

## Read your home timeline

```{literalinclude} ../../../examples/home_timeline.py
:language: python
:caption: examples/home_timeline.py
```

## Read someone's posts

```{literalinclude} ../../../examples/profile_posts.py
:language: python
:caption: examples/profile_posts.py
```

## Like and unlike

Liking creates a record. Keep the URI it returns, because undoing the like means deleting that record.

::::{tab-set}
:::{tab-item} Like
```{literalinclude} ../../../examples/like_post.py
:language: python
:caption: examples/like_post.py
```
:::
:::{tab-item} Unlike
```{literalinclude} ../../../examples/unlike_post.py
:language: python
:caption: examples/unlike_post.py
```
:::
::::

## Repost

```{literalinclude} ../../../examples/repost_post.py
:language: python
:caption: examples/repost_post.py
```

## Process notifications

```{literalinclude} ../../../examples/process_notifications.py
:language: python
:caption: examples/process_notifications.py
```
