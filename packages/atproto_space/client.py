import typing as t

import typing_extensions as te
from atproto_core._effects import run_flow

from atproto_space._client import _SpaceClientBase, create_space_flow, get_account_did
from atproto_space.reader import ClientAttestationProvider, NotifyRegistrationProvider, SpaceReader
from atproto_space.space_type import SpaceType

if t.TYPE_CHECKING:
    from atproto_client import Client, models
    from atproto_client.models.unknown_type import UnknownInputType
    from atproto_client.request import Request
    from atproto_core.uri import SpaceRef
    from atproto_identity.resolver import IdResolver

    from atproto_space.models import SpacePolicy, WriteOperation


class _ClientOptions(te.TypedDict, total=False):
    """Arguments the client takes besides the client of the account, the space and its type."""

    client_attestation_provider: ClientAttestationProvider
    notify_registration_provider: NotifyRegistrationProvider
    id_resolver: 'IdResolver'
    request: 'Request'


class SpaceClient(_SpaceClientBase, SpaceReader):
    """Client of a space that acts for an account. It reads the space and writes the repo of the account in it.

    A request for the repo of the account goes to the PDS of the account with the session of the client:
    every write, and every read that is given no repo or the DID of the account. Any other read goes
    where :py:class:`~atproto_space.SpaceReader` sends it, with a space credential that the client requests
    with a delegation token of the PDS of the account.

    Note:
        The client asks the PDS of the account for no MAC on the repo of the account. Of the repo of the account,
        a record is taken as the PDS sent it, and a commit is checked for its form only.

    Warning:
        Spaces are in alpha. The methods can change together with the protocol.

    Args:
        client: Client that is logged in as the account.
        space: URI of the space or a reference to it.
        space_type: Type of the space. The space must be of this type,
            and the records of other collections than the ones it declares are flagged as invalid.
        client_attestation_provider: Returns a client attestation for the given audience.
            For spaces that admit certain applications only.
        notify_registration_provider: Returns the endpoint that the host of the space notifies of updates.
            It is registered with every credential.
        id_resolver: Identity resolver. One that caches DID documents in memory by default.
        request: HTTP client of the requests that carry the space credential.
            It must carry no session of an account, so the one of a client is refused.
    """

    @classmethod
    def create_space(
        cls,
        client: 'Client',
        space_type: t.Union[SpaceType, str],
        policy: 'SpacePolicy',
        skey: t.Optional[str] = None,
        **kwargs: te.Unpack[_ClientOptions],
    ) -> te.Self:
        """Create a space that the account is the authority of, and open it.

        Args:
            client: Client that is logged in as the account.
            space_type: Type of the space, or its NSID.
            policy: Policy that governs the space.
            skey: Key of the space. The key of a type with a literal key by default,
                otherwise one that the PDS generates.
            **kwargs: Other arguments of the client.

        Returns:
            :obj:`SpaceClient`: Client of the new space.

        Raises:
            :class:`ValueError`: The key is not the literal key of the type.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        flow = create_space_flow(cls, client, space_type, policy, skey, **kwargs)
        space: te.Self = run_flow(flow)
        return space

    def __init__(
        self,
        client: 'Client',
        space: t.Union[str, 'SpaceRef'],
        space_type: t.Optional[SpaceType] = None,
        *,
        client_attestation_provider: t.Optional[ClientAttestationProvider] = None,
        notify_registration_provider: t.Optional[NotifyRegistrationProvider] = None,
        id_resolver: t.Optional['IdResolver'] = None,
        request: t.Optional['Request'] = None,
    ) -> None:
        # a client that is not logged in fails here, not on the first request
        get_account_did(client)

        super().__init__(
            space,
            space_type,
            delegation_token_provider=self._get_delegation_token,
            client_attestation_provider=client_attestation_provider,
            notify_registration_provider=notify_registration_provider,
            id_resolver=id_resolver,
            request=request,
        )
        self._client = client

    @property
    @te.override
    def client(self) -> 'Client':
        """Client of the account."""
        return self._client

    def create_record(
        self, record: 'UnknownInputType', rkey: t.Optional[str] = None, validate: t.Optional[bool] = None
    ) -> 'models.ComAtprotoSpaceCreateRecord.Response':
        """Create a record in the repo of the account in the space.

        Args:
            record: Record model, or a dict with ``$type``. The type is the collection of the record.
            rkey: Record key. One that the PDS generates by default.
            validate: :obj:`True` requires the PDS to validate the record against its lexicon and :obj:`False`
                skips the validation. By default the PDS validates the records of the lexicons that it knows.

        Returns:
            :obj:`models.ComAtprotoSpaceCreateRecord.Response`: Reference to the created record.

        Raises:
            :class:`ValueError`: The record has no type.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return run_flow(self._create_record_flow(record, rkey, validate))

    def put_record(
        self, record: 'UnknownInputType', rkey: str, validate: t.Optional[bool] = None
    ) -> 'models.ComAtprotoSpacePutRecord.Response':
        """Create or replace a record in the repo of the account in the space.

        Args:
            record: Record model, or a dict with ``$type``. The type is the collection of the record.
            rkey: Record key.
            validate: :obj:`True` requires the PDS to validate the record against its lexicon and :obj:`False`
                skips the validation. By default the PDS validates the records of the lexicons that it knows.

        Returns:
            :obj:`models.ComAtprotoSpacePutRecord.Response`: Reference to the record.

        Raises:
            :class:`ValueError`: The record has no type.
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return run_flow(self._put_record_flow(record, rkey, validate))

    def delete_record(self, collection: str, rkey: str) -> bool:
        """Delete a record from the repo of the account in the space, or ensure it doesn't exist.

        Args:
            collection: NSID of the record collection.
            rkey: Record key.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return run_flow(self._delete_record_flow(collection, rkey))

    def apply_writes(
        self, writes: t.Sequence['WriteOperation'], validate: t.Optional[bool] = None
    ) -> 'models.ComAtprotoSpaceApplyWrites.Response':
        """Apply a batch of writes to the repo of the account in the space. All of them are applied, or none.

        Args:
            writes: Operations in the order to apply them in: :obj:`models.ComAtprotoSpaceApplyWrites.Create`,
                :obj:`models.ComAtprotoSpaceApplyWrites.Update`
                and :obj:`models.ComAtprotoSpaceApplyWrites.Delete`.
            validate: :obj:`True` requires the PDS to validate the records against their lexicons and :obj:`False`
                skips the validation. By default the PDS validates the records of the lexicons that it knows.

        Returns:
            :obj:`models.ComAtprotoSpaceApplyWrites.Response`: Results of the operations, in their order.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return run_flow(self._apply_writes_flow(writes, validate))

    def clear_records(self) -> bool:
        """Delete every record of the repo of the account in the space.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        return run_flow(self._clear_records_flow())

    def _get_delegation_token(self, ref: 'SpaceRef') -> str:
        return run_flow(self._delegation_token_flow(ref))
