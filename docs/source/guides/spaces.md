# Spaces

A space holds records with an access perimeter: bookmarks and drafts that only their owner reads, gated content, private posts, a group forum. The records still live with the accounts that wrote them, each on its own PDS, but apart from the public repository, and they are served only to those the space admits.

The rules are the protocol's, not this SDK's. See the [permissioned data proposal](https://github.com/bluesky-social/proposals/tree/main/0016-permissioned-data).

:::{warning}
Spaces are in alpha. The protocol is not final, and the classes, the methods and the lexicons behind them can change with it in any release. See [Limits](#limits).
:::

## The shape of it

- A **space** is named by its authority, its type and its key, in a URI: `at://<authority>/space/<type>/<skey>`, for example `at://did:plc:abc/space/com.example.forum/general`.
- A **space type** is declared by a lexicon: the type of the key, and the record collections to expect in the spaces of that type.
- The **authority** is the account at the root of the URI. Its PDS is the **host** of the space, which decides who may read it.
- Every account that writes to a space holds its own **repo** in it, on its own PDS. These accounts form the **writer set** of the space.
- Reading the repo of another account takes a **space credential**. The host of the space issues one in exchange for a **delegation token**, which the PDS of the reader mints for the applications that the reader authorized.
- What is read from the repo of another account is verified against a MAC of its host, so a response cannot be forged on the way.

Three classes do the work:

- A [SpaceClient](#atproto_space.SpaceClient) is one space as one account sees it. It reads the space and writes the repo of the account in it.
- A [SpaceManager](#atproto_space.SpaceManager) is for the authority of a space: its policy, its writers and its members.
- A [SpaceReader](#atproto_space.SpaceReader) reads a space for no account in particular. It is what a service that keeps a copy of spaces uses.

```python
from atproto import Client, SpaceClient

client = Client()
client.login_oauth(session)

space = SpaceClient(client, 'at://did:plc:abc/space/com.example.forum/general')
space.create_record({'$type': 'com.example.post', 'text': 'Hello, space!'})

for record in space.all_records():
    print(record.repo, record.collection, record.value)
```

The credentials are requested and renewed for you, every request goes to the server that holds the data, and what comes back is verified.

## Scopes

Access to spaces is granted through `space:` [OAuth scopes](oauth.md#scopes), by space type and authority:

| Scope | Grants |
|---|---|
| `space:com.example.bookmarks` | The user's own bookmarks spaces: read, and write the collections the type declares |
| `space:com.example.forum?authority=*` | Every forum the user is in, under any authority: read, and write the declared collections |
| `space:com.example.forum?authority=*&action=read` | The same forums, read-only |
| `space:com.example.forum?authority=*&action=read_self` | Only the user's own repo in those forums, read-only |
| `space:*?authority=*&action=read_self` | List all of the user's spaces, and read the user's own repo in each |
| `space:com.example.forum?manage=create&manage=update&manage=delete` | The user's own forums: read, write the declared collections, and create, reconfigure and delete the forums themselves |

A `read` grant covers every repo of the space. A `read_self` grant covers only the user's own repo, so it is not enough to get a space credential. Writing a collection that the type does not declare takes `collection=`, and managing a space takes `manage=`.

The PDS resolves the lexicon of every space type that a scope names, all but `*`, when the user authorizes. The type has to be published as a lexicon whose main definition is a `space`, otherwise the authorization fails with `invalid_scope`.

:::{note}
App passwords do not work. A PDS refuses a session that was created with one on every space method, so log in with [OAuth](oauth.md) or with the account password.
:::

## Opening a space

The spaces of an account are listed by its PDS:

```python
response = client.com.atproto.space.list_spaces({'space_type': 'com.example.forum'})
for view in response.spaces:
    print(view.space)
```

Without `space_type` it lists the spaces of every type that the account holds a repo in or is the authority of, and `space_did` narrows the listing to one authority. It is an ordinary paginated query, so [paginate](#atproto_client.utils.pagination.paginate) works on it.

With OAuth the listing is checked against its filters. A grant for one space type needs `space_type`, a grant for the user's own spaces needs `space_did` set to the DID of the account, and a listing without filters needs a grant for every type and authority, such as `space:*?authority=*&action=read_self`.

Open a space by its URI:

```python
from atproto import SpaceClient

space = SpaceClient(client, 'at://did:plc:abc/space/com.example.forum/general')
```

Opening a space makes no request. The space credential is requested when a read first needs it, then kept and renewed shortly before it expires. To learn right away whether the space grants access, call [authorize](#atproto_space.SpaceClient.authorize):

```python
space.authorize()  # raises if the space does not grant access
```

Every `SpaceClient` requests its own credential, so keep one instance per space instead of opening the space again for every use.

### The type of a space

A [SpaceType](#atproto_space.SpaceType) says which records belong in a space. It is optional. With it, the URI must name a space of that type, and the records of other collections are flagged as invalid when you read the space:

```python
from atproto import SpaceClient, SpaceType

forum = SpaceType('com.example.forum', key='any', collections=('com.example.post',))
space = SpaceClient(client, 'at://did:plc:abc/space/com.example.forum/general', forum)
```

If you have the lexicon of the type, build it from that:

```python
from atproto_lexicon.parser import lexicon_parse_file

forum = SpaceType.from_lexicon(lexicon_parse_file('lexicons/com.example.forum.json'))
```

[ref_for](#atproto_space.SpaceType.ref_for) builds the reference to a space of the type from its authority and key. For a type with a literal key, such as `literal:self`, the key can be left out.

## Creating a space

[create_space](#atproto_space.SpaceClient.create_space) creates a space with the account as its authority and returns it, opened:

```python
from atproto import SpaceClient, models

space = SpaceClient.create_space(client, forum, models.ComAtprotoMemberspacePolicy.Main(), skey='general')
print(space.uri)
```

Without `skey`, the key is the literal key of the type, or one that the PDS generates. The policy decides who may read the space and whose writes count. Every PDS supports three:

| Policy | For |
|---|---|
| `models.ComAtprotoPersonalspacePolicy.Main` | Personal data that only the authority and the applications it authorized read |
| `models.ComAtprotoMemberspacePolicy.Main` | A space governed by a member list, see [Managing a space](#managing-a-space) |
| `models.ComAtprotoManagedspacePolicy.Main` | A space whose access decisions are delegated to an application |

## Your own records

Writes always go to the repo of the account. A record is a record model or a dict with `$type`, and its type is the collection it is stored under:

```python
from atproto import AtUri, models
from atproto_client.models.dot_dict import DotDict

created = space.create_record({'$type': 'com.example.post', 'text': 'Hello, space!'})
rkey = AtUri.from_str(created.uri).rkey

space.put_record({'$type': 'com.example.post', 'text': 'Edited'}, rkey)
space.delete_record('com.example.post', rkey)

Create = models.ComAtprotoSpaceApplyWrites.Create
space.apply_writes(
    [
        Create(collection='com.example.post', value=DotDict({'$type': 'com.example.post', 'text': 'First'})),
        Create(collection='com.example.post', value=DotDict({'$type': 'com.example.post', 'text': 'Second'})),
    ]
)
```

[apply_writes](#atproto_space.SpaceClient.apply_writes) applies all of its operations or none. The `value` of an operation is a record model or a [DotDict](#atproto_client.models.dot_dict.DotDict). [clear_records](#atproto_space.SpaceClient.clear_records) deletes every record of the account in the space.

Reads target the repo of the account unless `repo` is given:

```python
for record in space.records(collection='com.example.post'):
    if record.valid:
        print(record.rkey, record.value.text)

post = space.get_record('com.example.post', rkey)
print(post.value.text)
```

[records](#atproto_space.SpaceClient.records) pages through the repo and yields a [SpaceRecord](#atproto_space.SpaceRecord) for each record. Its `value` is the record model when the SDK has one for the collection, and a `DotDict` otherwise. [list_records](#atproto_space.SpaceClient.list_records) returns one page as the PDS sent it.

These reads and writes use the session of the account, so a `read_self` grant is enough to read the account's own repo. These reads ask the PDS for no MAC: a record is taken as the PDS sent it, and a repo read in full is checked against its commit only.

The URI of a record in a space has six parts: the three of the space, then the author, the collection and the record key. [AtUri](#atproto_core.uri.AtUri) reads all of them:

```python
uri = AtUri.from_str(created.uri)

uri.space_did  # the authority of the space
uri.author_did  # the account that the record belongs to
uri.collection  # 'com.example.post'
```

:::{warning}
The record helpers of the namespaces, such as `client.com.atproto.space.policy.create(...)`, write to the public repository, as for [any other record type](records-and-repos.md#record-sugar). Records of a space go through `SpaceClient`.
:::

## Other members' records

Give `repo` to read the repo of another account. This takes a `read` grant:

```python
from atproto import models

for writer in space.writers():
    if not isinstance(writer, models.ComAtprotoSpaceDefs.RepoWrite):
        continue  # the repo was removed from the space

    for record in space.records(writer.repo, 'com.example.post'):
        if record.valid:
            print(writer.repo, record.value.text)
```

[writers](#atproto_space.SpaceClient.writers) iterates over the writer set, as the host of the space knows it. A single record is verified against the MAC of its host:

```python
post = space.get_record('com.example.post', rkey, repo='did:plc:xyz')
```

Listed records are not covered by a MAC. When that matters, read the record with `get_record`, or read the repo in full.

## The whole space

[all_records](#atproto_space.SpaceClient.all_records) reads every repo of the writer set. Each repo is fetched in full and verified, its commit against the MAC of its host and its records against its commit, before its records are yielded:

```python
for record in space.all_records():
    if record.valid:
        print(record.repo, record.collection, record.value)
    else:
        print(record.repo, record.collection, record.error)
```

Every record is yielded, flagged with `valid`. A record is invalid when it is stored under another collection than its `$type`, when the type of the space does not declare its collection, or when it does not match the model of its collection. The reason is in `error`. Records are checked by the client, because not every host enforces the type of a space.

The value of a record whose collection has no model is as decoded from DAG-CBOR, so a link is a [CID](#atproto_core.cid.CID) and bytes are `bytes`. [records](#atproto_space.SpaceClient.records) yields such a value in the JSON form, as it was listed.

Repos that are not found, taken down, suspended or deactivated are skipped.

## Blobs

A blob is uploaded as usual and referred to from a record of the space. With OAuth the upload takes a `blob:` [scope](oauth.md#scopes) next to the `space:` one, for example `atproto space:com.example.forum?authority=* blob:image/*`:

```python
blob = client.upload_blob(image).blob
space.create_record({'$type': 'com.example.post', 'text': 'With an image', 'image': blob})
```

It is fetched from the repo that refers to it, and verified against its CID. [list_blobs](#atproto_space.SpaceClient.list_blobs) lists the CIDs of the blobs that the records of a repo refer to:

```python
for cid in space.list_blobs('did:plc:xyz').cids:
    data = space.get_blob(cid, 'did:plc:xyz')
```

The CID of a blob reference is `str(blob.cid)`. A record whose collection has no model holds the reference as a [DotDict](#atproto_client.models.dot_dict.DotDict), which has no `cid`, so build the [BlobRef](#atproto_client.models.blob_ref.BlobRef) from it first:

```python
from atproto_client.models.blob_ref import BlobRef

for record in space.records('did:plc:xyz', 'com.example.post'):
    image = BlobRef.model_validate(record.value.image.to_dict())
    data = space.get_blob(str(image.cid), record.repo)
```

## Managing a space

The authority of a space manages it with a [SpaceManager](#atproto_space.SpaceManager). The client must be logged in as the account that the URI names, with a `manage` grant on the space:

```python
from atproto import SpaceManager, models

manager = SpaceManager(client, space.uri)

policy = manager.get_space().policy
manager.remove_writer('did:plc:xyz')
```

[remove_writer](#atproto_space.SpaceManager.remove_writer) takes a repo out of the writer set. The repo is added back when its account writes to the space again and the policy lets it. [delete_space](#atproto_space.SpaceManager.delete_space) deletes the space along with the repo of the authority in it. The repos of other accounts are left where they are.

A space with the member list policy has members, each with the right to read, to write, or both:

```python
Member = models.ComAtprotoMemberspaceDefs.Member

manager.put_members([Member(did='did:plc:xyz', read=True, write=True)])

for member in manager.members():
    print(member.did, member.read, member.write)

manager.remove_members(['did:plc:xyz'])
```

[update_space](#atproto_space.SpaceManager.update_space) replaces the policy as a whole, so change the one that `get_space` returned:

```python
policy = manager.get_space().policy
if isinstance(policy, models.ComAtprotoMemberspacePolicy.Main):
    policy.public_read = True
    manager.update_space(policy)
```

The last write wins. A policy of another type discards the state of the previous one, such as a member list. A host may support policies of its own; `get_space` returns one that the SDK has no model for as a `DotDict`.

## A sync service

A sync service keeps its own copy of spaces, for example to index them for the users of an application. It acts for no account, so it uses a [SpaceReader](#atproto_space.SpaceReader), which has every read above and no writes.

### Getting credentials

A reader exchanges delegation tokens for space credentials. A delegation token is always minted by the PDS of an account that the space admits, with the session of that account, but the session does not have to live in the service:

```python
from atproto import SpaceReader


def get_delegation_token(ref):
    # the session of an account that the space admits
    return client.com.atproto.space.get_delegation_token({'space': str(ref)}).token


reader = SpaceReader(space_uri, forum, delegation_token_provider=get_delegation_token)
```

The provider can as well return a token that was minted elsewhere, for example by the application that holds the sessions of the users. A space that anyone may read needs no provider.

A space can admit certain applications only. Such a space wants a client attestation, signed with a key of the OAuth client:

```python
from atproto_crypto.jwk import load_private_jwk
from atproto_space.tokens import create_client_attestation

private_key = load_private_jwk(jwk)


def get_client_attestation(audience):
    return create_client_attestation(client_id, audience, private_key, kid=jwk['kid'])


reader = SpaceReader(
    space_uri,
    delegation_token_provider=get_delegation_token,
    client_attestation_provider=get_client_attestation,
)
```

`SpaceClient` takes `client_attestation_provider` too.

### Syncing repos

The service keeps a copy of each repo: its records and a `head`, the state to continue from. [pull_repo](#atproto_space.SpaceReader.pull_repo) brings the copy up to date:

```python
from atproto import RepoChanges, RepoSnapshot

head = store.get_head(repo)  # None before the first pull


def lookup(collection, rkey):
    return store.get_cid(repo, collection, rkey)


pulled = reader.pull_repo(head, lookup, repo)
if isinstance(pulled, RepoChanges):
    for change in pulled.changes:
        if change.cid:
            store.put(repo, change.collection, change.rkey, change.cid, change.value)
        else:
            store.delete(repo, change.collection, change.rkey)
    store.set_head(repo, pulled.head)
elif isinstance(pulled, RepoSnapshot):
    store.replace(repo, pulled.records)
    store.set_head(repo, pulled.head)
else:
    # the host has no such repo
    store.replace(repo, [])
    store.set_head(repo, None)
```

With a head, the operations since it are applied and checked against the commit of the repo. Without one, or when the operation log does not continue the known state, the repo is read in full and its records replace every known one. Either way the result is verified.

If the host returns a repo older than the known head, `pull_repo` raises [RepoGapError](#atproto_space.exceptions.RepoGapError). Call it again without a head to replace the copy with that repo, or keep the copy and try again later.

A [RepoHead](#atproto_space.RepoHead) is a revision and 2048 bytes of state. Store both. The values of the records are as decoded from DAG-CBOR, so a link is a [CID](#atproto_core.cid.CID).

To find the repos to sync, iterate [writers](#atproto_space.SpaceReader.writers). It yields the latest update of each repo: a `RepoWrite` with the current revision of the repo, or a `RepoRemoved` for a repo that is no longer part of the space. The highest `space_rev` seen is the cursor to list only the repos updated since:

```python
for writer in reader.writers(cursor=last_space_rev):
    ...
```

The host of a space may forget a removal after 72 hours. A service that has not caught up in that time lists the whole writer set instead, and drops the repos that are missing from it.

### Notifications

A service can register an endpoint that the host of the space notifies of updates, in place of polling. The registration is made, and renewed, with every credential:

```python
from atproto import models


def get_notify_registration(ref):
    # a token of this space that stays the same across credentials
    return models.ComAtprotoSpaceAuthorizeSpaceSync.Notify(
        endpoint='https://sync.example.com', token=store.get_notify_token(str(ref))
    )


reader = SpaceReader(
    space_uri,
    delegation_token_provider=get_delegation_token,
    notify_registration_provider=get_notify_registration,
)

credential = reader.authorize()  # registers the endpoint
print(credential.space_rev)
```

The endpoint has to implement `com.atproto.space.confirmRegistration`, which the host calls before it registers the endpoint, and `com.atproto.space.notifySpaceUpdate`. Serving them is up to the service: the SDK has the models of both and no server for them. When the service is told that its registration expired, or that the space was deleted, it calls `reader.authorize(renew=True)`, which fails with `SpaceDeleted` when the space is gone.

### Running on a server

Every reader builds an HTTP client and a cache of DID documents of its own, unless it is given them. A service that reads many spaces creates them once and passes them to every reader:

```python
from atproto import DidInMemoryCache, IdResolver, Request, SpaceReader

request = Request()
id_resolver = IdResolver(cache=DidInMemoryCache())

readers = [
    SpaceReader(uri, delegation_token_provider=get_delegation_token, request=request, id_resolver=id_resolver)
    for uri in space_uris
]
```

A reader sends its space credential with each request and keeps nothing in the HTTP client, so the readers of different spaces can share a `request`. The `request` of a reader must not be given to a `Client` as well. A client sends the session of its account with every request of its HTTP client, so a reader refuses to use one that a client has. `reader.request.close()` closes the HTTP client, as it does [for Client](http-and-transport.md#lifecycle).

The hosts that a reader contacts are named by DID documents, which anyone can publish: the PDS of the authority, the PDS of every writer, the host of a `did:web`. Its requests carry space credentials.

:::{warning}
Nothing stops a DID document from naming an internal address, and the reader does not check for one. If your service can reach internal systems, restrict its outbound network access.
:::

## Async

[AsyncSpaceClient](#atproto_space.AsyncSpaceClient), [AsyncSpaceManager](#atproto_space.AsyncSpaceManager) and [AsyncSpaceReader](#atproto_space.AsyncSpaceReader) have the same methods as coroutines, and async iterators where the sync classes return iterators. The providers and the lookup may be synchronous or asynchronous.

```python
from atproto import AsyncClient, AsyncSpaceClient

client = AsyncClient()
await client.login_oauth(session)

space = AsyncSpaceClient(client, 'at://did:plc:abc/space/com.example.forum/general')
await space.create_record({'$type': 'com.example.post', 'text': 'Hello, space!'})

async for record in space.all_records():
    print(record.repo, record.collection, record.value)
```

The async `all_records` reads four repos at a time. The sync one reads them one after another.

## Where requests go

| Request | Sent to | Authenticated with |
|---|---|---|
| The repo of the account: every write, and reads without `repo` | The PDS of the account | The session of the client |
| The repo of another account: reads with `repo` | The PDS of that account | The space credential |
| The space as a whole: `writers` | The host of the space | The space credential |
| The space credential itself: `authorize` | The host of the space | The delegation token, in the body |

Nothing is proxied. The requests that carry a space credential are made by an HTTP client of their own, never by the one that holds the session of the account. Pass `request` to configure it, as for [Client](http-and-transport.md), and `id_resolver` to share a cache of DID documents between instances. The `request` of a client, or a clone of it, is refused: it would send the session of the account to every host.

## Errors

| Error | When |
|---|---|
| [RequestErrorBase](#atproto_client.exceptions.RequestErrorBase) with `SpaceNotFound` | The space does not exist, or does not grant access. A host does not tell the two apart |
| [RequestErrorBase](#atproto_client.exceptions.RequestErrorBase) with `AppNotAuthorized` | The space admits certain applications only. See the client attestation in [Getting credentials](#getting-credentials) |
| [RequestErrorBase](#atproto_client.exceptions.RequestErrorBase) with `SpaceDeleted` | The space was deleted. Drop any copy of its data |
| [SpaceRepoVerificationError](#atproto_space.exceptions.SpaceRepoVerificationError) | A record, a commit, a repo or a blob failed verification |
| [RepoGapError](#atproto_space.exceptions.RepoGapError) | A repo cannot be synced from the known state. `pull_repo` reads the repo in full instead, and raises it only when the repo in full is older than the known state, for example after the host restored a backup |
| [InvalidStarError](#atproto_core.exceptions.InvalidStarError) | The host sent a repo that is not a valid STAR file |
| [SpaceIdentityError](#atproto_space.exceptions.SpaceIdentityError) | A DID document has no PDS, or no key to verify the responses of its host with |
| [DidNotFoundError](#atproto_identity.exceptions.DidNotFoundError) | The authority of the space, or the account of a repo, has no DID document |
| [SpaceTokenError](#atproto_space.exceptions.SpaceTokenError) | The host of the space issued a malformed credential |
| [LoginRequiredError](#atproto_client.exceptions.LoginRequiredError) | The client of a `SpaceClient` or a `SpaceManager` is not logged in |
| `ValueError` | The space is not of the given type, `request` carries the session of an account, a reader was given no `repo`, or the account is not the authority of the space it wants to manage |

The name of a server error is in the response, as described in [Error handling](error-handling.md#inspecting-the-failure):

```python
from atproto.exceptions import RequestErrorBase

try:
    space.authorize()
except RequestErrorBase as e:
    if e.response and e.response.content.error == 'SpaceNotFound':
        ...  # no such space, or no access to it
```

The `Space*` errors and `RepoGapError` inherit from [SpaceError](#atproto_space.exceptions.SpaceError). `InvalidStarError` does not.

Two failures are recovered from on their own:

- A request that is refused because of its credential (HTTP 401, for example after the credential was revoked) is repeated once with a new credential.
- A response that fails verification is requested once more with the key of its host resolved again, because the key may have been rotated.

## Limits

- **Alpha.** The lexicons come from a development branch of the protocol, and method names, scope parameters and wire formats can still change. Pin the SDK version if you build on this.
- **App passwords** are refused by every space method.
- **Whole responses are held in memory.** [get_repo](#atproto_space.SpaceReader.get_repo), `all_records` and [get_blob](#atproto_space.SpaceReader.get_blob) read the repo or the blob in full before they return.
- **A blob that its host serves as `application/json`** fails verification, because such a response is parsed.
- **Credentials live in memory**, and every instance requests its own.
- **Client only.** Hosting a space, minting credentials and serving the notification endpoints are not covered.
