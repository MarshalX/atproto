import typing as t

from atproto_client import models
from atproto_client.utils import paginate
from atproto_core.uri import SpaceRef

from atproto_space._client import get_account_did

if t.TYPE_CHECKING:
    from atproto_client import AsyncClient, Client

    from atproto_space.models import SpacePolicy


class _SpaceManagerBase:
    def __init__(self, client: t.Any, space: t.Union[str, SpaceRef]) -> None:
        ref = SpaceRef.from_str(space) if isinstance(space, str) else space
        if get_account_did(client) != ref.space_did:
            raise ValueError(f'Only the space authority ({ref.space_did}) can manage {ref}')

        self._client = client
        self._ref = ref
        self._uri = str(ref)

    @property
    def ref(self) -> SpaceRef:
        """Reference to the space."""
        return self._ref

    @property
    def uri(self) -> str:
        """URI of the space."""
        return self._uri


class SpaceManager(_SpaceManagerBase):
    """Manager of a space that acts for its authority: the policy of the space, its writers and its members.

    Only the authority of a space manages it, so the client must be logged in as the account
    that the URI of the space names.

    Warning:
        Spaces are in alpha. The methods can change together with the protocol.

    Args:
        client: Client that is logged in as the authority of the space.
        space: URI of the space or a reference to it.
    """

    def __init__(self, client: 'Client', space: t.Union[str, SpaceRef]) -> None:
        super().__init__(client, space)

    @property
    def client(self) -> 'Client':
        """Client of the authority of the space."""
        client: Client = self._client
        return client

    def get_space(self) -> 'models.ComAtprotoSpaceGetSpace.Response':
        """Get the space with the policy that governs it.

        Returns:
            :obj:`models.ComAtprotoSpaceGetSpace.Response`: Space and its policy.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return self.client.com.atproto.space.get_space(models.ComAtprotoSpaceGetSpace.Params(space=self._uri))

    def update_space(self, policy: 'SpacePolicy') -> bool:
        """Replace the policy of the space as a whole.

        Note:
            A policy of another type discards the state of the previous one, such as a member list.

        Args:
            policy: Policy to govern the space.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return self.client.com.atproto.space.update_space(
            models.ComAtprotoSpaceUpdateSpace.Data(space=self._uri, policy=policy)
        )

    def delete_space(self) -> bool:
        """Delete the space, along with the repo of its authority in it. The repos of other accounts are left.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return self.client.com.atproto.space.delete_space(models.ComAtprotoSpaceDeleteSpace.Data(space=self._uri))

    def remove_writer(self, repo: str) -> bool:
        """Remove the repo of an account from the writer set of the space.

        Note:
            The repo is added back when the account writes to the space again and the policy lets it.

        Args:
            repo: DID of the account that the repo belongs to.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return self.client.com.atproto.space.remove_writer(
            models.ComAtprotoSpaceRemoveWriter.Data(space=self._uri, repo=repo)
        )

    def list_members(
        self, limit: t.Optional[int] = None, cursor: t.Optional[str] = None
    ) -> 'models.ComAtprotoMemberspaceListMembers.Response':
        """List the members of the space. For a space that a member list governs.

        Args:
            limit: Maximum number of members to list.
            cursor: Cursor of the page.

        Returns:
            :obj:`models.ComAtprotoMemberspaceListMembers.Response`: Page of members.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return self.client.com.atproto.memberspace.list_members(
            models.ComAtprotoMemberspaceListMembers.Params(space=self._uri, limit=limit, cursor=cursor)
        )

    def members(self) -> t.Iterator['models.ComAtprotoMemberspaceDefs.Member']:
        """Iterate over the members of the space. For a space that a member list governs.

        Yields:
            :obj:`models.ComAtprotoMemberspaceDefs.Member`: Member with its access to the space.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        def fetch(params: t.Dict[str, t.Any]) -> 'models.ComAtprotoMemberspaceListMembers.Response':
            return self.list_members(cursor=params['cursor'])

        yield from paginate(fetch, {'cursor': None}).items()

    def put_members(self, members: t.Sequence['models.ComAtprotoMemberspaceDefs.Member']) -> bool:
        """Add members to the space, or replace the access of the ones it has. For a space that a member list governs.

        Args:
            members: Members with their access to the space, 100 at most. The last entry of an account counts.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return self.client.com.atproto.memberspace.put_members(
            models.ComAtprotoMemberspacePutMembers.Data(space=self._uri, members=list(members))
        )

    def remove_members(self, dids: t.Sequence[str]) -> bool:
        """Remove members from the space. For a space that a member list governs.

        Args:
            dids: DIDs of the members, 100 at most. The ones of other accounts are ignored.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return self.client.com.atproto.memberspace.remove_members(
            models.ComAtprotoMemberspaceRemoveMembers.Data(space=self._uri, dids=list(dids))
        )


