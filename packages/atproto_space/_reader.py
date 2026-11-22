import typing as t
from dataclasses import replace

import typing_extensions as te
from atproto_client import models
from atproto_client.exceptions import ModelError, RequestErrorBase, UnauthorizedError
from atproto_client.models.common import XrpcError
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.record_registry import resolve_record_type
from atproto_client.models.string_formats import TID_RE
from atproto_client.models.utils import get_or_create, get_response_model
from atproto_core._effects import Flow, T, call, call_blocking
from atproto_core.exceptions import InvalidStarError
from atproto_core.nsid import validate_nsid
from atproto_core.uri import SpaceRef
from atproto_core.uri.space import is_record_key
from atproto_crypto.did import private_key_to_did_key
from atproto_crypto.exceptions import DidKeyError
from atproto_crypto.kem import Encapsulation, encapsulate
from cryptography.hazmat.primitives.asymmetric import ec
from pydantic import BaseModel

from atproto_space._data import (
    DAG_CBOR_CODEC,
    RAW_CODEC,
    encode_json_value,
    get_blob_cid,
    get_record_cid,
    is_sha256_cid,
    json_to_ipld,
)
from atproto_space.commit import RepoCommit, verify_commit
from atproto_space.credential import SpaceCredential
from atproto_space.exceptions import RepoGapError, SpaceIdentityError, SpaceMacError, SpaceRepoVerificationError
from atproto_space.mac import (
    COMMIT_MAC_PROFILE,
    MAC_KEM_INFO,
    RECORD_MAC_PROFILE,
    format_mac_request,
    verify_commit_mac,
    verify_record_mac,
)
from atproto_space.models import RecordChange, RepoChanges, RepoHead, RepoSnapshot, SpaceRecord, Writer
from atproto_space.repo_archive import _verify_records, read_repo_archive
from atproto_space.tokens import get_space_host_audience

if t.TYPE_CHECKING:
    from atproto_client.models.base import ParamsModelBase
    from atproto_client.request import Response
    from atproto_core.did_doc import DidDocument

    from atproto_space.space_type import SpaceType

_ACCEPT_SIGNATURE_HEADER: t.Final = 'accept-signature'

_UNAUTHENTICATED_STATUS: t.Final = 401
_SUCCESS_STATUSES: t.Final = range(200, 300)
_SPACE_DELETED_ERROR: t.Final = 'SpaceDeleted'
_REPO_NOT_FOUND_ERROR: t.Final = 'RepoNotFound'
# the errors of a host that holds no readable data of a repo
_UNREADABLE_REPO_ERRORS: t.Final = frozenset(
    {_REPO_NOT_FOUND_ERROR, 'RepoTakendown', 'RepoSuspended', 'RepoDeactivated'}
)

_TYPE_FIELD: t.Final = '$type'

_QueryResult = t.Tuple['Response', t.Optional[Encapsulation]]
_RecordResult = t.Tuple['models.ComAtprotoSpaceGetRecord.Response', t.Any]
_RepoOpsResult = t.Tuple['models.ComAtprotoSpaceListRepoOps.Response', t.List[t.Dict[str, t.Any]]]
_Pull = t.Union[RepoChanges, RepoSnapshot, None]

_VERIFICATION_ERRORS: t.Final = (SpaceMacError, SpaceRepoVerificationError)


def is_writer(entry: object) -> te.TypeGuard[Writer]:
    """Tell whether an entry of the writer set is of a kind that this version knows."""
    return isinstance(entry, (models.ComAtprotoSpaceDefs.RepoWrite, models.ComAtprotoSpaceDefs.RepoRemoved))


def get_written_repos(writers: t.Iterable[Writer]) -> t.List[str]:
    """Get the repos of the writer set of a space, without the ones that were removed from it."""
    # a repo that is listed again was updated during the listing, and its last entry is the current one
    current = {writer.repo: writer for writer in writers}
    return [repo for repo, writer in current.items() if isinstance(writer, models.ComAtprotoSpaceDefs.RepoWrite)]


