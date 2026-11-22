import asyncio
import contextlib
import typing as t

import typing_extensions as te
from atproto_client.client.base import AsyncClientBase
from atproto_client.request import AsyncRequest
from atproto_client.utils import paginate
from atproto_core._effects import run_flow_async
from atproto_core._locks import KeyedLocks
from atproto_core.uri import SpaceRef

from atproto_space._reader import _SpaceReaderBase, check_request, get_written_repos, is_writer

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_identity.resolver import AsyncIdResolver

    from atproto_space.credential import SpaceCredential
    from atproto_space.models import RepoChanges, RepoHead, RepoSnapshot, SpaceRecord, Writer
    from atproto_space.space_type import SpaceType

AsyncDelegationTokenProvider = t.Callable[[SpaceRef], t.Union[t.Optional[str], t.Awaitable[t.Optional[str]]]]
AsyncClientAttestationProvider = t.Callable[[str], t.Union[str, t.Awaitable[str]]]
AsyncNotifyRegistrationProvider = t.Callable[
    [SpaceRef],
    t.Union[
        t.Optional['models.ComAtprotoSpaceAuthorizeSpaceSync.Notify'],
        t.Awaitable[t.Optional['models.ComAtprotoSpaceAuthorizeSpaceSync.Notify']],
    ],
]
AsyncCidLookup = t.Callable[[str, str], t.Union[t.Optional[str], t.Awaitable[t.Optional[str]]]]

_ALL_RECORDS_CONCURRENCY: t.Final = 4


