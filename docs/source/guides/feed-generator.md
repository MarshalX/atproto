# Building a feed generator

A feed generator is a service you run that answers one question: *given a cursor and a limit, which posts belong in this feed?* Bluesky calls your endpoint, you return a list of post URIs, and the app hydrates and renders them. You never serve post content, only an ordering.

This is the most complete thing you can build with this SDK, and the only place that uses all of it at once: the firehose to ingest, `atproto_core` to decode commits, `atproto_client` to publish the feed record, and `atproto_server` plus `atproto_identity` to authenticate inbound requests.

:::{tip}
There is a complete, working implementation to clone and modify: [MarshalX/bluesky-feed-generator](https://github.com/MarshalX/bluesky-feed-generator). Everything below walks through how it works. Read [the protocol-level overview](https://github.com/bluesky-social/feed-generator#overview) for the parts that are not Python.
:::

## The four pieces

1. **Ingest.** Subscribe to the firehose, decode commits, keep the posts you care about.
2. **Serve.** Answer `app.bsky.feed.getFeedSkeleton` with URIs and a cursor.
3. **Identify.** Publish a DID document so the network knows who you are, and optionally verify the tokens it sends you.
4. **Publish.** Write an `app.bsky.feed.generator` record to your own repository so the feed appears in the app.

## 1. Ingest from the firehose

The firehose delivers signed commits. Each carries a CAR file of blocks, and each operation in the commit names a CID you look up in those blocks to get the record.

```python
from atproto import CAR, AtUri, models

_INTERESTED_RECORDS = {
    models.AppBskyFeedLike: models.ids.AppBskyFeedLike,
    models.AppBskyFeedPost: models.ids.AppBskyFeedPost,
    models.AppBskyGraphFollow: models.ids.AppBskyGraphFollow,
}


def _get_ops_by_type(commit: models.ComAtprotoSyncSubscribeRepos.Commit) -> defaultdict:
    operation_by_type = defaultdict(lambda: {'created': [], 'deleted': []})

    car = CAR.from_bytes(commit.blocks)
    for op in commit.ops:
        uri = AtUri.from_str(f'at://{commit.repo}/{op.path}')

        if op.action == 'create':
            record_raw_data = car.blocks.get(op.cid)
            if not record_raw_data:
                continue

            record = models.get_or_create(record_raw_data, strict=False)
            if record is None:  # unknown record, outside the bsky lexicons
                continue

            for record_type, record_nsid in _INTERESTED_RECORDS.items():
                if uri.collection == record_nsid and models.is_record_type(record, record_type):
                    operation_by_type[record_nsid]['created'].append(
                        {'record': record, 'uri': str(uri), 'cid': str(op.cid), 'author': commit.repo}
                    )
                    break

        if op.action == 'delete':
            operation_by_type[uri.collection]['deleted'].append({'uri': str(uri)})

    return operation_by_type
```

Three SDK details are doing the work here:

[CAR.from_bytes](#atproto_core.car.car.CAR)
: Decodes the commit's block store. `car.blocks` maps CID to raw record data.

[get_or_create](#atproto_client.models.utils.get_or_create) with `strict=False`
: Turns raw block data into a model, resolving the class from the record's `$type`. `strict=False` matters: the firehose carries every lexicon on the network, including ones this SDK has never heard of, and strict mode would raise on them. Records you do not know degrade to a [DotDict](#atproto_client.models.dot_dict.DotDict) instead of taking your process down.

[is_record_type](#atproto_client.models.utils.is_record_type)
: Narrows the type after the fact. The collection check alone is not enough: a record's path says what it claims to be, its `$type` says what it is.

See [Firehose](firehose.md) for the subscription itself, and [Working with models](models.md) for the model machinery.

:::{tip}
If you do not need cryptographic verifiability, [Jetstream](jetstream.md) delivers the same events as plain JSON with server-side filtering and no CAR decoding. It is substantially less code and less CPU. Use the firehose when you need to verify what you received.
:::

### Persist the cursor

A feed generator that restarts should not re-ingest from the beginning, and should not skip what it missed. The firehose sequence number is your cursor. Store it periodically and pass it back on reconnect:

```python
def _run(name, operations_callback, stream_stop_event=None):
    state = SubscriptionState.get_or_none(SubscriptionState.service == name)

    params = None
    if state:
        params = models.ComAtprotoSyncSubscribeRepos.Params(cursor=state.cursor)

    client = FirehoseSubscribeReposClient(params)

    def on_message_handler(message: firehose_models.MessageFrame) -> None:
        commit = parse_subscribe_repos_message(message)
        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            return

        # every ~1k events; more often than this costs more than it saves
        if commit.seq % 1000 == 0:
            client.update_params(models.ComAtprotoSyncSubscribeRepos.Params(cursor=commit.seq))
            SubscriptionState.update(cursor=commit.seq).where(SubscriptionState.service == name).execute()

        if not commit.blocks:
            return

        operations_callback(_get_ops_by_type(commit))

    client.start(on_message_handler)
```

`update_params` changes what the client reconnects with, so an automatic reconnect resumes from the stored sequence rather than from the live tip.

:::{warning}
Wrap `client.start(...)` in a loop that catches `FirehoseError` and reconnects. A stream that runs for weeks will disconnect.
:::

### Filter

Everything past this point is your algorithm. The reference implementation keeps posts whose text mentions "python":

```python
for created_post in ops[models.ids.AppBskyFeedPost]['created']:
    record = created_post['record']
    if 'python' in record.text.lower():
        posts_to_create.append({'uri': created_post['uri'], 'cid': created_post['cid']})
```

Two things worth handling that are easy to forget:

- **Process deletions.** If you only ever insert, your feed will serve URIs for posts that no longer exist.
- **Consider backdated posts.** Accounts importing their history from elsewhere can flood a feed with old content. The reference implementation compares `record.created_at` against a threshold and optionally drops them.

## 2. Serve the skeleton

Your service needs three HTTP endpoints. Any framework will do; the reference implementation uses Flask.

`GET /xrpc/app.bsky.feed.getFeedSkeleton`
: The feed itself. Takes `feed`, `cursor` and `limit` query parameters, returns `{'cursor': ..., 'feed': [{'post': uri}, ...]}`.

`GET /xrpc/app.bsky.feed.describeFeedGenerator`
: Declares which feeds this service hosts.

`GET /.well-known/did.json`
: Your DID document, if you use a `did:web` identity.

The skeleton response is only URIs. Bluesky hydrates them:

```python
@app.route('/xrpc/app.bsky.feed.getFeedSkeleton', methods=['GET'])
def get_feed_skeleton():
    feed = request.args.get('feed', default=None, type=str)
    algo = algos.get(feed)
    if not algo:
        return 'Unsupported algorithm', 400

    try:
        cursor = request.args.get('cursor', default=None, type=str)
        limit = request.args.get('limit', default=20, type=int)
        body = algo(cursor, limit)
    except ValueError:
        return 'Malformed cursor', 400

    return jsonify(body)
```

Your cursor is yours to define, and only has to be opaque and stable. The reference implementation encodes the last post's index time and CID as `{timestamp}::{cid}`, which makes paging a stable keyset query rather than an offset.

## 3. Verify inbound requests

If your feed is personalised, you need to know who is asking. Bluesky sends a **service auth JWT** in the `Authorization` header, signed by the requesting user's key.

This is where `atproto_server` and `atproto_identity` come in:

```python
from atproto import DidInMemoryCache, IdResolver, verify_jwt
from atproto.exceptions import InvalidTokenError

_CACHE = DidInMemoryCache()
_ID_RESOLVER = IdResolver(cache=_CACHE)


def validate_auth(request) -> str:
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthorizationError('Invalid authorization header')

    jwt = auth_header[len('Bearer ') :].strip()

    try:
        # own_did binds the token to this service by checking the "aud" claim
        payload = verify_jwt(jwt, _ID_RESOLVER.did.resolve_atproto_key, own_did=config.SERVICE_DID)
    except InvalidTokenError as e:
        raise AuthorizationError(f'Invalid token: {e}') from e

    # the "lxm" claim binds the token to a single XRPC method
    nsid = request.path.rsplit('/', 1)[-1]
    if getattr(payload, 'lxm', None) != nsid:
        raise AuthorizationError(f'Token is not bound to the "{nsid}" method')

    return payload.iss
```

[verify_jwt](#atproto_server.auth.jwt.verify_jwt) does the cryptography. The second argument is a callable that resolves an issuer DID to its signing key. [IdResolver](#atproto_identity.resolver.IdResolver) provides exactly that as `resolver.did.resolve_atproto_key`.

Three checks matter, and only the first is automatic:

**Signature**
: `verify_jwt` resolves the issuer's key and verifies against it.

**Audience** (`aud`)
: Pass `own_did=` so a token minted for a *different* service cannot be replayed against yours. Omitting this is the common mistake.

**Method** (`lxm`)
: Check it yourself. The claim binds the token to one XRPC method, so a token for `getFeedSkeleton` cannot be used against another endpoint.

`payload.iss` is the requesting user's DID. That is what you personalise on.

:::{important}
Cache DID resolution. Every request would otherwise resolve the issuer's DID document over the network. [DidInMemoryCache](#atproto_identity.cache.in_memory_cache.DidInMemoryCache) is enough for a single process; subclass `DidBaseCache` for something shared. See [Identity](identity.md).
:::

## 4. Publish the feed record

The feed only appears in the app once there is an `app.bsky.feed.generator` record in *your* repository pointing at your service.

```python
from atproto import Client, models

client = Client()
client.login(HANDLE, PASSWORD)

avatar_blob = None
if AVATAR_PATH:
    with open(AVATAR_PATH, 'rb') as f:
        avatar_blob = client.upload_blob(f.read()).blob

response = client.com.atproto.repo.put_record(
    models.ComAtprotoRepoPutRecord.Data(
        repo=client.me.did,
        collection=models.ids.AppBskyFeedGenerator,
        rkey=RECORD_NAME,
        record=models.AppBskyFeedGenerator.Record(
            did=feed_did,  # did:web:<your hostname>, or a did:plc you control
            display_name=DISPLAY_NAME,
            description=DESCRIPTION,
            avatar=avatar_blob,
            accepts_interactions=ACCEPTS_INTERACTIONS,
            created_at=client.get_current_time_iso(),
        ),
    )
)

print('Feed URI:', response.uri)
```

`put_record` rather than `create_record`, because `rkey` is a stable name you chose: running it again updates the feed's display data instead of creating a second feed. That returned URI is what your service matches on in `getFeedSkeleton`.

Deleting that record removes the feed from the network, along with all of its likes.

:::{note}
`did:web:<hostname>` is the easy identity: it needs no registration, just the `/.well-known/did.json` endpoint above. It binds your feed to that domain forever, though. If you expect to migrate domains, use a `did:plc` instead.
:::

## Running it

The firehose subscription and the HTTP server are separate concerns. The reference implementation runs the subscription on a background thread inside the Flask process, which is fine for a single worker.

:::{warning}
If you run multiple workers, run the firehose consumer as its **own process**. Otherwise every worker opens its own subscription and writes the same posts.
:::

Use a production WSGI server rather than Flask's development one.

## Where to go from here

- [Firehose](firehose.md): the subscription API in full, including labels and error handling.
- [Jetstream](jetstream.md): the cheaper ingest path, and archive backfill for bootstrapping.
- [Working with models](models.md): `get_or_create`, `is_record_type`, and `DotDict`.
- [Identity](identity.md): resolvers and caching.
- [Custom lexicons](../cli/custom-lexicons.md): if your service exposes an API of its own.