def check_request(request: t.Any) -> None:
    """Check that the request of a reader carries no session of an account.

    Raises:
        :class:`ValueError`: The request has a source of authentication or an ``Authorization`` header.
    """
    # the request of a client and its clones send the session of the account to every host
    if request._auth_source is not None or 'authorization' in map(str.lower, request.get_headers()):
        raise ValueError('The request of a reader must carry no session of an account')


def _get_error_name(error: RequestErrorBase) -> t.Optional[str]:
    content = error.response.content if error.response else None
    if isinstance(content, XrpcError):
        return content.error

    # an error that has no message is left unparsed
    name = content['error'] if isinstance(content, DotDict) else None
    return name if isinstance(name, str) else None


def _is_unauthenticated(error: UnauthorizedError) -> bool:
    # the error is raised for 403 as well, which a new credential does not help against
    return error.response is not None and error.response.status_code == _UNAUTHENTICATED_STATUS


def _is_unparsed(error: RequestErrorBase) -> bool:
    """Tell whether the error is a response of success with a body that is not the JSON it is declared to be."""
    return error.response is not None and error.response.status_code in _SUCCESS_STATUSES


def get_record_type(value: t.Any) -> t.Optional[str]:
    record_type: object = None
    if isinstance(value, BaseModel):
        record_type = getattr(value, 'py_type', None)
    elif isinstance(value, (dict, DotDict)) and _TYPE_FIELD in value:
        record_type = value[_TYPE_FIELD]

    return record_type if isinstance(record_type, str) else None


def _load_record(collection: str, value: t.Any) -> t.Any:
    """Parse a record into the model that is registered for its collection, if there is one."""
    if isinstance(value, BaseModel):
        return value

    model = resolve_record_type(collection)
    try:
        if model is None:
            return value if isinstance(value, DotDict) else DotDict(value)

        return get_or_create(value.to_dict() if isinstance(value, DotDict) else value, model)
    except RecursionError as e:
        raise ModelError('Record is nested too deep') from e


def _has_cid(value: t.Any, cid: str) -> bool:
    try:
        return get_record_cid(encode_json_value(value)) == cid
    except ValueError:
        # a value outside of the data model has no CID
        return False


def _load_repo_value(value: t.Any, cid: t.Optional[str]) -> t.Optional[t.Dict[str, t.Any]]:
    """Convert a record to the form that a repo archive holds it in, if it is a map that has the CID."""
    if not cid or not _has_cid(value, cid):
        return None

    try:
        return json_to_ipld(value)
    except ValueError:
        # a link and a byte string have a CID as well
        return None


def _is_valid_op(op: 'models.ComAtprotoSpaceListRepoOps.OpEntry') -> bool:
    """Tell whether the fields of an operation have the formats that the lexicon declares for them."""
    return (
        validate_nsid(op.collection, soft_fail=True)
        and is_record_key(op.rkey)
        and TID_RE.fullmatch(op.rev) is not None
        and all(cid is None or is_sha256_cid(cid, DAG_CBOR_CODEC) for cid in (op.cid, op.prev))
    )


def _get_kem_key(did_doc: 'DidDocument') -> t.Optional[str]:
    """Get the DID key of ``#atproto_kem`` of a DID document, if it is a key that a MAC can be keyed with."""
    try:
        kem_key = did_doc.get_kem_key()
        if kem_key is not None:
            encapsulate(kem_key, MAC_KEM_INFO)
    except (ValueError, DidKeyError):
        return None

    return kem_key


def _verify_record(
    response: 'Response', uri: str, encapsulation: Encapsulation
) -> 'models.ComAtprotoSpaceGetRecord.Response':
    """Verify that a response holds the requested record and that its host vouches for it with the MAC.

    Raises:
        :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The response holds another record,
            or the value of the record does not match its CID.
        :class:`atproto_space.exceptions.SpaceMacError`: The MAC is missing, malformed or wrong,
            or it covers another record.
    """
    record = get_response_model(response, models.ComAtprotoSpaceGetRecord.Response)
    if record.uri != uri:
        raise SpaceRepoVerificationError(f'Record is not the one requested: {record.uri}')

    if not is_sha256_cid(record.cid, DAG_CBOR_CODEC):
        raise SpaceRepoVerificationError(f'Invalid record CID: {record.cid}')

    verify_record_mac(uri, record.cid, encapsulation, response.headers)

    # a model does not keep every field of a record the way it was received
    value = t.cast('t.Dict[str, t.Any]', response.content)['value']
    if not _has_cid(value, record.cid):
        raise SpaceRepoVerificationError('Record value does not match its CID')

    return record


