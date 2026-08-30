# Posting

Everything you publish is a record in your repository. This page covers the sugar the client puts on top of `app.bsky.feed.post` (plain text, rich text, images, video, embeds) and how to delete what you created.

## Sending a post

[send_post](#atproto_client.client.client.Client.send_post) takes the text and returns a `CreateRecordResponse` with two fields, `uri` and `cid`. Keep it: you need the URI to delete the post and both fields to reply to it, quote it, or like it.

```{literalinclude} ../../../examples/send_post.py
:language: python
:caption: examples/send_post.py
```

The full signature:

`text`
: The post body, at most 300 graphemes and 3000 bytes. Accepts a `str` or a [TextBuilder](#atproto_client.utils.text_builder.TextBuilder).

`profile_identify`
: Handle or DID of the repository to write to. Defaults to the logged-in account.

`reply_to`
: An `AppBskyFeedPost.ReplyRef`. See [Replies](#replies).

`embed`
: One of `AppBskyEmbedImages.Main`, `AppBskyEmbedExternal.Main`, `AppBskyEmbedRecord.Main`, `AppBskyEmbedRecordWithMedia.Main` or `AppBskyEmbedVideo.Main`.

`langs`
: Up to three BCP-47 language codes. Defaults to `['en']` when you pass nothing, so set it if you are not posting in English.

`facets`
: Rich text ranges. Usually built for you by `TextBuilder`; see [Rich text](#rich-text).

:::{note}
`send_post` is also available as `post`, and `delete_post` as `unsend`. They are plain aliases, not different methods.
:::

## Replies

There is no `send_reply` method. A reply is a normal post carrying a `reply_to` ref, and that ref needs **two** strong references: `root` (the first post in the thread) and `parent` (the post you are answering). Build them with [create_strong_ref](#atproto_client.models.utils.create_strong_ref), which turns anything with a `uri` and `cid` into a `ComAtprotoRepoStrongRef.Main`.

```{literalinclude} ../../../examples/send_reply.py
:language: python
:caption: examples/send_reply.py
```

Getting `root` wrong splits the thread in the app, so carry the root ref down the whole chain and only move `parent`.

## Rich text

Links, mentions and hashtags are not markup. They are *facets*, byte ranges attached to the post alongside the plain text. Read the [Bluesky post guide](https://bsky.network/docs/bluesky-api/creating-a-post) if you want the wire format; the SDK gives you [TextBuilder](#atproto_client.utils.text_builder.TextBuilder) so you do not have to count bytes.

`TextBuilder` has four methods, all of which return the builder so you can chain them:

`text(text)`
: Plain text, no facet.

`link(text, url)`
: Text that links to `url`.

`mention(text, did)`
: Text that mentions an account. Takes a **DID**, not a handle, so resolve the handle first.

`tag(text, tag)`
: Text that acts as a hashtag. `tag` is the tag itself, without the `#`.

Pass the builder straight to `send_post` (or `send_image`, `send_images`, `send_video`) in place of the text. The client calls `build_text` and `build_facets` for you.

```{literalinclude} ../../../examples/send_rich_text.py
:language: python
:caption: examples/send_rich_text.py
```

If you need the two halves separately, to inspect them or to reuse the same text with a different embed, call [build_text](#atproto_client.utils.text_builder.TextBuilder.build_text) and [build_facets](#atproto_client.utils.text_builder.TextBuilder.build_facets) yourself:

```python
builder = client_utils.TextBuilder().text('Built with ').link('atproto', 'https://atproto.blue/')
client.send_post(text=builder.build_text(), facets=builder.build_facets())
```

:::{warning}
Facets must not overlap. `TextBuilder` writes segments in order and never produces overlapping ranges, but if you assemble `facets` by hand you have to guarantee it: two features over the same byte range is invalid.
:::

### Building facets by hand

You do not have to use `TextBuilder`. Pass a list of `AppBskyRichtextFacet.Main` to the `facets` argument and the client sends it as-is. This example scans finished text for URLs and attaches a link facet to each match. Note that the offsets are **byte** offsets into the UTF-8 encoding of the text, not character offsets:

```{literalinclude} ../../../examples/advanced_usage/auto_hyperlinks.py
:language: python
:caption: examples/advanced_usage/auto_hyperlinks.py
```

## Images

[send_image](#atproto_client.client.client.Client.send_image) uploads one image and posts it. [send_images](#atproto_client.client.client.Client.send_images) takes up to four. Both accept the raw bytes, not a path or a file object.

```{literalinclude} ../../../examples/send_image.py
:language: python
:caption: examples/send_image.py
```

Always pass `image_alt`. It is the only description of the picture that a screen reader gets.

`image_aspect_ratio` is optional but worth setting: without it clients fall back to 1:1 and crop your image. It takes an `AppBskyEmbedDefs.AspectRatio(width=..., height=...)`, the ratio rather than the pixel size, so `width=16, height=9` is fine.

```{literalinclude} ../../../examples/send_images.py
:language: python
:caption: examples/send_images.py
```

`image_alts` and `image_aspect_ratios` are positional lists lined up with `images`. Short lists are padded, with missing alts becoming `''` and missing ratios `None`, so the call still succeeds if you supply fewer than you have images. Extra entries are ignored.

## Video

[send_video](#atproto_client.client.client.Client.send_video) works like `send_image`: bytes in, `video_alt` and `video_aspect_ratio` optional.

```{literalinclude} ../../../examples/send_video.py
:language: python
:caption: examples/send_video.py
```

:::{attention}
`send_video` uploads the file with `com.atproto.repo.uploadBlob`, a single plain blob upload, and embeds the result. It does **not** drive the chunked video pipeline.

If you need that pipeline (large files, resumable uploads, transcode status, upload quota), call the `app.bsky.video` namespace directly: [start_upload](#atproto_client.namespaces.sync_ns.AppBskyVideoNamespace.start_upload), [upload_part](#atproto_client.namespaces.sync_ns.AppBskyVideoNamespace.upload_part), [finish_upload](#atproto_client.namespaces.sync_ns.AppBskyVideoNamespace.finish_upload), [get_job_status](#atproto_client.namespaces.sync_ns.AppBskyVideoNamespace.get_job_status), [abort_upload](#atproto_client.namespaces.sync_ns.AppBskyVideoNamespace.abort_upload) and [get_upload_limits](#atproto_client.namespaces.sync_ns.AppBskyVideoNamespace.get_upload_limits). There is no high-level wrapper around them: you drive the job yourself and build the `AppBskyEmbedVideo.Main` embed from the blob it produces.
:::

## Embeds

The `embed` argument takes one of five models. `send_image`, `send_images` and `send_video` are shortcuts that build `AppBskyEmbedImages.Main` and `AppBskyEmbedVideo.Main` for you; the other three you construct yourself.

`AppBskyEmbedExternal.Main`
: A link card. Holds an `External(uri, title, description, thumb)`; `thumb` is a `BlobRef` you upload first.

`AppBskyEmbedRecord.Main`
: A quote post. Holds a strong ref to the record being quoted, which can be any record and not only a post: a feed generator, a list, a starter pack.

`AppBskyEmbedRecordWithMedia.Main`
: A quote post *and* an image or video. Holds a `record` and a `media`.

```{literalinclude} ../../../examples/advanced_usage/send_embed.py
:language: python
:caption: examples/advanced_usage/send_embed.py
```

### Link cards from OGP tags

Nothing fetches the target page for you: `title`, `description` and `thumb` are whatever you put in them. To get the card the app shows, read the [Open Graph](https://ogp.me/) tags off the page yourself and upload `og:image` as a blob:

```{literalinclude} ../../../examples/advanced_usage/send_ogp_link_card.py
:language: python
:caption: examples/advanced_usage/send_ogp_link_card.py
```

:::{tip}
A link card is only a card. It does not make the URL in your text clickable. That needs a link facet, so add one with `TextBuilder` if the URL appears in the body too.
:::

## Blobs

Images, videos, avatars and link-card thumbnails are all *blobs*: binary data uploaded separately from the record that references it. [upload_blob](#atproto_client.client.client.Client.upload_blob) takes bytes and returns a response whose `.blob` is a [BlobRef](#atproto_client.models.blob_ref.BlobRef).

```python
with open('cat.jpg', 'rb') as f:
    blob = client.upload_blob(f.read()).blob

print(blob.mime_type, blob.size, blob.cid)
```

The SDK sends the body with a `*/*` content type, so the MIME type on the returned `BlobRef` is whatever the PDS determined from the bytes. You do not pass it in.

:::{warning}
An uploaded blob is deleted if no record references it within a few minutes, and the size and MIME type restrictions are enforced at the moment the reference is created, not at upload. An upload that succeeds can still fail when you attach it.
:::

A `BlobRef` carries `mime_type`, `size` and `ref`, plus a `cid` property that decodes `ref` into a CID whichever way it is stored. The `ref` has two representations, because JSON and CBOR encode a CID differently:

`is_json_representation`
: `ref` is an `IpldLink`, the `{"$link": "..."}` form used in XRPC responses.

`is_bytes_representation`
: `ref` is raw bytes or a string, the form you get out of the firehose and CAR files.

[to_json_representation](#atproto_client.models.blob_ref.BlobRef.to_json_representation) and [to_bytes_representation](#atproto_client.models.blob_ref.BlobRef.to_bytes_representation) convert between them. Both return a **new** `BlobRef`; neither mutates the one you called it on.

```python
# a blob read from the firehose, re-used in a new record
json_blob = firehose_blob.to_json_representation()
```

## Deleting a post

[delete_post](#atproto_client.client.client.Client.delete_post) takes the AT-URI of the post and returns a boolean. It parses the repository and record key out of the URI, so it can only delete records in a repository you can write to.

```{literalinclude} ../../../examples/delete_post.py
:language: python
:caption: examples/delete_post.py
```

Deleting a post does not delete its blobs, its likes, or the replies other people wrote under it.

## See also

- [Reading](reading.md): fetching the posts you and other people wrote.
- [Social graph](social-graph.md): likes, reposts and follows on top of those posts.
- [Working with models](models.md): how the `models.*` types you pass to `embed` are shaped.
