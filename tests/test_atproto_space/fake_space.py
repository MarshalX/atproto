"""In-process network of PDSes for Spaces tests, served through ``httpx.MockTransport``."""

import asyncio
import base64
import hashlib
import hmac
import json
import secrets
import threading
import time
import typing as t
from dataclasses import dataclass, field

import httpx
import libipld
import typing_extensions as te
from atproto_client import AsyncClient, Client
from atproto_client.models.string_formats import DID_RE
from atproto_client.request import AsyncRequest, Request
from atproto_core.did_doc import DidDocument
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import SpaceRef
from atproto_crypto.algs import P256
from atproto_crypto.did import parse_did_key, private_key_to_did_key
from atproto_crypto.exceptions import DidKeyError
from atproto_crypto.jwk import base64url_decode
from atproto_crypto.jws import sign_jwt
from atproto_crypto.kem import decapsulate
from atproto_crypto.lthash import LtHash
from atproto_identity.exceptions import DidNotFoundError
from atproto_space._data import encode_json_value, get_record_cid
from atproto_space._structured_fields import (
    InnerList,
    Item,
    Member,
    parse_dictionary,
    serialize_dictionary,
    serialize_inner_list,
)
from atproto_space.exceptions import SpaceTokenError
from atproto_space.http_signature import build_signature_base
from atproto_space.tokens import DELEGATION_TOKEN_TYP, SPACE_CREDENTIAL_TYP, parse_space_token
from cryptography.hazmat.primitives.asymmetric import ec

from tests.test_atproto_space.star_builder import encode_repo_archive

if t.TYPE_CHECKING:
    from atproto_identity.resolver import AsyncIdResolver, IdResolver

AUTHORITY_DID = 'did:plc:authorityauthorityauthor'
ALICE_DID = 'did:plc:alicealicealicealiceali2'
BOB_DID = 'did:plc:bobbobbobbobbobbobbobbob'
AUTHORITY_PDS = 'https://authority.pds.test'
ALICE_PDS = 'https://alice.pds.test'
BOB_PDS = 'https://bob.pds.test'
SPACE = f'at://{AUTHORITY_DID}/space/com.example.group/main'

_P256 = P256()

_XRPC_PREFIX = '/xrpc/'
_DID_KEY_PREFIX = 'did:key:'
_SIGNING_KEY_ID = '#atproto'
_STAR_ENCODING = 'application/vnd.dasl.star'
_BLOB_ENCODING = 'application/octet-stream'
_RAW_SHA256_CID_PREFIX = bytes([0x01, 0x55, 0x12, 0x20])

_COMMIT_VERSION = 1
_COMMIT_FIELDS = ('ver', 'repo', 'space', 'rev', 'data')
_COMMIT_MAC_PROFILE = 'atproto-space-commit'
_RECORD_MAC_PROFILE = 'atproto-space-record'
_MAC_ALG = 'hmac-sha256'
_MAC_REQUEST_PARAMS = frozenset({'keyid', 'tag', 'alg'})
_MAC_KEM_INFO = b'atproto-mac'

_CREDENTIAL_SCHEME = 'atproto-space-credential'
_CREDENTIAL_AUDIENCE_HEADER = 'atproto-space-audience'
_CREDENTIAL_COMPONENTS = ('"authorization"', '"atproto-space-audience"')
_CREDENTIAL_TAG = 'atproto-space-credential'
_CREDENTIAL_ALG = 'ecdsa-p256-sha256'
_CREDENTIAL_SIGNATURE_SIZE = 64

_DELEGATION_TOKEN_LIFETIME = 60
_ACCESS_TOKEN_LIFETIME = 7200
_PASSWORD = 'password'
_GATE_TIMEOUT = 10

_WRITE_TYPE_PREFIX = 'com.atproto.space.applyWrites#'
_WRITE_ACTIONS = {f'{_WRITE_TYPE_PREFIX}{action}': action for action in ('create', 'update', 'delete')}
_REPO_WRITE_TYPE = 'com.atproto.space.defs#repoWrite'
_REPO_REMOVED_TYPE = 'com.atproto.space.defs#repoRemoved'

_MEMBERSPACE_POLICY_TYPE = 'com.atproto.memberspace.policy'
_POLICY_TYPES = frozenset(
    {'com.atproto.personalspace.policy', _MEMBERSPACE_POLICY_TYPE, 'com.atproto.managedspace.policy'}
)

_TID_ALPHABET = '234567abcdefghijklmnopqrstuvwxyz'
# later than any revision of a fixture, so a repo that was seeded with one moves forward
_FIRST_TIMESTAMP = 2_000_000_000_000_000


class _XrpcFailure(Exception):
    def __init__(self, status_code: int, error: str, message: str = '') -> None:
        super().__init__(message or error)
        self.status_code = status_code
        self.error = error


@dataclass
class Account:
    did: str
    pds: str
    access_token: str
    signing_key: ec.EllipticCurvePrivateKey = field(repr=False)
    #: Key of ``#atproto_kem``. An account without it can not answer with a MAC.
    kem_key: t.Optional[ec.EllipticCurvePrivateKey] = field(repr=False)
    #: Type and value of the ``#atproto_kem`` method that the DID document holds in place of the one of the key.
    kem_method: t.Optional[t.Tuple[str, str]] = None
    #: Error that the PDS answers anyone else who reads a repo of the account with, such as ``RepoTakendown``.
    unavailable: t.Optional[str] = None

    @property
    def did_document(self) -> DidDocument:
        methods = [_build_verification_method(self.did, 'atproto', self.signing_key)]
        if self.kem_method is not None:
            key_type, key = self.kem_method
            methods.append(
                {'id': f'{self.did}#atproto_kem', 'type': key_type, 'controller': self.did, 'publicKeyMultibase': key}
            )
        elif self.kem_key is not None:
            methods.append(_build_verification_method(self.did, 'atproto_kem', self.kem_key))

        return DidDocument.from_dict(
            {
                'id': self.did,
                'verificationMethod': methods,
                'service': [{'id': '#atproto_pds', 'type': 'AtprotoPersonalDataServer', 'serviceEndpoint': self.pds}],
            }
        )


@dataclass
class Record:
    cid: str
    #: JSON form of the record.
    value: t.Dict[str, t.Any]
    #: DAG-CBOR of the record.
    data: bytes


@dataclass
class Op:
    rev: str
    collection: str
    rkey: str
    cid: t.Optional[str]
    prev: t.Optional[str]
    #: Position among the operations of the commit.
    idx: int = 0


@dataclass
class Repo:
    """Repo of an account in a space, kept by the PDS of the account."""

    rev: str
    #: Path (``collection/rkey``) -> record.
    records: t.Dict[str, Record] = field(default_factory=dict)
    ops: t.List[Op] = field(default_factory=list)
    #: CID -> content and MIME type.
    blobs: t.Dict[str, t.Tuple[bytes, str]] = field(default_factory=dict)


