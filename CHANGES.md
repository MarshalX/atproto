# Change Log

## Version 0.0.55

**24.10.2024**

* Add Python 3.13 support by @MarshalX in https://github.com/MarshalX/atproto/pull/416
* Add support for `LexRef` as a Schema type of inputs by @MarshalX in https://github.com/MarshalX/atproto/pull/412
* Replace `threading.Lock` with a boolean flag in `_WebsocketClient` by @Darkkekus in https://github.com/MarshalX/atproto/pull/402
* Update compatibility with Read The Docs by @MarshalX in https://github.com/MarshalX/atproto/pull/405
* Update lexicons by @MarshalX in https://github.com/MarshalX/atproto/pull/403, https://github.com/MarshalX/atproto/pull/404, https://github.com/MarshalX/atproto/pull/413
* Fix different cases of response header names by @MarshalX in https://github.com/MarshalX/atproto/pull/415

## Version 0.0.54

**13.09.2024**

* Add `Client.send_video` high-level method by @Meorge in https://github.com/MarshalX/atproto/pull/395
* Add support for `known_values` and `enum` of string properties in objects by @MarshalX in https://github.com/MarshalX/atproto/pull/391
* Update lexicons by @MarshalX in https://github.com/MarshalX/atproto/pull/394 and https://github.com/MarshalX/atproto/pull/398
* Fix string definitions which use `know_values` field as _closed_ enum by @MarshalX in https://github.com/MarshalX/atproto/pull/389
* Fix model field default value generating in cases when this is the only one constraint by @MarshalX in https://github.com/MarshalX/atproto/pull/393
* Fix response parsing for JSON content type by @MarshalX in https://github.com/MarshalX/atproto/pull/397

## Version 0.0.53

**10.09.2024**