class AsyncSpaceManager(_SpaceManagerBase):
    """Manager of a space that acts for its authority: the policy of the space, its writers and its members.

    Only the authority of a space manages it, so the client must be logged in as the account
    that the URI of the space names.

    Warning:
        Spaces are in alpha. The methods can change together with the protocol.

    Args:
        client: Client that is logged in as the authority of the space.
        space: URI of the space or a reference to it.
    """

    def __init__(self, client: 'AsyncClient', space: t.Union[str, SpaceRef]) -> None:
        super().__init__(client, space)

    @property
    def client(self) -> 'AsyncClient':
        """Client of the authority of the space."""
        client: AsyncClient = self._client
        return client

    async def get_space(self) -> 'models.ComAtprotoSpaceGetSpace.Response':
        """Get the space with the policy that governs it.

        Returns:
            :obj:`models.ComAtprotoSpaceGetSpace.Response`: Space and its policy.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await self.client.com.atproto.space.get_space(models.ComAtprotoSpaceGetSpace.Params(space=self._uri))

    async def update_space(self, policy: 'SpacePolicy') -> bool:
        """Replace the policy of the space as a whole.

        Note:
            A policy of another type discards the state of the previous one, such as a member list.

        Args:
            policy: Policy to govern the space.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await self.client.com.atproto.space.update_space(
            models.ComAtprotoSpaceUpdateSpace.Data(space=self._uri, policy=policy)
        )

    async def delete_space(self) -> bool:
        """Delete the space, along with the repo of its authority in it. The repos of other accounts are left.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await self.client.com.atproto.space.delete_space(models.ComAtprotoSpaceDeleteSpace.Data(space=self._uri))

    async def remove_writer(self, repo: str) -> bool:
        """Remove the repo of an account from the writer set of the space.

        Note:
            The repo is added back when the account writes to the space again and the policy lets it.

        Args:
            repo: DID of the account that the repo belongs to.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await self.client.com.atproto.space.remove_writer(
            models.ComAtprotoSpaceRemoveWriter.Data(space=self._uri, repo=repo)
        )

    async def list_members(
        self, limit: t.Optional[int] = None, cursor: t.Optional[str] = None
    ) -> 'models.ComAtprotoMemberspaceListMembers.Response':
        """List the members of the space. For a space that a member list governs.

        Args:
            limit: Maximum number of members to list.
            cursor: Cursor of the page.

        Returns:
            :obj:`models.ComAtprotoMemberspaceListMembers.Response`: Page of members.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await self.client.com.atproto.memberspace.list_members(
            models.ComAtprotoMemberspaceListMembers.Params(space=self._uri, limit=limit, cursor=cursor)
        )

    async def members(self) -> t.AsyncIterator['models.ComAtprotoMemberspaceDefs.Member']:
        """Iterate over the members of the space. For a space that a member list governs.

        Yields:
            :obj:`models.ComAtprotoMemberspaceDefs.Member`: Member with its access to the space.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        async def fetch(params: t.Dict[str, t.Any]) -> 'models.ComAtprotoMemberspaceListMembers.Response':
            return await self.list_members(cursor=params['cursor'])

        async for member in paginate(fetch, {'cursor': None}).items():
            yield member

    async def put_members(self, members: t.Sequence['models.ComAtprotoMemberspaceDefs.Member']) -> bool:
        """Add members to the space, or replace the access of the ones it has. For a space that a member list governs.

        Args:
            members: Members with their access to the space, 100 at most. The last entry of an account counts.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await self.client.com.atproto.memberspace.put_members(
            models.ComAtprotoMemberspacePutMembers.Data(space=self._uri, members=list(members))
        )

    async def remove_members(self, dids: t.Sequence[str]) -> bool:
        """Remove members from the space. For a space that a member list governs.

        Args:
            dids: DIDs of the members, 100 at most. The ones of other accounts are ignored.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return await self.client.com.atproto.memberspace.remove_members(
            models.ComAtprotoMemberspaceRemoveMembers.Data(space=self._uri, dids=list(dids))
        )