class AsyncSpaceReader(_SpaceReaderBase):
    """Reader of a space that acts for no account. For services that sync spaces.

    A request goes to the PDS of the account whose repo it reads, or to the host of the space
    when it reads no repo. It is authorized with a space credential, which the reader requests
    from the host of the space on the first read and renews on its own.

    Warning:
        Spaces are in alpha. The methods can change together with the protocol.

    Args:
        space: URI of the space or a reference to it.
        space_type: Type of the space. The space must be of this type,
            and the records of other collections than the ones it declares are flagged as invalid.
        delegation_token_provider: Returns the delegation token of an account that reads the space,
            to exchange for a space credential. Only a space that anyone can read needs none.
            May be a coroutine function.
        client_attestation_provider: Returns a client attestation for the given audience.
            For spaces that admit certain applications only. May be a coroutine function.
        notify_registration_provider: Returns the endpoint that the host of the space notifies of updates.
            It is registered with every credential. May be a coroutine function.
        id_resolver: Identity resolver. One that caches DID documents in memory by default. Readers can share it.
        request: HTTP client of the reader. Readers can share it. It must carry no session of an account,
            so the one of a client is refused.
    """

    def __init__(
        self,
        space: t.Union[str, SpaceRef],
        space_type: t.Optional['SpaceType'] = None,
        *,
        delegation_token_provider: t.Optional[AsyncDelegationTokenProvider] = None,
        client_attestation_provider: t.Optional[AsyncClientAttestationProvider] = None,
        notify_registration_provider: t.Optional[AsyncNotifyRegistrationProvider] = None,
        id_resolver: t.Optional['AsyncIdResolver'] = None,
        request: t.Optional[AsyncRequest] = None,
    ) -> None:
        if id_resolver is None:
            from atproto_identity.cache.in_memory_cache import AsyncDidInMemoryCache
            from atproto_identity.resolver import AsyncIdResolver

            id_resolver = AsyncIdResolver(cache=AsyncDidInMemoryCache())

        super().__init__(
            space,
            space_type,
            delegation_token_provider,
            client_attestation_provider,
            notify_registration_provider,
            id_resolver,
            request if request is not None else AsyncRequest(),
        )
        self._locks: KeyedLocks[asyncio.Lock] = KeyedLocks(asyncio.Lock)

    @property
    def request(self) -> AsyncRequest:
        """HTTP client of the reader."""
        request: AsyncRequest = self._request
        return request

    async def authorize(self, renew: bool = False) -> 'SpaceCredential':
        """Get the space credential, requesting it from the host of the space when needed.

        The first read requests the credential on its own. Call this method to learn early
        whether the space grants access.

        Args:
            renew: Request a new credential even when the current one is still good.

        Returns:
            :obj:`SpaceCredential`: Space credential.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await self._authorize(renew)

    async def list_writers(
        self, limit: t.Optional[int] = None, cursor: t.Optional[str] = None
    ) -> 'models.ComAtprotoSpaceListWriters.Response':
        """List the accounts that hold a repo in the space, as the host of the space knows them.

        Args:
            limit: Maximum number of repos to list.
            cursor: Revision of the space to list the repos updated after.

        Returns:
            :obj:`models.ComAtprotoSpaceListWriters.Response`: Latest update of each repo,
            in the order of the revisions of the space.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._list_writers_flow(limit, cursor))

    async def writers(self, cursor: t.Optional[str] = None) -> t.AsyncIterator['Writer']:
        """Iterate over the accounts that hold a repo in the space, in the order of their latest update.

        A repo that was removed from the space is listed as ``RepoRemoved``. A repo that is updated
        during the iteration can be listed again, and its last entry is the current one.

        Note:
            The highest ``space_rev`` listed so far is the cursor to list the repos updated since.
            The host of a space may forget a removal after 72 hours, so with an older cursor
            list every repo and drop the ones that are not listed.

        Args:
            cursor: Revision of the space to list the repos updated after.

        Yields:
            :obj:`models.ComAtprotoSpaceDefs.RepoWrite` or :obj:`models.ComAtprotoSpaceDefs.RepoRemoved`:
            Latest update of a repo. Entries of an unknown kind are left out.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        async def fetch(params: t.Dict[str, t.Any]) -> 'models.ComAtprotoSpaceListWriters.Response':
            return await self.list_writers(cursor=params['cursor'])

        async for writer in paginate(fetch, {'cursor': cursor}).items():
            if is_writer(writer):
                yield writer

    async def list_records(
        self,
        repo: t.Optional[str] = None,
        collection: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        cursor: t.Optional[str] = None,
        exclude_values: t.Optional[bool] = None,
    ) -> 'models.ComAtprotoSpaceListRecords.Response':
        """List the records of a repo in the space.

        Note:
            Listed records are not verified against the commit of the repo.

        Args:
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.
            collection: NSID of the collection to list. Every collection by default.
            limit: Maximum number of records to list.
            cursor: Cursor of the page.
            exclude_values: List the records without their values.

        Returns:
            :obj:`models.ComAtprotoSpaceListRecords.Response`: Page of records.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._list_records_flow(repo, collection, limit, cursor, exclude_values))

    async def records(
        self, repo: t.Optional[str] = None, collection: t.Optional[str] = None
    ) -> t.AsyncIterator['SpaceRecord']:
        """Iterate over the records of a repo in the space, each flagged with whether it is valid.

        Note:
            Listed records are not verified against the commit of the repo.

        Args:
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.
            collection: NSID of the collection to list. Every collection by default.

        Yields:
            :obj:`SpaceRecord`: Record of the repo.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        repo = self._get_repo(repo)

        async def fetch(params: t.Dict[str, t.Any]) -> 'models.ComAtprotoSpaceListRecords.Response':
            return await self.list_records(repo, collection, cursor=params['cursor'])

        async for record in paginate(fetch, {'cursor': None}).items():
            yield self._classify_record(repo, record.collection, record.rkey, record.cid, record.value, collection)

    async def get_record(
        self, collection: str, rkey: str, repo: t.Optional[str] = None
    ) -> 'models.ComAtprotoSpaceGetRecord.Response':
        """Get a record of a repo in the space, verified against the MAC of its host.

        Note:
            A client gets no MAC for the repo of its account, and takes the record as its PDS sent it.

        Args:
            collection: NSID of the record collection.
            rkey: Record key.
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.

        Returns:
            :obj:`models.ComAtprotoSpaceGetRecord.Response`: Record.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account.
            :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The record failed verification.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._get_record_flow(collection, rkey, repo))

    async def get_latest_commit(self, repo: t.Optional[str] = None) -> 'models.ComAtprotoSpaceDefs.Commit':
        """Get the current commit of a repo in the space, verified against the MAC of its host.

        Note:
            A client gets no MAC for the repo of its account, so only the form of the commit is checked.

        Args:
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.

        Returns:
            :obj:`models.ComAtprotoSpaceDefs.Commit`: Commit of the repo.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account.
            :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The commit failed verification.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._get_latest_commit_flow(repo))

    async def get_blob(self, cid: str, repo: t.Optional[str] = None) -> bytes:
        """Get a blob of a repo in the space, verified against its CID.

        Note:
            A blob that its host serves as ``application/json`` fails verification: such a response is parsed.

        Args:
            cid: CID of the blob.
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.

        Returns:
            :obj:`bytes`: Content of the blob.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account,
                or the CID is not a CID of a blob.
            :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The blob failed verification.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._get_blob_flow(cid, repo))

    async def list_blobs(
        self, repo: t.Optional[str] = None, limit: t.Optional[int] = None, cursor: t.Optional[str] = None
    ) -> 'models.ComAtprotoSpaceListBlobs.Response':
        """List the CIDs of the blobs that the records of a repo in the space refer to.

        Args:
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.
            limit: Maximum number of blobs to list.
            cursor: Cursor of the page.

        Returns:
            :obj:`models.ComAtprotoSpaceListBlobs.Response`: Page of CIDs.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._list_blobs_flow(repo, limit, cursor))

    async def get_repo(self, repo: t.Optional[str] = None) -> 'RepoSnapshot':
        """Get a repo of the space in full, verified against the MAC of its host and against its commit.

        Note:
            The whole repo is read into memory. A client gets no MAC for the repo of its account,
            so the records are verified against the commit only.

        Args:
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.

        Returns:
            :obj:`RepoSnapshot`: Records of the repo, and the state to sync the repo from later.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account.
            :class:`atproto.exceptions.InvalidStarError`: The host did not answer with a STAR file.
            :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The repo failed verification.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._get_repo_flow(repo))

    async def list_repo_ops(
        self,
        repo: t.Optional[str] = None,
        since: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        cursor: t.Optional[str] = None,
        exclude_values: t.Optional[bool] = None,
    ) -> 'models.ComAtprotoSpaceListRepoOps.Response':
        """List the operation log of a repo in the space, with the current commit of the repo.

        The commit is verified against the MAC of its host.

        Note:
            The operations are not verified. :py:meth:`sync_repo` applies them to a known state of the repo.
            A client gets no MAC for the repo of its account, so only the form of the commit is checked.

        Args:
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.
            since: Revision of the repo to list the operations after.
            limit: Maximum number of operations to list.
            cursor: Cursor of the page.
            exclude_values: List the operations without the values of the records.

        Returns:
            :obj:`models.ComAtprotoSpaceListRepoOps.Response`: Page of operations.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account.
            :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The commit failed verification.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._list_repo_ops_flow(repo, since, limit, cursor, exclude_values))

    async def sync_repo(self, head: 'RepoHead', lookup: AsyncCidLookup, repo: t.Optional[str] = None) -> 'RepoChanges':
        """Bring a known state of a repo in the space up to date from the operation log of the repo.

        Every operation is checked against the known state, and the resulting state against the commit
        of the repo, which is verified against the MAC of its host.

        Args:
            head: Known state of the repo. The ``head`` that the repo was read or synced with last.
            lookup: Returns the CID of a record in the known state of the repo by its collection and record key,
                or :obj:`None` when there is no such record. May be a coroutine function.
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.

        Returns:
            :obj:`RepoChanges`: Changes of the records since the known state.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account.
            :class:`atproto_space.exceptions.RepoGapError`: The operation log does not continue the known state.
            :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The repo failed verification.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._sync_repo_flow(head, lookup, repo))

    async def pull_repo(
        self,
        head: t.Optional['RepoHead'] = None,
        lookup: t.Optional[AsyncCidLookup] = None,
        repo: t.Optional[str] = None,
    ) -> t.Union['RepoChanges', 'RepoSnapshot', None]:
        """Bring a repo in the space up to date.

        The repo is synced from its known state. It is read in full when there is no known state,
        for example on the first pull, or when the operation log does not continue the known state.

        Args:
            head: Known state of the repo, if any. The ``head`` that the repo was pulled with last.
            lookup: Returns the CID of a record in the known state of the repo by its collection and record key,
                or :obj:`None` when there is no such record. Required with the known state.
                May be a coroutine function.
            repo: DID of the account that the repo belongs to. A client reads the repo of its account by default.

        Returns:
            :obj:`RepoChanges`: Changes of the records since the known state,
            :obj:`RepoSnapshot` when the repo was read in full and its records replace every known one,
            or :obj:`None` when the host has no such repo, so every known record of it is gone.

        Raises:
            :class:`ValueError`: The repo is not given and the reader acts for no account,
                or the known state is given without the lookup.
            :class:`atproto_space.exceptions.RepoGapError`: The repo in full is older than the known state.
            :class:`atproto.exceptions.InvalidStarError`: The host did not answer with a STAR file.
            :class:`atproto_space.exceptions.SpaceRepoVerificationError`: The repo failed verification.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await run_flow_async(self._pull_repo_flow(head, lookup, repo))

    async def all_records(self) -> t.AsyncIterator['SpaceRecord']:
        """Iterate over the records of every repo in the space, each flagged with whether it is valid.

        Each repo is read in full and verified before its records are yielded. The repos that were removed
        from the space are left out, and so are the ones that are not found, taken down, suspended or deactivated.
        Up to four repos are read at a time.

        Yields:
            :obj:`SpaceRecord`: Record of the space.

        Raises:
            :class:`atproto.exceptions.InvalidStarError`: The host did not answer with a STAR file.
            :class:`atproto_space.exceptions.SpaceRepoVerificationError`: A repo failed verification.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        repos = get_written_repos([writer async for writer in self.writers()])
        for start in range(0, len(repos), _ALL_RECORDS_CONCURRENCY):
            batch = repos[start : start + _ALL_RECORDS_CONCURRENCY]
            tasks = [asyncio.ensure_future(run_flow_async(self._get_readable_repo_flow(repo))) for repo in batch]

            try:
                for repo, task in zip(batch, tasks):
                    snapshot = await task
                    if snapshot is None:
                        continue

                    for record in snapshot.records:
                        yield self._classify_record(repo, record.collection, record.rkey, record.cid, record.value)
            finally:
                # a batch that is not read to its end leaves no request running
                for task in tasks:
                    task.cancel()

                await asyncio.gather(*tasks, return_exceptions=True)

    @te.override
    def _xrpc(self, service: str) -> AsyncClientBase:
        # a client may have been given the request since the reader was built
        check_request(self._request)
        return AsyncClientBase(service, self._request)

    @te.override
    async def _authorize(
        self, renew: bool = False, rejected: t.Optional['SpaceCredential'] = None
    ) -> 'SpaceCredential':
        credential = self._get_usable_credential(renew, rejected)
        if credential is not None:
            return credential

        async with self._credential_lock():
            return await run_flow_async(self._authorize_flow(renew, rejected))

    @contextlib.asynccontextmanager
    async def _credential_lock(self) -> t.AsyncGenerator[None, None]:
        lock = self._locks.enter(self._uri)
        try:
            async with lock:
                yield
        finally:
            self._locks.leave(self._uri)