def _verified_flow(message: str, attempt: t.Callable[[bool], Flow[T]]) -> Flow[T]:
    """Run a read that verifies its response, and once more when the verification fails.

    Args:
        message: Message of the error to raise when the verification fails again.
        attempt: Read to run. Takes whether to resolve the KEM key of the repo without the cache.

    Raises:
        :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The verification failed twice,
            or the response could not be parsed.
    """
    try:
        try:
            return (yield from attempt(False))
        except _VERIFICATION_ERRORS:
            # the KEM key may have been rotated after the DID document was cached
            return (yield from attempt(True))
    except _VERIFICATION_ERRORS as e:
        raise SpaceRepoVerificationError(message) from e
    except RequestErrorBase as e:
        if not _is_unparsed(e):
            raise

        raise SpaceRepoVerificationError(message) from e


class _SpaceReaderBase:
    def __init__(
        self,
        space: t.Union[str, SpaceRef],
        space_type: t.Optional['SpaceType'],
        delegation_token_provider: t.Optional[t.Callable[[SpaceRef], t.Any]],
        client_attestation_provider: t.Optional[t.Callable[[str], t.Any]],
        notify_registration_provider: t.Optional[t.Callable[[SpaceRef], t.Any]],
        id_resolver: t.Any,
        request: t.Any,
    ) -> None:
        ref = SpaceRef.from_str(space) if isinstance(space, str) else space
        if space_type is not None and ref.space_type != space_type.nsid:
            raise ValueError(f'{ref} is not a {space_type.nsid} space')

        check_request(request)

        self._ref = ref
        self._uri = str(ref)
        self._space_type = space_type
        self._delegation_token_provider = delegation_token_provider
        self._client_attestation_provider = client_attestation_provider
        self._notify_registration_provider = notify_registration_provider
        self._id_resolver = id_resolver
        self._request = request

        self._credential: t.Optional[SpaceCredential] = None

    @property
    def ref(self) -> SpaceRef:
        """Reference to the space."""
        return self._ref

    @property
    def uri(self) -> str:
        """URI of the space."""
        return self._uri

    @property
    def space_type(self) -> t.Optional['SpaceType']:
        """Type of the space, when the reader was given one."""
        return self._space_type

    def _xrpc(self, service: str) -> t.Any:
        """Build a client of a host on the request of the reader, which carries no session."""
        raise NotImplementedError

    def _authorize(self, renew: bool = False, rejected: t.Optional[SpaceCredential] = None) -> t.Any:
        """Get the space credential, taking the credential lock when a new one has to be requested."""
        raise NotImplementedError

    def _get_repo(self, repo: t.Optional[str]) -> str:
        if repo is None:
            raise ValueError('The repo to read is required')

        return repo

    def _get_account_client(self, repo: str) -> t.Any:
        """Get the client of the account that a repo belongs to, when the reader acts for that account."""
        return None

    def _get_usable_credential(self, renew: bool, rejected: t.Optional[SpaceCredential]) -> t.Optional[SpaceCredential]:
        credential = self._credential
        if credential is None or renew or credential is rejected or credential.needs_renewal:
            return None

        return credential

    def _authorize_flow(self, renew: bool, rejected: t.Optional[SpaceCredential]) -> Flow[SpaceCredential]:
        """Get the space credential, requesting a new one when needed. Runs under the credential lock."""
        # another caller may have replaced the credential while this one waited for the lock
        credential = self._get_usable_credential(renew, rejected)
        if credential is not None:
            return credential

        try:
            credential = yield from self._mint_flow(renew or rejected is not None)
        except RequestErrorBase as e:
            if _get_error_name(e) == _SPACE_DELETED_ERROR:
                self._credential = None

            raise

        self._credential = credential

        return credential

    def _mint_flow(self, refresh: bool) -> Flow[SpaceCredential]:
        service = yield from self._resolve_pds_flow(self._ref.space_did, refresh)

        delegation_token = client_attestation = notify = None
        if self._delegation_token_provider is not None:
            delegation_token = yield call(self._delegation_token_provider, self._ref)
        if self._client_attestation_provider is not None:
            audience = get_space_host_audience(self._ref.space_did)
            client_attestation = yield call(self._client_attestation_provider, audience)
        if self._notify_registration_provider is not None:
            notify = yield call(self._notify_registration_provider, self._ref)

        # every credential is bound to a key of its own
        private_key = ec.generate_private_key(ec.SECP256R1())
        data = models.ComAtprotoSpaceAuthorizeSpaceSync.Data(
            space=self._uri,
            credential_key=private_key_to_did_key(private_key),
            delegation_token=delegation_token,
            client_attestation=client_attestation,
            notify=notify,
        )
        response = yield call(
            self._xrpc(service).invoke_procedure,
            'com.atproto.space.authorizeSpaceSync',
            data=data,
            input_encoding='application/json',
        )
        output = get_response_model(response, models.ComAtprotoSpaceAuthorizeSpaceSync.Response)

        return SpaceCredential.parse(output.credential, private_key, output.space_rev)

    def _resolve_pds_flow(self, did: str, refresh: bool) -> Flow[str]:
        did_doc: DidDocument = yield call(self._id_resolver.did.ensure_resolve, did, refresh)

        endpoint = did_doc.get_pds_endpoint()
        if endpoint is None:
            raise SpaceIdentityError(f'DID document of {did} has no PDS endpoint')

        return endpoint

    def _resolve_kem_key_flow(self, did: str, refresh: bool) -> Flow[str]:
        did_doc: DidDocument = yield call(self._id_resolver.did.ensure_resolve, did, refresh)

        kem_key = _get_kem_key(did_doc)
        if kem_key is None and not refresh:
            # the key may have been added or replaced after the DID document was cached
            did_doc = yield call(self._id_resolver.did.ensure_resolve, did, True)
            kem_key = _get_kem_key(did_doc)

        if kem_key is None:
            raise SpaceIdentityError(f'DID document of {did} has no usable #atproto_kem key')

        return kem_key

    def _credentialed_query_flow(
        self,
        audience: str,
        nsid: str,
        params: 'ParamsModelBase',
        mac_profile: t.Optional[str] = None,
        kem_key: t.Optional[str] = None,
    ) -> Flow[_QueryResult]:
        """Query the PDS of the audience with the space credential, renewing a credential that it rejects.

        Args:
            audience: DID of the repo for the methods of a repo, DID of the space authority for the methods of a space.
            nsid: NSID of the method.
            params: Parameters of the method.
            mac_profile: Profile of the MAC to ask the host for.
            kem_key: DID key of ``#atproto_kem`` of the audience, which keys the MAC.

        Returns:
            The response, and the encapsulation that the MAC of the response is verified with.
        """
        # resolved before the credential, so that an audience without a PDS costs no credential
        service = yield from self._resolve_pds_flow(audience, False)
        credential: SpaceCredential = yield call(self._authorize)

        try:
            return (yield from self._send_query_flow(service, credential, audience, nsid, params, mac_profile, kem_key))
        except UnauthorizedError as e:
            if not _is_unauthenticated(e):
                raise

        service = yield from self._resolve_pds_flow(audience, True)
        credential = yield call(self._authorize, False, credential)

        return (yield from self._send_query_flow(service, credential, audience, nsid, params, mac_profile, kem_key))

    def _send_query_flow(
        self,
        service: str,
        credential: SpaceCredential,
        audience: str,
        nsid: str,
        params: 'ParamsModelBase',
        mac_profile: t.Optional[str],
        kem_key: t.Optional[str],
    ) -> Flow[_QueryResult]:
        headers = credential.headers(audience)

        encapsulation = None
        if mac_profile and kem_key:
            # a key share keys one MAC, so every attempt gets its own
            encapsulation = encapsulate(kem_key, MAC_KEM_INFO)
            headers[_ACCEPT_SIGNATURE_HEADER] = format_mac_request(mac_profile, encapsulation.key_share)

        response: Response = yield call(self._xrpc(service).invoke_query, nsid, params=params, headers=headers)

        return response, encapsulation

    def _repo_query_flow(self, repo: str, nsid: str, params: 'ParamsModelBase') -> Flow['Response']:
        """Query the PDS of a repo, as its account when the reader acts for it, with the space credential otherwise."""
        client = self._get_account_client(repo)
        if client is not None:
            response: Response = yield call(client.invoke_query, nsid, params=params)
        else:
            response, _ = yield from self._credentialed_query_flow(repo, nsid, params)

        return response

    def _mac_query_flow(
        self, repo: str, nsid: str, params: 'ParamsModelBase', mac_profile: str, refresh_kem_key: bool
    ) -> Flow[_QueryResult]:
        """Query the PDS of a repo for a response that carries a MAC.

        A reader that acts for the account of the repo asks as the account, and asks for no MAC.

        Args:
            repo: DID of the account that the repo belongs to.
            nsid: NSID of the method.
            params: Parameters of the method.
            mac_profile: Profile of the MAC to ask the host for.
            refresh_kem_key: Resolve the KEM key of the account without the cache.

        Returns:
            The response, and the encapsulation that the MAC of the response is verified with, if one was asked for.
        """
        client = self._get_account_client(repo)
        if client is not None:
            response: Response = yield call(client.invoke_query, nsid, params=params)
            return response, None

        kem_key = yield from self._resolve_kem_key_flow(repo, refresh_kem_key)

        return (yield from self._credentialed_query_flow(repo, nsid, params, mac_profile, kem_key))

    def _verify_repo_commit(
        self,
        commit: 'models.ComAtprotoSpaceDefs.Commit',
        repo: str,
        response: 'Response',
        encapsulation: t.Optional[Encapsulation],
    ) -> None:
        """Verify the commit of a repo, and the MAC of its host when the host was asked for one."""
        verify_commit(commit, self._uri, repo)
        if encapsulation is not None:
            verify_commit_mac(commit, encapsulation, response.headers)

    def _list_writers_flow(
        self, limit: t.Optional[int], cursor: t.Optional[str]
    ) -> Flow['models.ComAtprotoSpaceListWriters.Response']:
        params = models.ComAtprotoSpaceListWriters.Params(space=self._uri, limit=limit, cursor=cursor)
        response, _ = yield from self._credentialed_query_flow(
            self._ref.space_did, 'com.atproto.space.listWriters', params
        )

        return get_response_model(response, models.ComAtprotoSpaceListWriters.Response)

    def _list_records_flow(
        self,
        repo: t.Optional[str],
        collection: t.Optional[str],
        limit: t.Optional[int],
        cursor: t.Optional[str],
        exclude_values: t.Optional[bool],
    ) -> Flow['models.ComAtprotoSpaceListRecords.Response']:
        repo = self._get_repo(repo)
        params = models.ComAtprotoSpaceListRecords.Params(
            space=self._uri,
            repo=repo,
            collection=collection,
            limit=limit,
            cursor=cursor,
            exclude_values=exclude_values,
        )
        response = yield from self._repo_query_flow(repo, 'com.atproto.space.listRecords', params)

        return get_response_model(response, models.ComAtprotoSpaceListRecords.Response)

    def _get_record_flow(
        self, collection: str, rkey: str, repo: t.Optional[str]
    ) -> Flow['models.ComAtprotoSpaceGetRecord.Response']:
        record, _ = yield from self._verified_record_flow(self._get_repo(repo), collection, rkey)

        return record

    def _verified_record_flow(self, repo: str, collection: str, rkey: str) -> Flow[_RecordResult]:
        """Get a record of a repo, verified, together with its value in the JSON form that it was received in."""
        params = models.ComAtprotoSpaceGetRecord.Params(space=self._uri, repo=repo, collection=collection, rkey=rkey)
        uri = f'{self._uri}/{repo}/{collection}/{rkey}'

        def attempt(refresh_kem_key: bool) -> Flow[_RecordResult]:
            response, encapsulation = yield from self._mac_query_flow(
                repo, 'com.atproto.space.getRecord', params, RECORD_MAC_PROFILE, refresh_kem_key
            )
            if encapsulation is None:
                # an account takes the records of its own repo from its PDS as they are
                record = get_response_model(response, models.ComAtprotoSpaceGetRecord.Response)
            else:
                record = _verify_record(response, uri, encapsulation)

            return record, t.cast('t.Dict[str, t.Any]', response.content)['value']

        return (yield from _verified_flow(f'Record {uri} failed verification', attempt))

    def _get_latest_commit_flow(self, repo: t.Optional[str]) -> Flow['models.ComAtprotoSpaceDefs.Commit']:
        repo = self._get_repo(repo)
        params = models.ComAtprotoSpaceGetLatestCommit.Params(space=self._uri, repo=repo)

        def attempt(refresh_kem_key: bool) -> Flow['models.ComAtprotoSpaceDefs.Commit']:
            response, encapsulation = yield from self._mac_query_flow(
                repo, 'com.atproto.space.getLatestCommit', params, COMMIT_MAC_PROFILE, refresh_kem_key
            )
            commit = get_response_model(response, models.ComAtprotoSpaceGetLatestCommit.Response).commit
            self._verify_repo_commit(commit, repo, response, encapsulation)

            return commit

        return (yield from _verified_flow(f'Repo {repo} commit failed verification', attempt))

    def _get_blob_flow(self, cid: str, repo: t.Optional[str]) -> Flow[bytes]:
        repo = self._get_repo(repo)
        if not is_sha256_cid(cid, RAW_CODEC):
            raise ValueError(f'{cid} is not a CID of a blob')

        params = models.ComAtprotoSpaceGetBlob.Params(space=self._uri, repo=repo, cid=cid)
        try:
            response = yield from self._repo_query_flow(repo, 'com.atproto.space.getBlob', params)
        except RequestErrorBase as e:
            if not _is_unparsed(e):
                raise

            raise SpaceRepoVerificationError(f'Blob {cid} failed verification') from e

        blob = response.content
        if not isinstance(blob, bytes) or get_blob_cid(blob) != cid:
            raise SpaceRepoVerificationError(f'Blob {cid} failed verification')

        return blob

    def _list_blobs_flow(
        self, repo: t.Optional[str], limit: t.Optional[int], cursor: t.Optional[str]
    ) -> Flow['models.ComAtprotoSpaceListBlobs.Response']:
        repo = self._get_repo(repo)
        params = models.ComAtprotoSpaceListBlobs.Params(space=self._uri, repo=repo, limit=limit, cursor=cursor)
        response = yield from self._repo_query_flow(repo, 'com.atproto.space.listBlobs', params)

        return get_response_model(response, models.ComAtprotoSpaceListBlobs.Response)

    def _get_repo_flow(self, repo: t.Optional[str]) -> Flow[RepoSnapshot]:
        repo = self._get_repo(repo)
        params = models.ComAtprotoSpaceGetRepo.Params(space=self._uri, repo=repo)

        def attempt(refresh_kem_key: bool) -> Flow[RepoSnapshot]:
            response, encapsulation = yield from self._mac_query_flow(
                repo, 'com.atproto.space.getRepo', params, COMMIT_MAC_PROFILE, refresh_kem_key
            )
            # the records of a large repo take seconds to hash
            snapshot: RepoSnapshot = yield call_blocking(self._load_snapshot, repo, response, encapsulation)

            return snapshot

        return (yield from _verified_flow(f'Repo {repo} failed verification', attempt))

    def _load_snapshot(self, repo: str, response: 'Response', encapsulation: t.Optional[Encapsulation]) -> RepoSnapshot:
        """Read the repo that a response holds, verified against its commit and the MAC of its host."""
        if not isinstance(response.content, bytes):
            raise InvalidStarError('Invalid STAR file. Expected a binary response.')

        archive, commit = read_repo_archive(response.content)
        self._verify_repo_commit(commit, repo, response, encapsulation)
        records, repo_commit = _verify_records(archive, commit)

        return RepoSnapshot(commit, RepoHead(commit.rev, repo_commit.state), records)

    def _get_readable_repo_flow(self, repo: str) -> Flow[t.Optional[RepoSnapshot]]:
        """Get a repo in full, unless its host holds no readable data of it."""
        try:
            return (yield from self._get_repo_flow(repo))
        except RequestErrorBase as e:
            if _get_error_name(e) not in _UNREADABLE_REPO_ERRORS:
                raise

        return None

    def _list_repo_ops_flow(
        self,
        repo: t.Optional[str],
        since: t.Optional[str],
        limit: t.Optional[int],
        cursor: t.Optional[str],
        exclude_values: t.Optional[bool],
    ) -> Flow['models.ComAtprotoSpaceListRepoOps.Response']:
        page, _ = yield from self._repo_ops_flow(self._get_repo(repo), since, limit, cursor, exclude_values)

        return page

    def _repo_ops_flow(
        self,
        repo: str,
        since: t.Optional[str],
        limit: t.Optional[int],
        cursor: t.Optional[str],
        exclude_values: t.Optional[bool],
    ) -> Flow[_RepoOpsResult]:
        """List a page of the operation log of a repo, together with the operations in the JSON form."""
        params = models.ComAtprotoSpaceListRepoOps.Params(
            space=self._uri,
            repo=repo,
            since=since,
            limit=limit,
            cursor=cursor,
            exclude_values=exclude_values,
        )

        def attempt(refresh_kem_key: bool) -> Flow[_RepoOpsResult]:
            response, encapsulation = yield from self._mac_query_flow(
                repo, 'com.atproto.space.listRepoOps', params, COMMIT_MAC_PROFILE, refresh_kem_key
            )
            page = get_response_model(response, models.ComAtprotoSpaceListRepoOps.Response)
            self._verify_repo_commit(page.commit, repo, response, encapsulation)

            return page, t.cast('t.Dict[str, t.Any]', response.content)['ops']

        return (yield from _verified_flow(f'Repo {repo} commit failed verification', attempt))

    def _sync_repo_flow(
        self, head: RepoHead, lookup: t.Callable[[str, str], t.Any], repo: t.Optional[str]
    ) -> Flow[RepoChanges]:
        repo = self._get_repo(repo)
        repo_commit = RepoCommit(head.state)
        changes: t.Dict[str, RecordChange] = {}

        rev = head.rev
        cursor: t.Optional[str] = None
        cursors: t.Set[str] = set()
        while True:
            page, ops = yield from self._repo_ops_flow(repo, head.rev, None, cursor, None)

            for op, op_json in zip(page.ops, ops):
                if not _is_valid_op(op):
                    raise SpaceRepoVerificationError(f'Repo {repo} returned an invalid operation')

                # the operations of one commit share a revision
                if op.rev <= head.rev or op.rev < rev:
                    raise RepoGapError(f'Repo {repo} operations are out of order')

                rev = op.rev
                yield from self._merge_op_flow(repo, op, op_json.get('value'), changes, lookup)
                repo_commit.apply(op.collection, op.rkey, op.cid, op.prev)

            # every page holds the current commit of the repo, and the one of the last page counts
            commit = page.commit
            # a page without operations or a repeated cursor would loop forever
            if not page.cursor or not page.ops or page.cursor in cursors:
                break

            cursors.add(page.cursor)
            cursor = page.cursor

        if not repo_commit.matches(commit):
            raise RepoGapError(f'Repo {repo} diverged from its commit')

        synced: t.List[RecordChange] = []
        for change in changes.values():
            if change.cid and change.value is None:
                # a value is listed only with the last operation on its record
                synced.append((yield from self._load_change_flow(repo, change)))
            elif change.cid or change.prev:
                # a record that was created and then deleted did not change
                synced.append(change)

        return RepoChanges(commit, RepoHead(commit.rev, repo_commit.state), synced)

    def _merge_op_flow(
        self,
        repo: str,
        op: 'models.ComAtprotoSpaceListRepoOps.OpEntry',
        value: t.Any,
        changes: t.Dict[str, RecordChange],
        lookup: t.Callable[[str, str], t.Any],
    ) -> Flow[None]:
        """Check an operation against the known state of its record and merge it into the change of the record."""
        path = f'{op.collection}/{op.rkey}'

        change = changes.get(path)
        current = change.cid if change is not None else (yield call(lookup, op.collection, op.rkey))
        if op.prev != current:
            raise RepoGapError(f'Repo {repo} diverged at {path}')

        if value is not None:
            value = _load_repo_value(value, op.cid)
            if value is None:
                raise SpaceRepoVerificationError(f'Record {path} failed verification')

        prev = change.prev if change is not None else op.prev
        changes[path] = RecordChange(op.collection, op.rkey, op.cid, prev, value)

    def _load_change_flow(self, repo: str, change: RecordChange) -> Flow[RecordChange]:
        record, value = yield from self._verified_record_flow(repo, change.collection, change.rkey)
        if record.cid != change.cid:
            raise RepoGapError(f'Repo {repo} changed while syncing')

        value = _load_repo_value(value, record.cid)
        if value is None:
            raise SpaceRepoVerificationError(f'Record {change.collection}/{change.rkey} failed verification')

        return replace(change, value=value)

    def _pull_repo_flow(
        self, head: t.Optional[RepoHead], lookup: t.Optional[t.Callable[[str, str], t.Any]], repo: t.Optional[str]
    ) -> Flow[_Pull]:
        repo = self._get_repo(repo)
        if head is not None and lookup is None:
            raise ValueError('The lookup of the known records is required to pull from a known state')

        try:
            if head is not None and lookup is not None:
                try:
                    return (yield from self._sync_repo_flow(head, lookup, repo))
                except (RepoGapError, SpaceRepoVerificationError):
                    # the repo in full replaces a state that the operation log does not continue
                    pass

            snapshot = yield from self._get_repo_flow(repo)
        except RequestErrorBase as e:
            if _get_error_name(e) != _REPO_NOT_FOUND_ERROR:
                raise

            return None

        if head is not None and snapshot.commit.rev < head.rev:
            raise RepoGapError(f'Repo {repo} is older than its known state')

        return snapshot

    def _classify_record(
        self, repo: str, collection: str, rkey: str, cid: str, value: t.Any, listed: t.Optional[str] = None
    ) -> SpaceRecord:
        """Flag a record with whether it is valid.

        Args:
            repo: DID of the account that the record belongs to.
            collection: NSID of the collection that the record is stored under.
            rkey: Record key.
            cid: CID of the record.
            value: Record, if its host returned it.
            listed: NSID of the collection that was listed, when the records of one were asked for.
        """
        try:
            valid_value = self._validate_record(collection, value, listed)
        except ModelError as e:
            return SpaceRecord(repo, collection, rkey, cid, value, False, e)

        return SpaceRecord(repo, collection, rkey, cid, valid_value, True)

    def _validate_record(self, collection: str, value: t.Any, listed: t.Optional[str]) -> t.Any:
        if value is None:
            raise ModelError('Record has no value')

        record_type = get_record_type(value)
        if record_type is None:
            raise ModelError('Record has no type')

        # not every host checks that a record is stored under the collection of its type
        if record_type != collection:
            raise ModelError(f'Record of type {record_type} is stored under collection {collection}')

        if listed is not None and collection != listed:
            raise ModelError(f'Record of collection {collection} is listed under collection {listed}')

        if self._space_type is not None and collection not in self._space_type.collections:
            raise ModelError(f'{collection} is not a collection of {self._space_type.nsid} spaces')

        return _load_record(collection, value)
