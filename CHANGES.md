# Change Log

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