@dataclass
class Writer:
    repo_rev: str
    data: bytes
    space_rev: str
    removed: bool = False


@dataclass
class Space:
    """Space as its host knows it."""

    uri: str
    #: DIDs of the accounts that read and write the space besides its authority.
    members: t.Set[str] = field(default_factory=set)
    #: Let anyone read the space, with or without a delegation token.
    public: bool = False
    deleted: bool = False
    #: DID -> state of the repo that its PDS reported last.
    writers: t.Dict[str, Writer] = field(default_factory=dict)
    #: JSON form of the policy that governs the space.
    policy: t.Dict[str, t.Any] = field(default_factory=lambda: {'$type': _MEMBERSPACE_POLICY_TYPE})
    #: DID -> whether a member reads the space and whether it writes it, for the members that do not do both.
    restricted: t.Dict[str, t.Tuple[bool, bool]] = field(default_factory=dict)

    def allows(self, did: str, write: bool = False) -> bool:
        if did in self.restricted:
            reads, writes = self.restricted[did]
            return writes if write else reads

        return did == SpaceRef.from_str(self.uri).space_did or did in self.members


@dataclass(frozen=True)
class MacRequest:
    """MAC that a request asks for, as a host reads it from ``Accept-Signature``."""

    label: str
    key_share: str
    signature_params: str


@dataclass(frozen=True)
class _Credential:
    space: str
    audience: str


@dataclass(frozen=True)
class _Write:
    #: ``create``, ``update``, ``delete`` or ``put``, which creates or updates.
    action: str
    collection: str
    rkey: str
    value: t.Optional[t.Dict[str, t.Any]] = None


_Auth = t.Union[Account, _Credential]
_Mac = t.Tuple[MacRequest, bytes]
_OpsCursor = t.Tuple[str, int]
_Route = t.Callable[[httpx.Request, str], httpx.Response]


def _build_verification_method(did: str, name: str, key: ec.EllipticCurvePrivateKey) -> t.Dict[str, str]:
    return {
        'id': f'{did}#{name}',
        'type': 'Multikey',
        'controller': did,
        'publicKeyMultibase': private_key_to_did_key(key)[len(_DID_KEY_PREFIX) :],
    }


def _generate_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1())


def _encode_tid(timestamp: int) -> str:
    value = timestamp << 10
    return ''.join(_TID_ALPHABET[(value >> shift) & 31] for shift in range(60, -1, -5))


def _encode_bytes(data: bytes) -> t.Dict[str, str]:
    return {'$bytes': base64.b64encode(data).decode('ascii').rstrip('=')}


def _get_blob_cid(data: bytes) -> str:
    return libipld.encode_cid(_RAW_SHA256_CID_PREFIX + hashlib.sha256(data).digest())


def _get_nsid(request: httpx.Request) -> str:
    return request.url.path[len(_XRPC_PREFIX) :]


def _json(body: t.Any, headers: t.Optional[t.Dict[str, str]] = None) -> httpx.Response:
    return httpx.Response(200, json=body, headers=headers)


def _parse_space(uri: str) -> SpaceRef:
    try:
        return SpaceRef.from_str(uri)
    except InvalidAtUriError as e:
        raise _XrpcFailure(400, 'InvalidSpaceUri', f'Not a space uri: {uri}') from e


def _parse_ops_cursor(cursor: str) -> _OpsCursor:
    rev, _, idx = cursor.partition('/')
    if not idx.isdecimal():
        raise _XrpcFailure(400, 'InvalidCursor', 'Malformed cursor')

    return rev, int(idx)


def _is_p256_did_key(key: object) -> bool:
    try:
        return isinstance(key, str) and parse_did_key(key).jwt_alg == P256.NAME
    except (DidKeyError, ValueError):
        return False


def _verify_jwt(jwt: str, signing_key: ec.EllipticCurvePrivateKey) -> bool:
    signing_input, _, signature = jwt.rpartition('.')
    public_key = parse_did_key(private_key_to_did_key(signing_key)).key_bytes

    try:
        return _P256.verify_signature(public_key, signing_input.encode(), base64url_decode(signature))
    except ValueError:
        return False


def _find_tagged(members: t.Mapping[str, Member], tag: str) -> t.List[t.Tuple[str, InnerList]]:
    return [
        (label, member)
        for label, member in members.items()
        if isinstance(member, InnerList) and member.params.get('tag') == tag
    ]


def _verify_credential_signature(headers: httpx.Headers, key_id: str) -> bool:
    try:
        signature_inputs = parse_dictionary(headers.get('signature-input', ''))
        signatures = parse_dictionary(headers.get('signature', ''))
    except ValueError:
        return False

    tagged = _find_tagged(signature_inputs, _CREDENTIAL_TAG)
    if len(tagged) != 1:
        return False

    label, signature_input = tagged[0]
    signature = signatures.get(label)
    if not isinstance(signature, Item) or not isinstance(signature.value, bytes) or signature.params:
        return False

    if serialize_inner_list(InnerList(signature_input.items)) != f'({" ".join(_CREDENTIAL_COMPONENTS)})':
        return False

    params = signature_input.params
    if params.get('alg', _CREDENTIAL_ALG) != _CREDENTIAL_ALG or params.get('keyid', key_id) != key_id:
        return False

    signature_base = build_signature_base(
        _CREDENTIAL_COMPONENTS,
        [headers['authorization'], headers[_CREDENTIAL_AUDIENCE_HEADER]],
        serialize_inner_list(signature_input),
    )

    return len(signature.value) == _CREDENTIAL_SIGNATURE_SIZE and _P256.verify_signature(
        parse_did_key(key_id).key_bytes, signature_base, signature.value
    )


def parse_mac_request(accept_signature: t.Optional[str], profile: str) -> t.Optional[MacRequest]:
    """Find the MAC that a request asks for under the tag of the profile, if it asks for one."""
    if accept_signature is None:
        return None

    try:
        requests = parse_dictionary(accept_signature)
    except ValueError as e:
        raise _XrpcFailure(400, 'InvalidSpaceMac', 'malformed Accept-Signature header') from e

    tagged = _find_tagged(requests, profile)
    if not tagged:
        return None

    if len(tagged) > 1:
        raise _XrpcFailure(400, 'InvalidSpaceMac', f'more than one MAC requested with tag "{profile}"')

    label, signature_params = tagged[0]
    components = f'("{profile}";sf)'
    if serialize_inner_list(InnerList(signature_params.items)) != components:
        raise _XrpcFailure(400, 'InvalidSpaceMac', f'MAC must cover exactly {components}')

    params = signature_params.params
    unsupported = set(params) - _MAC_REQUEST_PARAMS
    if unsupported:
        raise _XrpcFailure(400, 'InvalidSpaceMac', f'unsupported MAC parameter: {min(unsupported)}')

    if params.get('alg', _MAC_ALG) != _MAC_ALG:
        raise _XrpcFailure(400, 'InvalidSpaceMac', f'MAC algorithm must be {_MAC_ALG}')

    key_share = params.get('keyid')
    if not isinstance(key_share, str) or not DID_RE.fullmatch(key_share):
        raise _XrpcFailure(400, 'InvalidSpaceMac', 'missing or malformed keyid')

    return MacRequest(label, key_share, serialize_inner_list(signature_params))