**⚡ Thanks to libipld 2.0.0 firehose performance should increase approximately by 30%! No changes from you are required! Check more detailed benchmark results [here](https://github.com/MarshalX/python-libipld/releases/tag/v2.0.0)**

* Add libipld v2.0.0 support by @MarshalX in https://github.com/MarshalX/atproto/pull/315
* Update lexicons fetched from e4d41d6 committed 2024-09-04T10:42:39Z by @MarshalX in https://github.com/MarshalX/atproto/pull/380
* Fix firehose client stop by @MarshalX in https://github.com/MarshalX/atproto/pull/384

## Version 0.0.52

**01.09.2024**

* Add new asyncio implementation support for websockets 13.0; handle `ConnectionError` exception; remove `close_timeout` by @MarshalX in https://github.com/MarshalX/atproto/pull/376
* Add process_commits_async example by @MarshalX in https://github.com/MarshalX/atproto/pull/377
* Update process_commits example by @MarshalX in https://github.com/MarshalX/atproto/pull/374

## Version 0.0.51

**31.08.2024**

* Fix PDS auto-switching for self-hosted instances by @MarshalX in https://github.com/MarshalX/atproto/pull/370
* Update lexicons fetched from bfbac24 committed 2024-08-30T18:18:43Z by @MarshalX in https://github.com/MarshalX/atproto/pull/372

## Version 0.0.50

**30.08.2024**

* Use `jiter` instead of the built-in `json` module to improve performance by @MarshalX in https://github.com/MarshalX/atproto/pull/360
* Update docs example to fix empty blocks of commit by @MarshalX in https://github.com/MarshalX/atproto/pull/363
* Bump `certifi` from 2024.2.2 to 2024.7.4 by @dependabot in https://github.com/MarshalX/atproto/pull/355
* Bump `zipp` from 3.18.1 to 3.19.1 by @dependabot in https://github.com/MarshalX/atproto/pull/356
* Bump `setuptools` from 69.5.1 to 70.0.0 by @dependabot in https://github.com/MarshalX/atproto/pull/357
* Update lexicons by @MarshalX in https://github.com/MarshalX/atproto/pull/358, https://github.com/MarshalX/atproto/pull/359, https://github.com/MarshalX/atproto/pull/364, https://github.com/MarshalX/atproto/pull/366, https://github.com/MarshalX/atproto/pull/367

## Version 0.0.49

**04.07.2024**

**Breaking changes for Direct Messages. Now you must create a client with a chat proxy. See the updated [documentation](https://atproto.blue/en/latest/dm.html)**.

* Add automatically switching to PDS endpoint after login and session resume by @MarshalX in https://github.com/MarshalX/atproto/pull/344
* Add atproto proxy and atproto labelers support by @MarshalX in https://github.com/MarshalX/atproto/pull/345 and https://github.com/MarshalX/atproto/pull/351
* Add `BlobRef` representation conversations by @MarshalX in https://github.com/MarshalX/atproto/pull/348
* Fix `BlobRef` creation for JSON representation by @MarshalX in https://github.com/MarshalX/atproto/pull/340
* Fix `delete_post` example by @MarshalX in https://github.com/MarshalX/atproto/pull/342
* Fix `repost` method by @MarshalX in https://github.com/MarshalX/atproto/pull/343
* Bump urllib3 from 2.2.1 to 2.2.2 by @dependabot in https://github.com/MarshalX/atproto/pull/346
* Update lexicons by @MarshalX in https://github.com/MarshalX/atproto/pull/352, https://github.com/MarshalX/atproto/pull/350, https://github.com/MarshalX/atproto/pull/349, https://github.com/MarshalX/atproto/pull/347, https://github.com/MarshalX/atproto/pull/339, https://github.com/MarshalX/atproto/pull/337

## Version 0.0.48

**01.06.2024**

* Add Firehose Account message (use instead of Identity) by @MarshalX in https://github.com/MarshalX/atproto/pull/335
* Update lexicons fetched from 255d5ea committed 2024-05-31T21:39:21Z by @MarshalX in https://github.com/MarshalX/atproto/pull/334

## Version 0.0.47

**22.05.2024**

**💬 Just shipped: Bluesky Direct Messages! https://atproto.blue/en/latest/dm.html**

**Breaking changes**

Many of these changes were backward compatible for a few months with proper warnings.

* Drop support for Python 3.7 by @MarshalX in https://github.com/MarshalX/atproto/pull/321
* Delete deprecated record models called `Main` instead of `Record` by @MarshalX in https://github.com/MarshalX/atproto/pull/323
* Delete deprecated `SessionString` class by @MarshalX in https://github.com/MarshalX/atproto/pull/324
* Delete deprecated `subject` argument of `.like()` and `.repost()` methods by @MarshalX in https://github.com/MarshalX/atproto/pull/325

**What's Changed**

* Add support for Direct Messages (Chats) by @MarshalX in https://github.com/MarshalX/atproto/pull/331
* Add method to send post with multiple attached photos by @ryoryo25 in https://github.com/MarshalX/atproto/pull/313
* Register chat (DM) namespace by @MarshalX in https://github.com/MarshalX/atproto/pull/330
* Update lexicons by @MarshalX in https://github.com/MarshalX/atproto/pull/312, https://github.com/MarshalX/atproto/pull/314, https://github.com/MarshalX/atproto/pull/317, https://github.com/MarshalX/atproto/pull/322, https://github.com/MarshalX/atproto/pull/327, https://github.com/MarshalX/atproto/pull/328
* Fix HTTP error handling by @MarshalX in https://github.com/MarshalX/atproto/pull/329
* Bump requests from 2.31.0 to 2.32.2 by @dependabot in https://github.com/MarshalX/atproto/pull/332

## Version 0.0.46

**20.03.2024**

* Fix follow redirects by @MarshalX in https://github.com/MarshalX/atproto/pull/309
* Update lexicons fetched from c28e374 committed 2024-03-19T16:26:14Z by @MarshalX in https://github.com/MarshalX/atproto/pull/310

## Version 0.0.45

**14.03.2024**

**Content labeling (moderation) is here! This update brings labeling data-stream support as well ozone.tools API!**

- [Example how to subscribe and process labeling update](https://github.com/MarshalX/atproto/blob/main/examples/firehose/sub_labels.py)
- [Updated documentation about real-time updates](https://atproto.blue/en/latest/atproto_firehose/index.html)

* Add labels firehose data stream by @MarshalX in https://github.com/MarshalX/atproto/pull/304
* Register ozone.tools namespace as root namespace by @MarshalX in https://github.com/MarshalX/atproto/pull/303
* Generate unique namespace classes to avoid collisions between lexicons by @MarshalX in https://github.com/MarshalX/atproto/pull/299
* Update lexicons by @MarshalX in https://github.com/MarshalX/atproto/pull/297, https://github.com/MarshalX/atproto/pull/298, https://github.com/MarshalX/atproto/pull/302
* Fix CIMON by @MarshalX in https://github.com/MarshalX/atproto/pull/300
* Fix lexicon updater by @MarshalX in https://github.com/MarshalX/atproto/pull/301

## Version 0.0.44

**05.03.2024**

* Add identity firehose message by @MarshalX in https://github.com/MarshalX/atproto/pull/294
* Update lexicons fetched from d643b5b committed 2024-02-23T22:59:47Z by @MarshalX in https://github.com/MarshalX/atproto/pull/293
* Update lexicons fetched from c7e6ef0 committed 2024-03-05T19:27:25Z by @MarshalX in https://github.com/MarshalX/atproto/pull/295
* Fix typo in README by @yallxe in https://github.com/MarshalX/atproto/pull/291

## Version 0.0.43

**22.02.2024**

**🎉 New lexicon introduces Account Migration between PDS. More info: https://github.com/bluesky-social/pds/blob/main/ACCOUNT_MIGRATION.md**

* Fix bytes response by @MarshalX in https://github.com/MarshalX/atproto/pull/287
* Update lexicons fetched from 514aab9 committed 2024-02-22T15:43:58Z by @MarshalX in https://github.com/MarshalX/atproto/pull/288
* Bump cryptography from 42.0.2 to 42.0.4 by @dependabot in https://github.com/MarshalX/atproto/pull/289

## Version 0.0.42

**17.02.2024**

* Add `send_ogp_link_card.py` (Open Graph protocol) example by @OhkuboSGMS in https://github.com/MarshalX/atproto/pull/273
* Update lexicons fetched from 8c94979 committed 2024-02-16T02:12:39Z by @MarshalX in https://github.com/MarshalX/atproto/pull/279
* Bump cryptography from 41.0.7 to 42.0.2 by @dependabot in https://github.com/MarshalX/atproto/pull/280
* Fix pyright for pydantic aliases via `alias_generator` by @MarshalX in https://github.com/MarshalX/atproto/pull/277
* Fix `filter` argument of `get_author_feed` method in https://github.com/MarshalX/atproto/pull/278
* Fix pyright errors part 1 by @MarshalX in https://github.com/MarshalX/atproto/pull/278

## Version 0.0.41

**09.02.2024**

**[🔥 New documentation page about auth and session reusing!](https://atproto.blue/en/latest/atproto_client/auth.html)**

* Add on session change callback by @MarshalX in https://github.com/MarshalX/atproto/pull/269
* Update lexicons fetched from e4ec7af committed 2024-02-06T00:10:44Z by @MarshalX in https://github.com/MarshalX/atproto/pull/271

## Version 0.0.40

**04.02.2024**

Syntax sugar for records is here! Check out how simple work with basic operations is:
```python
from atproto import AtUri, Client, models

client = Client()
client.login('my-username', 'my-password')

# get records list
posts = client.app.bsky.feed.post.list(client.me.did, limit=10)
for uri, post in posts.records.items():
    print(uri, post.text)

# get specific record
post = client.app.bsky.feed.post.get(client.me.did, AtUri.from_str(uri).rkey)
print(post.value.text)

# create new  record
post_record = models.AppBskyFeedPost.Record(text='test record namespaces', created_at=client.get_current_time_iso())
new_post = client.app.bsky.feed.post.create(client.me.did, post_record)
print(new_post)

# delete record
deleted_post = client.app.bsky.feed.post.delete(client.me.did, AtUri.from_str(new_post.uri).rkey)
print(deleted_post)
```

**⚠️ Record models have been renamed from "Main" to "Record". Backward compatibility is provided but will be removed soon!**
**⚠️ Internals of High-Level Clients have been migrated to new syntax sugar. It could affect you because returned models are changed but the fields are the same.**

* Add record syntax sugar with get, list, create, and delete methods by @MarshalX in https://github.com/MarshalX/atproto/pull/263
* Rename record models from "Main" to "Record" by @MarshalX in https://github.com/MarshalX/atproto/pull/264
* Integrate syntax sugar for repo operations upon records by @MarshalX in https://github.com/MarshalX/atproto/pull/266

## Version 0.0.39

**02.02.2024**

**⚠️ Using strong references in `.like()` and `.repost()` methods are deprecated. Use URI and CID arguments instead.**

* Use .like() and .repost() methods without strong reference by @MarshalX in https://github.com/MarshalX/atproto/pull/255
* Allow Service URl as base URL by @MarshalX in https://github.com/MarshalX/atproto/pull/256
* Improve URL detection in auto_hyperlinks example by @editor-syntax in https://github.com/MarshalX/atproto/pull/250
* Simplify send_embed example by @MarshalX in https://github.com/MarshalX/atproto/pull/258
* Update lexicons fetched from f023494 committed 2024-01-30T22:19:36Z by @MarshalX in https://github.com/MarshalX/atproto/pull/259
* Delete release workflow by @MarshalX in https://github.com/MarshalX/atproto/pull/252
* Add docs codegen check to GitHub Actions Workflow by @MarshalX in https://github.com/MarshalX/atproto/pull/260

## Version 0.0.38

**26.01.2024**

* Add lexicons updating automation using GitHub Actions by @MarshalX in https://github.com/MarshalX/atproto/pull/248
* Update lexicons fetched from 8994d36 committed 2024-01-25T20:16:30Z by @MarshalX in https://github.com/MarshalX/atproto/pull/249
* Update code snippet in README by @MarshalX in https://github.com/MarshalX/atproto/pull/245
* Fix input data mutation in DotDict by @MarshalX in https://github.com/MarshalX/atproto/pull/246
* Fix links to documentation by @MarshalX in https://github.com/MarshalX/atproto/pull/244

## Version 0.0.37

**12.01.2024**

🎉 Welcome in 2024! User-specific custom feeds are here! This is a massive update with a lot of new implementations including Service JWT, signature validation, DID Keys, AtProtoData, and more! Huge docs restructuring is here too: https://atproto.blue

Code snippet: [Authorized Custom Feed (user-specific results) ](https://github.com/MarshalX/bluesky-feed-generator/pull/10)

SDK:
* Implement Service JWT by @MarshalX in https://github.com/MarshalX/atproto/pull/225
* Implement AtprotoData and DID key formatting and parsing by @MarshalX in https://github.com/MarshalX/atproto/pull/227
* Implement signature verification by @MarshalX in https://github.com/MarshalX/atproto/pull/232
* Add tests for auth flow in custom feeds by @MarshalX in https://github.com/MarshalX/atproto/pull/236
* Describe JWT payload according to RFC 7519 by @MarshalX in https://github.com/MarshalX/atproto/pull/235
* Update lexicons fetched from 51fcba7 committed 2024-01-09T23:29:07Z by @MarshalX in https://github.com/MarshalX/atproto/pull/238
* Fix AtUri hostname parsing with digits by @MarshalX in https://github.com/MarshalX/atproto/pull/229

Docs:
* Enable pydocstyle rules by @MarshalX in https://github.com/MarshalX/atproto/pull/226
* Cleanup docs of models by disabling aliases, schemes, validators, and list of fields by @MarshalX in https://github.com/MarshalX/atproto/pull/231
* Improve documentation by @MarshalX in https://github.com/MarshalX/atproto/pull/234
* Bump jinja2 from 3.1.2 to 3.1.3 by @dependabot in https://github.com/MarshalX/atproto/pull/230

## Version 0.0.36

**23.12.2023**

The AT Protocol Identity package has been implemented! 
It allows the resolution of DIDs and Handles using various techniques like DNS, HTTP, and PLC directory. 
Abstract and in-memory caching has been brought too. 
And as always, it provides both sync and async interfaces.
Check the docs below!

**🌐 [Identity resolvers for DID and Handle](https://atproto.blue/en/latest/atproto_identity/index.html)**

## Version 0.0.35

**21.12.2023**

**❗Breaking changes:** SDK was split into many packages. This affects imports in your codebase. [Read more](https://atproto.blue/en/latest/readme.content.html#sdk-structure)

* New SDK structure by @MarshalX in https://github.com/MarshalX/atproto/pull/214 and https://github.com/MarshalX/atproto/pull/216
* Fix decoding of CAR root by @MarshalX in https://github.com/MarshalX/atproto/pull/213
* Fix parsing of BlobRef in CBOR by @MarshalX in https://github.com/MarshalX/atproto/pull/215
* Update lexicons fetched from 905743d committed 2023-12-20T14:49:21Z by @MarshalX in https://github.com/MarshalX/atproto/pull/217

## Version 0.0.34

**17.12.2023**

* Make SDK more backward and forward-compatible with protocol by @MarshalX in https://github.com/MarshalX/atproto/pull/207
* Add plenty of new high-level methods by @MarshalX in https://github.com/MarshalX/atproto/pull/208
  * Breaking changes:
    * `unlike` now accepts AT URI instead of `record_key` and `profile_identify`
  * New methods:
    * `get_post`
    * `get_posts`
    * `get_post_thread`
    * `get_likes`
    * `get_reposted_by`
    * `get_timeline`
    * `get_author_feed`
    * `unrepost` AKA `delete_report`
    * `follow`
    * `unfollow` AKA `delete_follow`
    * `get_follows`
    * `get_followers`
    * `get_profile`
    * `get_profiles`
    * `mute`
    * `unmute`
    * `resolve_handle`
    * `update_handle`
    * `upload_blob`
* Migrate lexicon parser from dacite to pydantic; enable ruff ANN by @MarshalX in https://github.com/MarshalX/atproto/pull/206
  * Removed exceptions:
    * `UnknownPrimitiveTypeError`
    * `UnknownDefinitionTypeError`
  * Renamed fields:
    * `schema` -> `schema_`
    * `maxLength` -> `max_length`
    * ... and all other camelCase names now in snake_case

## Version 0.0.33

**13.12.2023**

* Update lexicons fetched from 0c54951 committed 2023-12-12T21:37:06Z by @MarshalX in https://github.com/MarshalX/atproto/pull/202
* Update changelog for v0.0.32 by @MarshalX in https://github.com/MarshalX/atproto/pull/199

## Version 0.0.32

**11.12.2023**

* Add text builder as helper for constructing rich text by @MarshalX in https://github.com/MarshalX/atproto/pull/194
* Lock dependencies by major version only by @MarshalX in https://github.com/MarshalX/atproto/pull/195
* Fix parsing of lexicon procedure parameters by @MarshalX in https://github.com/MarshalX/atproto/pull/196
* Update lexicons fetched from ffe39aa committed 2023-12-08T21:32:06Z by @MarshalX in https://github.com/MarshalX/atproto/pull/197
* Update code snippets in README by @MarshalX in https://github.com/MarshalX/atproto/pull/198
* Update changelog for v0.0.31 by @MarshalX in https://github.com/MarshalX/atproto/pull/191

## Version 0.0.31

**02.12.2023**

* Migrate firehose to new relay URI by @MarshalX in https://github.com/MarshalX/atproto/pull/190
* Update lexicons fetched from 8d9b1f7 committed 2023-12-01T20:28:54Z by @MarshalX in https://github.com/MarshalX/atproto/pull/189
* Update changelog for v0.0.30 by @MarshalX in https://github.com/MarshalX/atproto/pull/184

## Version 0.0.30

**06.11.2023**

* Add Python 3.12; migrate from black to ruff format by @MarshalX in https://github.com/MarshalX/atproto/pull/177
* Async Firehose Client: block on make message handler call, add on error callback by @DXsmiley in https://github.com/MarshalX/atproto/pull/157
* Downgrade sphinxext-opengraph to clean up the tree of dependencies (including vulnerable) by @MarshalX in https://github.com/MarshalX/atproto/pull/179
* Update lexicons fetched from 46b108c committed 2023-10-26T22:29:51Z by @MarshalX in https://github.com/MarshalX/atproto/pull/178
* Update lexicons fetched from 772736a committed 2023-11-02T20:16:26Z by @MarshalX in https://github.com/MarshalX/atproto/pull/182
* Update changelog for v0.0.29 by @MarshalX in https://github.com/MarshalX/atproto/pull/173
* Fix type hint of OnMessageCallback (Firehose client) by @MarshalX in https://github.com/MarshalX/atproto/pull/183
* Fix dependency groups by @MarshalX in https://github.com/MarshalX/atproto/pull/180

## Version 0.0.29

**28.09.2023**

* Make codegen deterministic by @DXsmiley in https://github.com/MarshalX/atproto/pull/162
* Add TypedDict for params and data arguments; add type hint for kwargs by @DXsmiley in https://github.com/MarshalX/atproto/pull/166
* Update lexicons fetched from 41ee177 committed 2023-09-27T21:08:58Z by @MarshalX in https://github.com/MarshalX/atproto/pull/172
* Update changelog for v0.0.28 by @MarshalX in https://github.com/MarshalX/atproto/pull/156

## Version 0.0.28

**16.09.2023**

* Add `update_params` method to firehose clients to fix utilizing the old state on reconnecting by @MarshalX in https://github.com/MarshalX/atproto/pull/149
* Add the ability to export and import session string by @MarshalX in https://github.com/MarshalX/atproto/pull/154
* Add the ability to pass `base_uri` to Firehose clients by @MarshalX in https://github.com/MarshalX/atproto/pull/155
* Update lexicons fetched from 9879ca9 committed 2023-09-14T20:24:48Z by @MarshalX in https://github.com/MarshalX/atproto/pull/150
* Update changelog for v0.0.27 by @MarshalX in https://github.com/MarshalX/atproto/pull/146

## Version 0.0.27

**13.09.2023**

* Add reposts support to the firehose process commits example by @MarshalX in https://github.com/MarshalX/atproto/pull/140
* Add snake to camel and camel to snake case conversion support for DotDict wrapper by @MarshalX in https://github.com/MarshalX/atproto/pull/143
* Update lexicons fetched from 07bb0da committed 2023-09-12T17:37:57Z by @MarshalX in https://github.com/MarshalX/atproto/pull/144
* Update dependencies by @MarshalX in https://github.com/MarshalX/atproto/pull/145

## Version 0.0.26

**08.09.2023**

All models have been migrated to Pydantic v2. 
Fields constraints have been added. 
Decoding of DAG-CBOR, CID and CAR files has been migrated to the brand-new library [libipld](https://github.com/MarshalX/python-libipld).
This library is powered by Rust and is much faster than the previous implementation. 
Pydantic v2 also uses Rust in the core. 
This leads to a significant performance boost.

Firehose catch up benchmark:
- The previous SDK version: 700 commits in 5 seconds.
- After migration to Pydantic v2: 2650 commits in 5 seconds.
- After migration to [libipld](https://github.com/MarshalX/python-libipld): **20000 commits in 5 seconds**.
- Using pydantic v2 and [libipld](https://github.com/MarshalX/python-libipld) with multiprocessing: **30000 commits in 5 seconds**.

The new release gives a **40x performance boost**! But the cost is a lot of breaking changes.

Example of firehose consumer with multiprocessing: [process_commits.py](https://github.com/MarshalX/atproto/blob/main/examples/firehose/process_commits.py)

_Test stand for benchmarks: MacBook Pro 2021, Apple M1 Pro, 32 GB RAM, 450mbps connection speed, Python 3.8_

**❗Breaking changes**
- Python 3.7.0 has been dropped. The minimum supported version is now **Python 3.7.1**.
- Camel cased fields are gone. Use snake case instead. For example, `createdAt` is now `created_at`.
- Root namespace has been fixed from `bsky` to `app`. For example, `Client().bsky.feed.get_likes` is now `Client().app.bsky.feed.get_likes`.
- Using similar model instances as strong refs is not allowed anymore. Use `models.create_strong_ref` helper function to convert refs ([example](https://github.com/MarshalX/atproto/blob/e20b8072f383628ea1a5ff306fc8625e1adf4072/examples/like_post.py#L11)).
- Creating model instances using positional arguments is no longer supported. Use keyword arguments instead. For example, thant's not possible anymore `models.ComAtprotoIdentityResolveHandle.Params('marshal.dev')`. Use `models.ComAtprotoIdentityResolveHandle.Params(handle='marshal.dev')` instead.
- Fields that conflict with reserved Pydantic names has _ (underscore) suffix. For example, `validation` is now `validation_`.
- `DotDict` has been moved to `models.dot_dict`.
- Inheritance of base models has been changed. Please check new base classes.
- Inheritance of `DotDict` has been changed. Please check the new base class.
- `BlobRef` model doesn't contain `to_dict()` method anymore.
- `CID` class has been reimplemented using [libipld](https://github.com/MarshalX/python-libipld) lib. It supports much less API.
- `_type` field of models has been renamed to `py_type`. Now it's constant.
- `leb128` module has been removed.
- Type hint of `CID` has been changed to `CIDType`.
- Type hint of `DotDict` has been changed to `DotDictType`.
- `multiformats` and `dag-cbor` dependencies have been removed.
- These reference classes have been removed:
    - `ResponseRef` from `get_profile`. Use `models.AppBskyActorDefs.ProfileViewDetailed` instead.
    - `ResponseRef` from `get_moderation_action`. Use `models.ComAtprotoAdminDefs.ActionViewDetail` instead.
    - `ResponseRef` from `get_moderation_report`. Use `models.ComAtprotoAdminDefs.ReportViewDetail` instead.
    - `ResponseRef` from `get_record`. Use `models.ComAtprotoAdminDefs.RecordViewDetail` instead.
    - `ResponseRef` from `get_repo`. Use `models.ComAtprotoAdminDefs.RepoViewDetail` instead.
    - `ResponseRef` from `resolve_moderation_reports`. Use `models.ComAtprotoAdminDefs.ActionView` instead.
    - `ResponseRef` from `reverse_moderation_action`. Use `models.ComAtprotoAdminDefs.ActionView` instead.
    - `ResponseRef` from `take_moderation_action`. Use `models.ComAtprotoAdminDefs.ActionView` instead.
    - `ResponseRef` from `create_app_password`. Use `models.ComAtprotoServerCreateAppPassword.AppPassword` instead.
- These exceptions have been removed: 
  - `UnexpectedFieldError`. Use `ModelError` instead.
  - `MissingValueError`. Use `ModelError` instead.
  - `ModelFieldError`. Use `ModelError` instead.
  - `WrongTypeError`. Use `ModelError` instead.
  - `CBORDecodingError`. Use `DAGCBORDecodingError` instead.

**New Features**
- Unit tests for model serialization and deserialization.
- Nested dictionaries support in `DotDict` models.
- `DotDict` models now support `__getitem__` and `__setitem__` methods.
- `create_strong_ref` helper function to convert ref-like models to strong refs.
- Fields constraints for models. Now you can see the max items count for the image array, max string length, etc.
- Better documentation of models.

**Minor Changes**
- Fixed nesting of `DotDict` models.
- Fixed serialization of `Union` types.
- Fixed serialization of `Literal` types.
- Fixed sending proper datetime values to the server.
- Fixed printing tracebacks in the Firehose async client.
- Fixed chaining of firehose exceptions.
- Fixed locked and outdated `typing-extensions` dependency.
- Fixed passing of arguments to `ClientBase`.

## Version 0.0.25

**30.08.2023**

🔥 Bsky made breaking changes in models of firehose. This release fixes it
* Update changelog for v0.0.24 by @MarshalX in https://github.com/MarshalX/atproto/pull/126
* Update lexicons fetched from ad1fcf1 committed 2023-08-30T00:07:21Z by @MarshalX in https://github.com/MarshalX/atproto/pull/131

## Version 0.0.24

**15.08.2023**

* Add update profile example by @MarshalX in https://github.com/MarshalX/atproto/pull/120
* Add automatic link (facet) detection example by @Jxck-S in https://github.com/MarshalX/atproto/pull/122
* Update changelog for v0.0.23 by @MarshalX in https://github.com/MarshalX/atproto/pull/117
* Update changelog by @MarshalX in https://github.com/MarshalX/atproto/pull/118
* Update lexicons fetched from 244bf46 committed 2023-08-10T20:54:24Z by @MarshalX in https://github.com/MarshalX/atproto/pull/124
* Update packages; fix CVE-2023-37920 (certifi) by @MarshalX in https://github.com/MarshalX/atproto/pull/125
* Fix update profile example by @IamC8 in https://github.com/MarshalX/atproto/pull/121

## Version 0.0.23

**23.07.2023**

* ❗ Delete get_or_create_model method (backward incompatible) by @MarshalX in https://github.com/MarshalX/atproto/pull/111
* Add documentation for base models by @MarshalX in https://github.com/MarshalX/atproto/pull/109
* Add import aliases for "models.utils" by @MarshalX in https://github.com/MarshalX/atproto/pull/111
* Add str and repr for BlobRef by @MarshalX in https://github.com/MarshalX/atproto/pull/113
* Add Firehose process commits example by @MarshalX in https://github.com/MarshalX/atproto/pull/114
* Implement additional magic methods for DotDict by @MarshalX in https://github.com/MarshalX/atproto/pull/109
* Make languages constants immutable by @MarshalX in https://github.com/MarshalX/atproto/pull/110
* Fix get_model_as_dict for DotDict by @MarshalX in https://github.com/MarshalX/atproto/pull/111
* Fix is_record_type for DotDict models by @MarshalX in https://github.com/MarshalX/atproto/pull/112
* Fix access to unknown fields in DotDict by @MarshalX in https://github.com/MarshalX/atproto/pull/116
* Update changelog for v0.0.21 by @MarshalX in https://github.com/MarshalX/atproto/pull/108

## Version 0.0.22

**23.07.2023**

release has been yanked

## Version 0.0.21

**21.07.2023**

* Add dot notation for dictionaries by @MarshalX in https://github.com/MarshalX/atproto/pull/106
* Fix unknown type that could be plain dictionary by @MarshalX in https://github.com/MarshalX/atproto/pull/105
* Fix parsing of custom (extended) records by @MarshalX in https://github.com/MarshalX/atproto/pull/106
* Fix a small typo in `README.md` by @ndrezn in https://github.com/MarshalX/atproto/pull/104
* Update lexicons fetched from b2ef386 committed 2023-07-20T16:00:51Z by @MarshalX in https://github.com/MarshalX/atproto/pull/107
* Update changelog for v0.0.20 by @MarshalX in https://github.com/MarshalX/atproto/pull/103

## Version 0.0.20

**19.07.2023**

* Update changelog for v0.0.19 by @MarshalX in https://github.com/MarshalX/atproto/pull/99
* Add pagination example using cursors by @ymdpharm in https://github.com/MarshalX/atproto/pull/93
* Migrate to websockets lib (fixed all known issues with lost firehouse frames, reconnections and crashes) by @MarshalX in https://github.com/MarshalX/atproto/pull/101

## Version 0.0.19

**18.07.2023**

* Update changelog for v0.0.18 by @MarshalX in https://github.com/MarshalX/atproto/pull/92
* Add posts langs support by @MarshalX in https://github.com/MarshalX/atproto/pull/96
* Fix infinite loop of reconnections to Firehose by @MarshalX in https://github.com/MarshalX/atproto/pull/97
* Update lexicons fetched from 775944e committed 2023-07-17T23:06:44Z by @MarshalX in https://github.com/MarshalX/atproto/pull/98

## Version 0.0.18

**16.07.2023**

* Update changelog for v0.0.17 by @MarshalX in https://github.com/MarshalX/atproto/pull/86
* Fix is_record_type for dict record types by @joelghill in https://github.com/MarshalX/atproto/pull/88
* Lower version of typing-extensions as possible; update ruff by @MarshalX in https://github.com/MarshalX/atproto/pull/90
* Update lexicons fetched from b9ca76f committed 2023-07-14T23:05:56Z by @MarshalX in https://github.com/MarshalX/atproto/pull/91

## Version 0.0.17

**06.07.2023**

* Update changelog for v0.0.16 by @MarshalX in https://github.com/MarshalX/atproto/pull/82
* Move the websocket client into part of the atproto package by @MarshalX in https://github.com/MarshalX/atproto/pull/84
* Update lexicons fetched from e7a0d27 committed 2023-07-03T16:28:39Z by @MarshalX in https://github.com/MarshalX/atproto/pull/85

## Version 0.0.16

**01.07.2023**

* Update changelog for v0.0.15 by @MarshalX in https://github.com/MarshalX/atproto/pull/77
* Update lexicons fetched from 0306f81 committed 2023-06-23T20:30:52Z by @MarshalX in https://github.com/MarshalX/atproto/pull/79
* Lock ruff version in GHA workflow by @MarshalX in https://github.com/MarshalX/atproto/pull/81

## Version 0.0.15

**23.06.2023**

* Update changelog for v0.0.14 by @MarshalX in https://github.com/MarshalX/atproto/pull/70
* Update Cimon by @MarshalX in https://github.com/MarshalX/atproto/pull/71
* Update lexicons fetched from 84032a6 committed 2023-06-12T21:51:38Z by @MarshalX in https://github.com/MarshalX/atproto/pull/72
* Update Ruff; make _MANDATORY_HEADERS private; fix issues by @MarshalX in https://github.com/MarshalX/atproto/pull/73
* Disable Cimon fail-on-error flag by @MarshalX in https://github.com/MarshalX/atproto/pull/74
* Update lexicons fetched from 2768fb9 committed 2023-06-20T14:36:09Z by @MarshalX in https://github.com/MarshalX/atproto/pull/75
* Fix dynamic versioning build backend by @MarshalX in https://github.com/MarshalX/atproto/pull/76

## Version 0.0.14

**10.06.2023**

* Update changelog for v0.0.13 by @MarshalX in https://github.com/MarshalX/atproto/pull/60
* Add Cimon in Detect Mode by @MarshalX in https://github.com/MarshalX/atproto/pull/63
* Enable Cimon Prevent Mode by @MarshalX in https://github.com/MarshalX/atproto/pull/64
* Add send_embed example by @MarshalX in https://github.com/MarshalX/atproto/pull/66
* Update README by @MarshalX in https://github.com/MarshalX/atproto/pull/67
* Update lexicons fetched from 8857fb0 committed 2023-06-09T13:21:09Z by @MarshalX in https://github.com/MarshalX/atproto/pull/68
* Bump requests from 2.30.0 to 2.31.0 by @dependabot in https://github.com/MarshalX/atproto/pull/69

## Version 0.0.13

**03.06.2023**

* Update changelog for v0.0.12 by @MarshalX in https://github.com/MarshalX/atproto/pull/58
* Update lexicons (add admin.rebaseRepo) fetched from 4a6c976 committed 2023-05-30T15:50:46Z by @MarshalX in https://github.com/MarshalX/atproto/pull/59

## Version 0.0.12

**01.06.2023**

* Update changelog for v0.0.11 by @MarshalX in https://github.com/MarshalX/atproto/pull/55
* Add mypy; fix types; fix error handling of requests by @MarshalX in https://github.com/MarshalX/atproto/pull/56
* Increase max message size in Firehose by @MarshalX in https://github.com/MarshalX/atproto/pull/57

## Version 0.0.11

**30.05.2023**

* Update changelog for v0.0.10 by @MarshalX in https://github.com/MarshalX/atproto/pull/52
* Keep Firehose open on invalid CBOR or DAG-CBOR by @MarshalX in https://github.com/MarshalX/atproto/pull/54

## Version 0.0.10

**27.05.2023**

* Update changelog for v0.0.9 by @MarshalX in https://github.com/MarshalX/atproto/pull/42
* Add CLI for codegen by @MarshalX in https://github.com/MarshalX/atproto/pull/43
* Update lexicons fetched from 743eaf1 committed 2023-05-26T00:04:10Z by @MarshalX in https://github.com/MarshalX/atproto/pull/44
* Add Ruff; init tests; fix code style and type hints by @MarshalX in https://github.com/MarshalX/atproto/pull/45
* Move docs dependencies to separated group by @MarshalX in https://github.com/MarshalX/atproto/pull/46
* Fix Ruff for root dir by @MarshalX in https://github.com/MarshalX/atproto/pull/48
* Update lexicons fetched from c62964b committed 2023-05-26T00:22:05Z by @MarshalX in https://github.com/MarshalX/atproto/pull/49
* Fix .gitignore by @MarshalX in https://github.com/MarshalX/atproto/pull/50
* Custom feed generators by @MarshalX in https://github.com/MarshalX/atproto/pull/47
* Fix firehose params by @MarshalX in https://github.com/MarshalX/atproto/pull/51

## Version 0.0.9

**25.05.2023**

* Update changelog for v0.0.8 by @MarshalX in https://github.com/MarshalX/atproto/pull/39
* Add "delete_post" and "repost" methods by @codybraun in https://github.com/MarshalX/atproto/pull/40
* Fix request error handling by @MarshalX in https://github.com/MarshalX/atproto/pull/41

## Version 0.0.8

**23.05.2023**

* update changelog for v0.0.7 by @MarshalX in https://github.com/MarshalX/atproto/pull/34
* Fix duplication of field descriptions in docs by @MarshalX in https://github.com/MarshalX/atproto/pull/35
* Add support for custom feeds. Update lexicons fetched from d661a60 committed 2023-05-23T05:02:36Z by @MarshalX in https://github.com/MarshalX/atproto/pull/36
* Add Firehose (data streaming) by @MarshalX in https://github.com/MarshalX/atproto/pull/31
* Add forgotten models by @MarshalX in https://github.com/MarshalX/atproto/pull/37
* Fix link format in docs by @MarshalX in https://github.com/MarshalX/atproto/pull/38

## Version 0.0.7

**20.05.2023**

* update changelog for v0.0.6 by @MarshalX in https://github.com/MarshalX/atproto/pull/29
* Update docs by @MarshalX in https://github.com/MarshalX/atproto/pull/30
* Short typing import by @MarshalX in https://github.com/MarshalX/atproto/pull/32
* Fix session refreshing by @MarshalX in https://github.com/MarshalX/atproto/pull/33

## Version 0.0.6

**19.05.2023**

* update changelog for v0.0.5 by @MarshalX in https://github.com/MarshalX/atproto/pull/24
* Update docs domain; improve open graph by @MarshalX in https://github.com/MarshalX/atproto/pull/25
* Don't lock dependencies so strictly; add pyjwt by @MarshalX in https://github.com/MarshalX/atproto/pull/26
* Add session refreshing by @MarshalX in https://github.com/MarshalX/atproto/pull/27
* Update lexicons fetched from cf36b36 committed 2023-05-18T22:57:59Z by @MarshalX in https://github.com/MarshalX/atproto/pull/28

## Version 0.0.5

**17.05.2023**

* update changelog for v0.0.4 by @MarshalX in https://github.com/MarshalX/atproto/pull/14
* Add CAR files support by @MarshalX in https://github.com/MarshalX/atproto/pull/17
* Update lexicons fetched from 1cbffd6 committed 2023-05-12T21:45:15Z (lists, mute lists preferences, repo rebase, and more), by @MarshalX in https://github.com/MarshalX/atproto/pull/18
* Fix spacing in examples by @prtolem in https://github.com/MarshalX/atproto/pull/16
* bump version by @MarshalX in https://github.com/MarshalX/atproto/pull/19
* Add PyPI publishing to release workflow by @MarshalX in https://github.com/MarshalX/atproto/pull/21
* Dynamic versioning from Git Tags by @MarshalX in https://github.com/MarshalX/atproto/pull/22
* fix creating of GitHub Release by @MarshalX in https://github.com/MarshalX/atproto/pull/23

## Version 0.0.4

**12.05.2023**

* update changes for 0.0.3 by @MarshalX in https://github.com/MarshalX/atproto/pull/10
* Update logo by @MarshalX in https://github.com/MarshalX/atproto/pull/11
* add example with rich text; fix generation of system type field by @MarshalX in https://github.com/MarshalX/atproto/pull/13
* fix sending of facets

## Version 0.0.3

**08.05.2023**

* add GHA workflow to create release on tag creation by @roj1512 in https://github.com/MarshalX/atproto/pull/1
* Add notifications example by @MarshalX in https://github.com/MarshalX/atproto/pull/2
* simplify and fix process_notifications example by @MarshalX in https://github.com/MarshalX/atproto/pull/4
* add ability to access to model's fields by [] by @MarshalX in https://github.com/MarshalX/atproto/pull/5
* add deserialization of records by @MarshalX in https://github.com/MarshalX/atproto/pull/6
* add home_timeline and profile_posts examples by @MarshalX in https://github.com/MarshalX/atproto/pull/7
* publish package with OpenID Connect by @MarshalX in https://github.com/MarshalX/atproto/pull/8
* bump version to 0.0.3 by @MarshalX in https://github.com/MarshalX/atproto/pull/9

## Version 0.0.2

**06.05.2023**

The first public release.
