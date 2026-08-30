# Examples

Every example on these pages is a real file in the [`examples/`](https://github.com/MarshalX/atproto/tree/main/examples) directory of the repository, included here verbatim. Clone the repo and run any of them directly.

They are licensed under [CC0](https://github.com/MarshalX/atproto/blob/main/examples/LICENSE) and so are fully dedicated to the public domain, so use them as the base for your own bots without worrying about copyright.

:::{tip}
Replace `'my-handle'` and `'my-password'` before running anything. Use an [app password](https://bsky.app/settings/app-passwords), not your account password. See [Authentication](../guides/authentication.md).
:::

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} {octicon}`rocket;1em;sd-mr-1` Basics
:link: basics
:link-type: doc

Post, reply, embed images and video, read a timeline, like, repost, and follow.
:::

:::{grid-item-card} {octicon}`tools;1em;sd-mr-1` Advanced usage
:link: advanced
:link-type: doc

Sessions, pagination, rich text, link cards, direct messages, proxies, and error handling.
:::

:::{grid-item-card} {octicon}`broadcast;1em;sd-mr-1` Firehose
:link: firehose
:link-type: doc

Subscribe to the whole network's repository and label events, and decode the commits.
:::

:::{grid-item-card} {octicon}`zap;1em;sd-mr-1` Jetstream
:link: jetstream
:link-type: doc

The same stream as plain JSON, filtered server-side, plus archive backfill.
:::

::::

Two more live elsewhere because they need their surrounding prose:

- [Custom lexicons](../cli/custom-lexicons.md): generating and using a package from your own lexicon files.
- [Building a feed generator](../guides/feed-generator.md): a complete service, walked through end to end.

```{toctree}
:hidden:
:maxdepth: 1

basics
advanced
firehose
jetstream
```