def _create_mac_headers(profile: str, covered: str, mac_request: MacRequest, shared_secret: bytes) -> t.Dict[str, str]:
    signature_base = build_signature_base([f'"{profile}";sf'], [covered], mac_request.signature_params)
    mac = hmac.new(shared_secret, signature_base, hashlib.sha256).digest()

    return {
        profile: covered,
        'signature-input': f'{mac_request.label}={mac_request.signature_params}',
        'signature': f'{mac_request.label}=:{base64.b64encode(mac).decode("ascii")}:',
    }


def create_commit_mac_headers(
    commit: t.Mapping[str, t.Any], mac_request: MacRequest, shared_secret: bytes
) -> t.Dict[str, str]:
    """Create the headers that a host answers a MAC request with: the commit and the MAC that covers it."""
    covered = serialize_dictionary({name: Item(commit[name]) for name in _COMMIT_FIELDS})

    return _create_mac_headers(_COMMIT_MAC_PROFILE, covered, mac_request, shared_secret)


def create_record_mac_headers(uri: str, cid: str, mac_request: MacRequest, shared_secret: bytes) -> t.Dict[str, str]:
    """Create the headers that a host answers a MAC request with: the name of the record and the MAC that covers it."""
    covered = serialize_dictionary({'uri': Item(uri), 'cid': Item(cid)})

    return _create_mac_headers(_RECORD_MAC_PROFILE, covered, mac_request, shared_secret)


@dataclass
class FakeSpaceNetwork:
    """PDSes of the accounts, each at its own origin, with the spaces and the repos that they host."""

    #: Lifetime of the space credentials in seconds.
    credential_lifetime: int = 600
    #: NSID -> responses to serve in place of the next requests, one each.
    forced_responses: t.Dict[str, t.List[httpx.Response]] = field(default_factory=dict)
    #: NSID -> seconds to wait before a request is served.
    delays: t.Dict[str, float] = field(default_factory=dict)
    #: NSID -> event that a request waits for before it is served, of ``threading`` or ``asyncio`` as the transport.
    gates: t.Dict[str, t.Union[threading.Event, asyncio.Event]] = field(default_factory=dict)
    #: Answer a MAC request without the MAC.
    drop_mac: bool = False
    #: Answer a MAC request with a MAC under another secret.
    corrupt_mac: bool = False
    #: Changes the commit of a repo before a host answers with it. The MAC covers the commit as it is changed.
    tamper_commit: t.Optional[t.Callable[[t.Dict[str, t.Any]], None]] = None
    #: Longest page of the operation log of a repo to serve, whatever limit the request asks for.
    ops_limit: t.Optional[int] = None
    #: Changes a page of the operation log of a repo before it is served. The MAC covers the commit as it was.
    tamper_ops: t.Optional[t.Callable[[t.Dict[str, t.Any]], None]] = None
    #: Changes the records of the archive of a repo, the path and the DAG-CBOR of each, before it is served.
    tamper_archive: t.Optional[t.Callable[[t.List[t.Tuple[str, bytes]]], None]] = None

    def __post_init__(self) -> None:
        self.accounts: t.Dict[str, Account] = {}
        self.spaces: t.Dict[str, Space] = {}
        #: (URI of the space, DID) -> repo.
        self.repos: t.Dict[t.Tuple[str, str], Repo] = {}
        self.requests: t.List[httpx.Request] = []
        self.log: t.List[t.Tuple[str, str, int]] = []
        #: Space credentials in the order they were issued.
        self.credentials: t.List[str] = []
        self._revoked_credentials: t.Set[str] = set()
        self._seen_jtis: t.Set[str] = set()
        self._timestamp = _FIRST_TIMESTAMP
        self._lock = threading.Lock()
        self._routes: t.Dict[str, _Route] = {
            'com.atproto.space.authorizeSpaceSync': self._authorize_space_sync,
            'com.atproto.space.listWriters': self._list_writers,
            'com.atproto.space.listRecords': self._list_records,
            'com.atproto.space.listBlobs': self._list_blobs,
            'com.atproto.space.getRecord': self._get_record,
            'com.atproto.space.getLatestCommit': self._get_latest_commit,
            'com.atproto.space.getBlob': self._get_blob,
            'com.atproto.space.getRepo': self._get_repo,
            'com.atproto.space.listRepoOps': self._list_repo_ops,
            'com.atproto.space.getDelegationToken': self._get_delegation_token,
            'com.atproto.space.createRecord': self._create_record,
            'com.atproto.space.putRecord': self._put_record,
            'com.atproto.space.deleteRecord': self._delete_record,
            'com.atproto.space.applyWrites': self._apply_writes_route,
            'com.atproto.space.clearRecords': self._clear_records,
            'com.atproto.space.createSpace': self._create_space,
            'com.atproto.space.getSpace': self._get_space,
            'com.atproto.space.updateSpace': self._update_space,
            'com.atproto.space.deleteSpace': self._delete_space,
            'com.atproto.space.removeWriter': self._remove_writer,
            'com.atproto.memberspace.listMembers': self._list_members,
            'com.atproto.memberspace.putMembers': self._put_members,
            'com.atproto.memberspace.removeMembers': self._remove_members,
            'com.atproto.server.createSession': self._create_session,
        }

    @property
    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handle)

    @property
    def async_transport(self) -> httpx.MockTransport:
        """Transport of an asynchronous client. A delayed response does not block the event loop."""
        return httpx.MockTransport(self.handle_async)

    def count(self, nsid: str) -> int:
        return len(self.requests_to(nsid))

    def statuses(self, nsid: str) -> t.List[int]:
        return [status for _, logged_nsid, status in self.log if logged_nsid == nsid]

    def requests_to(self, nsid: str) -> t.List[httpx.Request]:
        return [request for request in self.requests if _get_nsid(request) == nsid]

    def add_account(self, did: str, pds: str, has_kem_key: bool = True) -> Account:
        account = Account(
            did=did,
            pds=pds,
            access_token=f'access-{secrets.token_hex(8)}',
            signing_key=_generate_key(),
            kem_key=_generate_key() if has_kem_key else None,
        )
        self.accounts[did] = account

        return account

    def add_space(self, uri: str, members: t.Iterable[str] = (), public: bool = False) -> Space:
        space = Space(uri, set(members), public)
        self.spaces[uri] = space

        return space

    def put_record(self, space: str, repo: str, collection: str, rkey: str, value: t.Dict[str, t.Any]) -> str:
        """Write a record straight into a repo, whatever its type. Returns the CID."""
        return t.cast('str', self._apply_writes(space, repo, [_Write('put', collection, rkey, value)])[0])

    def delete_record(self, space: str, repo: str, collection: str, rkey: str) -> None:
        self._apply_writes(space, repo, [_Write('delete', collection, rkey)])

    def add_blob(self, space: str, repo: str, data: bytes, mime_type: str = _BLOB_ENCODING) -> str:
        """Attach a blob to a repo that exists. Returns the CID."""
        cid = _get_blob_cid(data)
        self.repos[(space, repo)].blobs[cid] = (data, mime_type)

        return cid

    def remove_writer(self, space: str, repo: str) -> None:
        writer = self.spaces[space].writers[repo]
        writer.space_rev = self._next_tid()
        writer.removed = True

    def get_commit(self, space: str, repo: str) -> t.Dict[str, t.Any]:
        """Get the commit of a repo that was written to."""
        state = self.repos[(space, repo)]

        set_hash = LtHash()
        for path, record in state.records.items():
            set_hash.add(f'{path}/{record.cid}')

        return {'ver': _COMMIT_VERSION, 'repo': repo, 'space': space, 'rev': state.rev, 'data': set_hash.digest()}

    def create_delegation_token(self, did: str, space: str) -> str:
        """Create the token that the PDS of an account issues for the host of a space."""
        issued_at = int(time.time())

        return sign_jwt(
            {'typ': DELEGATION_TOKEN_TYP, 'kid': _SIGNING_KEY_ID},
            {
                'iss': did,
                'sub': space,
                'aud': f'{_parse_space(space).space_did}#atproto_pds',
                'iat': issued_at,
                'exp': issued_at + _DELEGATION_TOKEN_LIFETIME,
                'jti': secrets.token_hex(16),
            },
            self.accounts[did].signing_key,
        )

    def revoke_credentials(self) -> None:
        """Make every host answer 401 to the space credentials issued so far."""
        self._revoked_credentials.update(self.credentials)

    def handle(self, request: httpx.Request) -> httpx.Response:
        request.read()
        self.requests.append(request)
        nsid = _get_nsid(request)
        time.sleep(self.delays.get(nsid, 0))

        gate = self.gates.get(nsid)
        if isinstance(gate, threading.Event):
            gate.wait(_GATE_TIMEOUT)

        return self._respond(request)

    async def handle_async(self, request: httpx.Request) -> httpx.Response:
        await request.aread()
        self.requests.append(request)
        nsid = _get_nsid(request)
        await asyncio.sleep(self.delays.get(nsid, 0))

        gate = self.gates.get(nsid)
        if isinstance(gate, asyncio.Event):
            await asyncio.wait_for(gate.wait(), _GATE_TIMEOUT)

        return self._respond(request)

    def _respond(self, request: httpx.Request) -> httpx.Response:
        origin = f'{request.url.scheme}://{request.url.host}'
        nsid = _get_nsid(request)

        with self._lock:
            forced = self.forced_responses.get(nsid)
            response = forced.pop(0) if forced else self._dispatch(request, origin, nsid)
            self.log.append((origin, nsid, response.status_code))

        return response

    def _dispatch(self, request: httpx.Request, origin: str, nsid: str) -> httpx.Response:
        route = self._routes.get(nsid)
        if route is None or not request.url.path.startswith(_XRPC_PREFIX):
            return httpx.Response(501, json={'error': 'MethodNotImplemented', 'message': 'Method Not Implemented'})

        try:
            return route(request, origin)
        except _XrpcFailure as e:
            return httpx.Response(e.status_code, json={'error': e.error, 'message': str(e)})

    def _next_tid(self) -> str:
        self._timestamp += 1
        return _encode_tid(self._timestamp)

    def _authenticate(self, request: httpx.Request, origin: str) -> _Auth:
        scheme, _, token = request.headers.get('authorization', '').partition(' ')
        if not token:
            raise _XrpcFailure(401, 'AuthMissing', 'Authentication Required')

        if scheme.lower() == _CREDENTIAL_SCHEME:
            return self._check_credential(request, token)

        account = next((a for a in self.accounts.values() if a.access_token == token and a.pds == origin), None)
        if scheme.lower() != 'bearer' or account is None:
            raise _XrpcFailure(401, 'InvalidToken', 'Token could not be verified')

        return account

    def _authenticate_account(self, request: httpx.Request, origin: str) -> Account:
        account = self._authenticate(request, origin)
        if not isinstance(account, Account):
            raise _XrpcFailure(401, 'InvalidToken', 'Unexpected authorization type')

        return account

    def _check_credential(self, request: httpx.Request, token: str) -> _Credential:
        try:
            claims = parse_space_token('credential', token)
            ref = SpaceRef.from_str(claims.sub)
        except SpaceTokenError as e:
            raise _XrpcFailure(401, e.code, str(e)) from e
        except InvalidAtUriError as e:
            raise _XrpcFailure(401, 'BadJwtSub', 'space token subject is not a space URI') from e

        authority = self.accounts.get(claims.iss)
        if authority is None or not _verify_jwt(token, authority.signing_key):
            raise _XrpcFailure(401, 'BadJwtSignature', 'could not verify the signature of the space credential')

        if claims.exp <= time.time():
            raise _XrpcFailure(401, 'JwtExpired', 'space credential expired')

        if claims.iss != ref.space_did:
            raise _XrpcFailure(401, 'BadJwtIss', 'space credential issuer is not the space authority')

        audience = request.headers.get(_CREDENTIAL_AUDIENCE_HEADER, '')
        if not DID_RE.fullmatch(audience):
            raise _XrpcFailure(401, 'BadSpaceSignature', 'missing or invalid space audience DID')

        if not _verify_credential_signature(request.headers, t.cast('str', claims.key_id)):
            raise _XrpcFailure(401, 'BadSpaceSignature', 'invalid HTTP message signature')

        if token in self._revoked_credentials:
            raise _XrpcFailure(401, 'CredentialRevoked', 'space credential has been revoked')

        return _Credential(space=claims.sub, audience=audience)

    @staticmethod
    def _check_credential_space(credential: _Credential, space: str, audience: str) -> None:
        if credential.audience != audience:
            raise _XrpcFailure(401, 'BadSpaceAudience', 'space audience does not match the request')

        if credential.space != space:
            raise _XrpcFailure(400, 'InvalidCredential', 'Credential is not scoped to this space')

    def _get_hosted_space(self, ref: SpaceRef, origin: str) -> Space:
        authority = self.accounts.get(ref.space_did)
        space = self.spaces.get(str(ref))
        if authority is None or authority.pds != origin or space is None:
            raise _XrpcFailure(400, 'SpaceNotFound', 'Space not found')

        return space

    def _authorize_repo_read(self, request: httpx.Request, origin: str) -> t.Tuple[str, str, _Auth]:
        space, repo = request.url.params['space'], request.url.params['repo']
        _parse_space(space)

        auth = self._authenticate(request, origin)
        if isinstance(auth, _Credential):
            self._check_credential_space(auth, space, repo)

        account = self.accounts.get(repo)
        # an account credential reads only the repo of the account
        if account is None or account.pds != origin or (isinstance(auth, Account) and auth.did != repo):
            raise _XrpcFailure(400, 'RepoNotFound', f'Could not find repo for DID: {repo}')

        if account.unavailable and isinstance(auth, _Credential):
            raise _XrpcFailure(400, account.unavailable, f'Repo is not available: {repo}')

        return space, repo, auth

    def _get_mac(self, request: httpx.Request, auth: _Auth, repo: str, profile: str) -> t.Optional[_Mac]:
        mac_request = parse_mac_request(request.headers.get('accept-signature'), profile)
        if mac_request is None:
            if isinstance(auth, _Credential):
                raise _XrpcFailure(400, 'InvalidSpaceMac', f'A MAC must be requested with tag "{profile}"')

            return None

        kem_key = self.accounts[repo].kem_key
        if kem_key is None:
            raise _XrpcFailure(500, 'InternalServerError', f'Account has no KEM key: {repo}')

        try:
            shared_secret = decapsulate(kem_key, mac_request.key_share, _MAC_KEM_INFO)
        except (DidKeyError, ValueError) as e:
            raise _XrpcFailure(400, 'InvalidSpaceMac', 'invalid KEM key') from e

        if self.drop_mac:
            return None
        if self.corrupt_mac:
            shared_secret = bytes(len(shared_secret))

        return mac_request, shared_secret

    def _get_repo_commit(self, space: str, repo: str) -> t.Dict[str, t.Any]:
        if (space, repo) not in self.repos:
            raise _XrpcFailure(400, 'RepoNotFound', f'Could not find repo for space: {space}')

        commit = self.get_commit(space, repo)
        if self.tamper_commit is not None:
            self.tamper_commit(commit)

        return commit

    def _get_records(self, space: str, repo: str) -> t.Dict[str, Record]:
        state = self.repos.get((space, repo))
        return state.records if state else {}

    def _record_writer(self, space_uri: str, did: str) -> None:
        space = self.spaces.get(space_uri)
        # the host of a space ignores the repo of an account that the space does not let write
        if space is None or space.deleted or not space.allows(did, write=True):
            return

        commit = self.get_commit(space_uri, did)
        space.writers[did] = Writer(repo_rev=commit['rev'], data=commit['data'], space_rev=self._next_tid())

    def _apply_writes(self, space: str, did: str, writes: t.Sequence[_Write]) -> t.List[t.Optional[str]]:
        """Apply the writes as one commit, or none of them. Returns the CID that each one left behind."""
        if not writes:
            return []

        state = self.repos.get((space, did))
        records = dict(state.records) if state else {}
        rev = self._next_tid()
        ops: t.List[Op] = []

        for write in writes:
            path = f'{write.collection}/{write.rkey}'
            prev = records[path].cid if path in records else None
            if write.action == 'create' and prev:
                raise _XrpcFailure(400, 'RecordAlreadyExists', f'Record already exists: {path}')
            if write.action in {'update', 'delete'} and not prev:
                raise _XrpcFailure(400, 'RecordNotFound', f'Record not found: {path}')

            cid = None
            if write.value is None:
                del records[path]
            else:
                data = encode_json_value(write.value)
                cid = get_record_cid(data)
                records[path] = Record(cid, write.value, data)

            ops.append(Op(rev, write.collection, write.rkey, cid, prev, len(ops)))

        if state is None:
            state = self.repos[(space, did)] = Repo(rev)

        state.rev = rev
        state.records = records
        state.ops += ops
        self._record_writer(space, did)

        return [op.cid for op in ops]

    def _authorize_space_sync(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = json.loads(request.content)
        ref = _parse_space(body['space'])
        if not _is_p256_did_key(body['credentialKey']):
            raise _XrpcFailure(400, 'InvalidRequest', 'credentialKey must be a P-256 did:key')

        space = self._get_hosted_space(ref, origin)
        if space.deleted:
            raise _XrpcFailure(400, 'SpaceDeleted', 'Space has been deleted')

        repo = None
        if body.get('delegationToken'):
            repo = self._verify_delegation_token(body['delegationToken'], ref)
        if body.get('clientAttestation'):
            self._check_client_attestation(body['clientAttestation'], ref)

        # the same answer as for a space that does not exist, so that it tells nothing about the space
        if not space.public and (repo is None or not space.allows(repo)):
            raise _XrpcFailure(400, 'SpaceNotFound', 'Space not found')

        issued_at = int(time.time())
        credential = sign_jwt(
            {'typ': SPACE_CREDENTIAL_TYP, 'kid': _SIGNING_KEY_ID},
            {
                'iss': ref.space_did,
                'sub': space.uri,
                'cnf': {'kid': body['credentialKey']},
                'iat': issued_at,
                'exp': issued_at + self.credential_lifetime,
                'jti': secrets.token_hex(16),
            },
            self.accounts[ref.space_did].signing_key,
        )
        self.credentials.append(credential)

        output = {'credential': credential}
        if space.writers:
            output['spaceRev'] = max(writer.space_rev for writer in space.writers.values())

        return _json(output)

    def _verify_delegation_token(self, token: str, ref: SpaceRef) -> str:
        try:
            claims = parse_space_token('delegation', token)
        except SpaceTokenError as e:
            raise _XrpcFailure(400, 'InvalidDelegationToken', str(e)) from e

        issuer = self.accounts.get(claims.iss)
        valid = (
            issuer is not None
            and _verify_jwt(token, issuer.signing_key)
            and claims.sub == str(ref)
            and claims.aud == f'{ref.space_did}#atproto_pds'
            and claims.exp > time.time()
            and claims.jti not in self._seen_jtis
        )
        if not valid:
            raise _XrpcFailure(400, 'InvalidDelegationToken', 'Delegation token is not valid for the space')

        self._seen_jtis.add(claims.jti)

        return claims.iss

    @staticmethod
    def _check_client_attestation(token: str, ref: SpaceRef) -> None:
        # the network has no client metadata to verify the signature with
        try:
            claims = parse_space_token('client_attestation', token)
        except SpaceTokenError as e:
            raise _XrpcFailure(400, 'InvalidClientAttestation', str(e)) from e

        if claims.aud != f'{ref.space_did}#atproto_pds':
            raise _XrpcFailure(400, 'InvalidClientAttestation', 'Client attestation is for another audience')

    def _list_writers(self, request: httpx.Request, origin: str) -> httpx.Response:
        params = request.url.params
        ref = _parse_space(params['space'])

        credential = self._authenticate(request, origin)
        if not isinstance(credential, _Credential):
            raise _XrpcFailure(401, 'MissingJwt', 'missing space credential')

        self._check_credential_space(credential, params['space'], ref.space_did)
        space = self._get_hosted_space(ref, origin)
        if space.deleted:
            raise _XrpcFailure(400, 'SpaceNotFound', 'Space not found')

        cursor = params.get('cursor', '')
        writers = sorted(
            ((did, writer) for did, writer in space.writers.items() if writer.space_rev > cursor),
            key=lambda item: item[1].space_rev,
        )[: int(params.get('limit', 100))]

        repos: t.List[t.Dict[str, t.Any]] = []
        for did, writer in writers:
            if writer.removed:
                repos.append({'$type': _REPO_REMOVED_TYPE, 'repo': did, 'spaceRev': writer.space_rev})
            else:
                repos.append(
                    {
                        '$type': _REPO_WRITE_TYPE,
                        'repo': did,
                        'repoRev': writer.repo_rev,
                        'data': _encode_bytes(writer.data),
                        'spaceRev': writer.space_rev,
                    }
                )

        output: t.Dict[str, t.Any] = {'repos': repos}
        if writers:
            output['cursor'] = writers[-1][1].space_rev

        return _json(output)

    def _list_records(self, request: httpx.Request, origin: str) -> httpx.Response:
        space, repo, _ = self._authorize_repo_read(request, origin)
        params = request.url.params
        limit = int(params.get('limit', 50))
        collection = params.get('collection')

        cursor = params.get('cursor')
        if cursor is not None:
            try:
                SpaceRef.from_uri(cursor)
            except InvalidAtUriError as e:
                raise _XrpcFailure(400, 'InvalidCursor', 'Malformed cursor') from e

        records = self._get_records(space, repo)
        prefix = f'{space}/{repo}/'
        paths = sorted(
            (
                path
                for path in records
                if (collection is None or path.split('/')[0] == collection)
                and (cursor is None or prefix + path < cursor)
            ),
            reverse=True,
        )[:limit]

        listed: t.List[t.Dict[str, t.Any]] = []
        for path in paths:
            record_collection, rkey = path.split('/')
            item: t.Dict[str, t.Any] = {'collection': record_collection, 'rkey': rkey, 'cid': records[path].cid}
            if params.get('excludeValues') != 'true':
                item['value'] = records[path].value

            listed.append(item)

        output: t.Dict[str, t.Any] = {'records': listed}
        if len(paths) >= limit:
            output['cursor'] = prefix + paths[-1]

        return _json(output)

    def _list_blobs(self, request: httpx.Request, origin: str) -> httpx.Response:
        space, repo, _ = self._authorize_repo_read(request, origin)
        params = request.url.params
        limit = int(params.get('limit', 500))

        state = self.repos.get((space, repo))
        cids = sorted(cid for cid in (state.blobs if state else {}) if cid > params.get('cursor', ''))[:limit]

        output: t.Dict[str, t.Any] = {'cids': cids}
        if len(cids) >= limit:
            output['cursor'] = cids[-1]

        return _json(output)

    def _get_record(self, request: httpx.Request, origin: str) -> httpx.Response:
        space, repo, auth = self._authorize_repo_read(request, origin)
        mac = self._get_mac(request, auth, repo, _RECORD_MAC_PROFILE)

        path = f'{request.url.params["collection"]}/{request.url.params["rkey"]}'
        uri = f'{space}/{repo}/{path}'
        record = self._get_records(space, repo).get(path)
        if record is None:
            raise _XrpcFailure(400, 'RecordNotFound', f'Could not locate record: {uri}')

        headers = create_record_mac_headers(uri, record.cid, *mac) if mac else None

        return _json({'uri': uri, 'cid': record.cid, 'value': record.value}, headers)

    def _get_latest_commit(self, request: httpx.Request, origin: str) -> httpx.Response:
        space, repo, auth = self._authorize_repo_read(request, origin)
        mac = self._get_mac(request, auth, repo, _COMMIT_MAC_PROFILE)

        commit = self._get_repo_commit(space, repo)
        headers = create_commit_mac_headers(commit, *mac) if mac else None

        return _json({'commit': {**commit, 'data': _encode_bytes(commit['data'])}}, headers)

    def _get_blob(self, request: httpx.Request, origin: str) -> httpx.Response:
        space, repo, _ = self._authorize_repo_read(request, origin)

        state = self.repos.get((space, repo))
        blob = state.blobs.get(request.url.params['cid']) if state else None
        if blob is None:
            raise _XrpcFailure(400, 'BlobNotFound', 'Blob not found')

        data, mime_type = blob

        return httpx.Response(200, content=data, headers={'content-type': mime_type})

    def _get_repo(self, request: httpx.Request, origin: str) -> httpx.Response:
        space, repo, auth = self._authorize_repo_read(request, origin)
        mac = self._get_mac(request, auth, repo, _COMMIT_MAC_PROFILE)

        commit = self._get_repo_commit(space, repo)
        records = self._get_records(space, repo)
        # an archive lists the records in the byte order of their paths
        paths = sorted(records, key=lambda path: path.encode('UTF-8'))
        pairs = [(path, records[path].data) for path in paths]
        if self.tamper_archive is not None:
            self.tamper_archive(pairs)

        headers = {'content-type': _STAR_ENCODING}
        if mac:
            headers.update(create_commit_mac_headers(commit, *mac))

        return httpx.Response(200, content=encode_repo_archive(commit, pairs), headers=headers)

    def _list_repo_ops(self, request: httpx.Request, origin: str) -> httpx.Response:
        space, repo, auth = self._authorize_repo_read(request, origin)
        mac = self._get_mac(request, auth, repo, _COMMIT_MAC_PROFILE)
        params = request.url.params
        limit = min(int(params.get('limit', 100)), self.ops_limit or 1000)
        since = params.get('since', '')
        cursor = _parse_ops_cursor(params['cursor']) if 'cursor' in params else None

        commit = self._get_repo_commit(space, repo)
        state = self.repos[(space, repo)]
        ops = sorted(
            (op for op in state.ops if op.rev > since and (cursor is None or (op.rev, op.idx) > cursor)),
            key=lambda op: (op.rev, op.idx),
        )[:limit]

        listed: t.List[t.Dict[str, t.Any]] = []
        for op in ops:
            item: t.Dict[str, t.Any] = {
                'rev': op.rev,
                'collection': op.collection,
                'rkey': op.rkey,
                'cid': op.cid,
                'prev': op.prev,
            }
            record = state.records.get(f'{op.collection}/{op.rkey}')
            # an operation is listed with the value only while the record is the one that it left behind
            if record is not None and record.cid == op.cid and params.get('excludeValues') != 'true':
                item['value'] = record.value

            listed.append(item)

        output: t.Dict[str, t.Any] = {'ops': listed, 'commit': {**commit, 'data': _encode_bytes(commit['data'])}}
        if len(ops) >= limit:
            output['cursor'] = f'{ops[-1].rev}/{ops[-1].idx}'
        if self.tamper_ops is not None:
            self.tamper_ops(output)

        headers = create_commit_mac_headers(commit, *mac) if mac else None

        return _json(output, headers)

    def _get_delegation_token(self, request: httpx.Request, origin: str) -> httpx.Response:
        account = self._authenticate_account(request, origin)
        space = request.url.params['space']
        _parse_space(space)

        return _json({'token': self.create_delegation_token(account.did, space)})

    def _authorize_write(self, request: httpx.Request, origin: str) -> t.Dict[str, t.Any]:
        account = self._authenticate_account(request, origin)
        body: t.Dict[str, t.Any] = json.loads(request.content)
        _parse_space(body['space'])
        if body['repo'] != account.did:
            raise _XrpcFailure(403, 'Forbidden', 'repo must match authenticated user')

        return body

    @staticmethod
    def _prepare_record(collection: str, record: t.Dict[str, t.Any], validate: t.Optional[bool]) -> t.Dict[str, t.Any]:
        record_type = record.get('$type', collection)
        if record_type != collection:
            raise _XrpcFailure(400, 'InvalidRequest', f'Invalid $type: expected {collection}, got {record_type}')

        # the network knows no lexicon to validate a record with
        if validate:
            raise _XrpcFailure(400, 'InvalidRequest', f'Unknown lexicon type: {collection}')

        return {**record, '$type': collection}

    @staticmethod
    def _build_write_output(body: t.Mapping[str, t.Any], write: _Write, cid: t.Optional[str]) -> t.Dict[str, t.Any]:
        output = {'uri': f'{body["space"]}/{body["repo"]}/{write.collection}/{write.rkey}', 'cid': cid}
        if body.get('validate') is None:
            output['validationStatus'] = 'unknown'

        return output

    def _write_record(self, body: t.Mapping[str, t.Any], action: str, rkey: str) -> httpx.Response:
        record = self._prepare_record(body['collection'], body['record'], body.get('validate'))
        write = _Write(action, body['collection'], rkey, record)
        cids = self._apply_writes(body['space'], body['repo'], [write])

        return _json(self._build_write_output(body, write, cids[0]))

    def _create_record(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = self._authorize_write(request, origin)
        return self._write_record(body, 'create', body.get('rkey') or self._next_tid())

    def _put_record(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = self._authorize_write(request, origin)
        return self._write_record(body, 'put', body['rkey'])

    def _delete_record(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = self._authorize_write(request, origin)
        path = f'{body["collection"]}/{body["rkey"]}'
        if path in self._get_records(body['space'], body['repo']):
            self._apply_writes(body['space'], body['repo'], [_Write('delete', body['collection'], body['rkey'])])

        return _json({})

    def _apply_writes_route(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = self._authorize_write(request, origin)

        writes: t.List[_Write] = []
        for item in body['writes']:
            action = _WRITE_ACTIONS.get(item.get('$type'))
            if action is None:
                raise _XrpcFailure(400, 'InvalidRequest', f'Action not supported: {item.get("$type")}')

            if action == 'delete':
                writes.append(_Write(action, item['collection'], item['rkey']))
            else:
                record = self._prepare_record(item['collection'], item['value'], body.get('validate'))
                writes.append(_Write(action, item['collection'], item.get('rkey') or self._next_tid(), record))

        cids = self._apply_writes(body['space'], body['repo'], writes)

        results: t.List[t.Dict[str, t.Any]] = []
        for write, cid in zip(writes, cids):
            result = {} if write.action == 'delete' else self._build_write_output(body, write, cid)
            results.append({'$type': f'{_WRITE_TYPE_PREFIX}{write.action}Result', **result})

        return _json({'results': results})

    def _clear_records(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = self._authorize_write(request, origin)

        state = self.repos.get((body['space'], body['repo']))
        if state is not None and state.records:
            state.rev = self._next_tid()
            state.records = {}
            state.ops = []
            self._record_writer(body['space'], body['repo'])

        return _json({})

    def _create_session(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = json.loads(request.content)
        account = self.accounts.get(body['identifier'])
        if account is None or account.pds != origin or body['password'] != _PASSWORD:
            raise _XrpcFailure(401, 'AuthenticationRequired', 'Invalid identifier or password')

        # a client reads the expiration of its session from the access token
        account.access_token = sign_jwt(
            {'typ': 'at+jwt'},
            {'sub': account.did, 'exp': int(time.time()) + _ACCESS_TOKEN_LIFETIME, 'jti': secrets.token_hex(16)},
            account.signing_key,
        )

        return _json(
            {
                'did': account.did,
                'handle': 'account.test',
                'accessJwt': account.access_token,
                'refreshJwt': account.access_token,
            }
        )

    def _authorize_authority(self, request: httpx.Request, origin: str, uri: str) -> Space:
        account = self._authenticate_account(request, origin)
        if _parse_space(uri).space_did != account.did:
            raise _XrpcFailure(400, 'NotAuthorized', 'Not the space authority')

        space = self.spaces.get(uri)
        if space is None:
            raise _XrpcFailure(400, 'SpaceNotFound', 'Space not found')

        return space

    def _authorize_management(self, request: httpx.Request, origin: str, uri: str, members: bool = False) -> Space:
        space = self._authorize_authority(request, origin, uri)
        if space.deleted:
            raise _XrpcFailure(400, 'SpaceNotFound', 'Space not found')

        if members and space.policy['$type'] != _MEMBERSPACE_POLICY_TYPE:
            raise _XrpcFailure(400, 'PolicyMismatch', 'Space does not have a memberspace policy')

        return space

    @staticmethod
    def _check_policy(policy: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        if policy.get('$type') not in _POLICY_TYPES:
            raise _XrpcFailure(400, 'UnsupportedPolicy', f'Unsupported policy: {policy.get("$type")}')

        return policy

    def _create_space(self, request: httpx.Request, origin: str) -> httpx.Response:
        account = self._authenticate_account(request, origin)
        body = json.loads(request.content)
        policy = self._check_policy(body['policy'])

        uri = str(SpaceRef(account.did, body['spaceType'], body.get('skey') or self._next_tid()))
        if uri in self.spaces:
            raise _XrpcFailure(400, 'SpaceAlreadyExists', 'Space already exists')

        self.spaces[uri] = Space(uri, policy=policy)

        return _json({'space': uri})

    def _get_space(self, request: httpx.Request, origin: str) -> httpx.Response:
        uri = request.url.params['space']
        space = self._authorize_management(request, origin, uri)

        return _json({'space': uri, 'policy': space.policy})

    def _update_space(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = json.loads(request.content)
        space = self._authorize_management(request, origin, body['space'])
        policy = self._check_policy(body['policy'])

        # a policy of another type keeps nothing of the previous one
        if policy['$type'] != space.policy['$type']:
            space.members.clear()
            space.restricted.clear()

        space.policy = policy

        return httpx.Response(200)

    def _delete_space(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = json.loads(request.content)
        space = self._authorize_authority(request, origin, body['space'])

        if not space.deleted:
            space.deleted = True
            # the repo of the authority goes with the space, the repos of the other accounts stay
            self.repos.pop((space.uri, _parse_space(space.uri).space_did), None)

        return httpx.Response(200)

    def _remove_writer(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = json.loads(request.content)
        space = self._authorize_management(request, origin, body['space'])

        writer = space.writers.get(body['repo'])
        if writer is not None and not writer.removed:
            self.remove_writer(space.uri, body['repo'])

        return httpx.Response(200)

    def _list_members(self, request: httpx.Request, origin: str) -> httpx.Response:
        params = request.url.params
        space = self._authorize_management(request, origin, params['space'], members=True)

        cursor = params.get('cursor', '')
        if cursor and not DID_RE.fullmatch(cursor):
            raise _XrpcFailure(400, 'InvalidCursor', 'Malformed cursor')

        dids = sorted(did for did in space.members | set(space.restricted) if did > cursor)
        dids = dids[: int(params.get('limit', 100))]

        members: t.List[t.Dict[str, t.Any]] = []
        for did in dids:
            reads, writes = space.restricted.get(did, (True, True))
            members.append({'did': did, 'read': reads, 'write': writes})

        output: t.Dict[str, t.Any] = {'members': members}
        if dids:
            output['cursor'] = dids[-1]

        return _json(output)

    def _put_members(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = json.loads(request.content)
        space = self._authorize_management(request, origin, body['space'], members=True)

        for member in body['members']:
            did, access = member['did'], (member['read'], member['write'])
            if all(access):
                space.members.add(did)
                space.restricted.pop(did, None)
            else:
                space.members.discard(did)
                space.restricted[did] = access

        return httpx.Response(200)

    def _remove_members(self, request: httpx.Request, origin: str) -> httpx.Response:
        body = json.loads(request.content)
        space = self._authorize_management(request, origin, body['space'], members=True)

        for did in body['dids']:
            space.members.discard(did)
            space.restricted.pop(did, None)

        return httpx.Response(200)


def build_network() -> FakeSpaceNetwork:
    """Build a network of three accounts, each on its own PDS, with a space of the first that the others belong to."""
    network = FakeSpaceNetwork()
    network.add_account(AUTHORITY_DID, AUTHORITY_PDS)
    network.add_account(ALICE_DID, ALICE_PDS)
    network.add_account(BOB_DID, BOB_PDS)
    network.add_space(SPACE, members=[ALICE_DID, BOB_DID])

    return network


class _FakeDidResolverBase:
    def __init__(self, network: FakeSpaceNetwork, cache: bool) -> None:
        self._network = network
        self._cache: t.Optional[t.Dict[str, DidDocument]] = {} if cache else None
        self.calls: t.List[t.Tuple[str, bool]] = []

    def _resolve(self, did: str, force_refresh: bool) -> t.Optional[DidDocument]:
        self.calls.append((did, force_refresh))

        if self._cache is not None and did in self._cache and not force_refresh:
            return self._cache[did]

        account = self._network.accounts.get(did)
        if account is None:
            return None

        did_doc = account.did_document
        if self._cache is not None:
            self._cache[did] = did_doc

        return did_doc


class _FakeDidResolver(_FakeDidResolverBase):
    def resolve(self, did: str, force_refresh: bool = False) -> t.Optional[DidDocument]:
        return self._resolve(did, force_refresh)

    def ensure_resolve(self, did: str, force_refresh: bool = False) -> DidDocument:
        did_doc = self.resolve(did, force_refresh)
        if did_doc is None:
            raise DidNotFoundError(f'Unable to resolve DID {did}')

        return did_doc


class FakeIdResolver:
    """Resolver of the accounts of the network. With the cache it keeps a DID document until it is told to refresh."""

    def __init__(self, network: FakeSpaceNetwork, cache: bool = False) -> None:
        self.did = _FakeDidResolver(network, cache)


class _AsyncFakeDidResolver(_FakeDidResolverBase):
    async def resolve(self, did: str, force_refresh: bool = False) -> t.Optional[DidDocument]:
        return self._resolve(did, force_refresh)

    async def ensure_resolve(self, did: str, force_refresh: bool = False) -> DidDocument:
        did_doc = await self.resolve(did, force_refresh)
        if did_doc is None:
            raise DidNotFoundError(f'Unable to resolve DID {did}')

        return did_doc


class AsyncFakeIdResolver:
    def __init__(self, network: FakeSpaceNetwork, cache: bool = False) -> None:
        self.did = _AsyncFakeDidResolver(network, cache)


def fake_id_resolver(network: FakeSpaceNetwork) -> 'IdResolver':
    return t.cast('IdResolver', FakeIdResolver(network))


def async_fake_id_resolver(network: FakeSpaceNetwork) -> 'AsyncIdResolver':
    return t.cast('AsyncIdResolver', AsyncFakeIdResolver(network))


def delegation_token_provider(network: FakeSpaceNetwork, did: str) -> t.Callable[[SpaceRef], str]:
    """Build the provider of a reader that reads with the delegation tokens of an account."""

    def provide(ref: SpaceRef) -> str:
        return network.create_delegation_token(did, str(ref))

    return provide


class _BearerAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self._token = token

    @te.override
    def auth_flow(self, request: httpx.Request) -> t.Generator[httpx.Request, httpx.Response, None]:
        request.headers['Authorization'] = f'Bearer {self._token}'
        yield request


class FakeAuthSession:
    """Session of an account that authenticates with a bearer token, in place of an OAuth session."""

    def __init__(self, account: Account) -> None:
        self._account = account

    @property
    def did(self) -> str:
        return self._account.did

    @property
    def pds_endpoint(self) -> str:
        return self._account.pds

    @property
    def httpx_auth(self) -> httpx.Auth:
        return _BearerAuth(self._account.access_token)


def fake_client(network: FakeSpaceNetwork, account: Account) -> Client:
    client = Client(request=Request(transport=network.transport))
    client.login_oauth(FakeAuthSession(account))

    return client


async def async_fake_client(network: FakeSpaceNetwork, account: Account) -> AsyncClient:
    client = AsyncClient(request=AsyncRequest(transport=network.async_transport))
    await client.login_oauth(FakeAuthSession(account))

    return client


def fake_password_client(network: FakeSpaceNetwork, account: Account) -> Client:
    """Log in with the password of an account. The session replaces the access token of the account."""
    client = Client(account.pds, Request(transport=network.transport))
    client.login(account.did, _PASSWORD, fetch_bsky_profile=False)

    return client


async def async_fake_password_client(network: FakeSpaceNetwork, account: Account) -> AsyncClient:
    client = AsyncClient(account.pds, AsyncRequest(transport=network.async_transport))
    await client.login(account.did, _PASSWORD, fetch_bsky_profile=False)

    return client
