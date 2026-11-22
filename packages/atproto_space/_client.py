import typing as t

import typing_extensions as te
from atproto_client import models
from atproto_client.exceptions import LoginRequiredError
from atproto_core._effects import Flow, call

from atproto_space._reader import _SpaceReaderBase, check_request, get_record_type
from atproto_space.space_type import _LITERAL_KEY_PREFIX, SpaceType

if t.TYPE_CHECKING:
    from atproto_client.client.methods_mixin.session import SessionMethodsMixin
    from atproto_client.models.unknown_type import UnknownInputType
    from atproto_core.uri import SpaceRef

    from atproto_space.credential import SpaceCredential
    from atproto_space.models import SpacePolicy, WriteOperation


def get_account_did(client: 'SessionMethodsMixin') -> str:
    """Get the DID of the account that a client is logged in as.

    Raises:
        :class:`atproto.exceptions.LoginRequiredError`: The client is not logged in.
    """
    did = client._auth_session_did
    if did is None and client._session is not None:
        did = client._session.did

    if did is None:
        raise LoginRequiredError

    return did


def _get_collection(record: 'UnknownInputType') -> str:
    collection = get_record_type(record)
    if collection is None:
        raise ValueError('Record has no type')

    return collection


def create_space_flow(
    space_client: t.Callable[..., t.Any],
    client: t.Any,
    space_type: t.Union[SpaceType, str],
    policy: 'SpacePolicy',
    skey: t.Optional[str],
    **kwargs: t.Any,
) -> Flow[t.Any]:
    """Create a space that the account of a client is the authority of, and open it with the given space client."""
    did = get_account_did(client)

    # a request that the space client refuses must fail before the space is created
    request = kwargs.get('request')
    if request is not None:
        check_request(request)

    if isinstance(space_type, str):
        nsid = space_type
    else:
        nsid = space_type.nsid
        # a key that is left to the PDS to generate has nothing to check
        if skey is not None or space_type.key.startswith(_LITERAL_KEY_PREFIX):
            skey = space_type.ref_for(did, skey).skey

    data = models.ComAtprotoSpaceCreateSpace.Data(space_type=nsid, skey=skey, policy=policy)
    response: models.ComAtprotoSpaceCreateSpace.Response = yield call(client.com.atproto.space.create_space, data)

    return space_client(client, response.space, None if isinstance(space_type, str) else space_type, **kwargs)


class _SpaceClientBase(_SpaceReaderBase):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._credential_did: t.Optional[str] = None

    @property
    def client(self) -> t.Any:
        """Client of the account."""
        raise NotImplementedError

    @property
    def did(self) -> str:
        """DID of the account that the client acts for."""
        return get_account_did(self.client)

    @te.override
    def _get_repo(self, repo: t.Optional[str]) -> str:
        return self.did if repo is None else repo

    @te.override
    def _get_account_client(self, repo: str) -> t.Any:
        # a PDS lets the session of an account read no other repo than the one of the account
        return self.client if repo == self.did else None

    @te.override
    def _get_usable_credential(
        self, renew: bool, rejected: t.Optional['SpaceCredential']
    ) -> t.Optional['SpaceCredential']:
        # the client may have logged in as another account since the credential was requested
        if self._credential_did != self.did:
            return None

        return super()._get_usable_credential(renew, rejected)

    def _delegation_token_flow(self, ref: 'SpaceRef') -> Flow[str]:
        did = self.did
        if did != self._credential_did:
            # a failed request must not leave the credential of the previous account to this one
            self._credential = None
            self._credential_did = did

        params = models.ComAtprotoSpaceGetDelegationToken.Params(space=str(ref))
        response: models.ComAtprotoSpaceGetDelegationToken.Response = yield call(
            self.client.com.atproto.space.get_delegation_token, params
        )

        return response.token

    def _create_record_flow(
        self, record: 'UnknownInputType', rkey: t.Optional[str], validate: t.Optional[bool]
    ) -> Flow['models.ComAtprotoSpaceCreateRecord.Response']:
        data = models.ComAtprotoSpaceCreateRecord.Data(
            space=self._uri,
            repo=self.did,
            collection=_get_collection(record),
            rkey=rkey,
            validate_=validate,
            record=record,
        )
        response: models.ComAtprotoSpaceCreateRecord.Response = yield call(
            self.client.com.atproto.space.create_record, data
        )

        return response

    def _put_record_flow(
        self, record: 'UnknownInputType', rkey: str, validate: t.Optional[bool]
    ) -> Flow['models.ComAtprotoSpacePutRecord.Response']:
        data = models.ComAtprotoSpacePutRecord.Data(
            space=self._uri,
            repo=self.did,
            collection=_get_collection(record),
            rkey=rkey,
            validate_=validate,
            record=record,
        )
        response: models.ComAtprotoSpacePutRecord.Response = yield call(self.client.com.atproto.space.put_record, data)

        return response

    def _delete_record_flow(self, collection: str, rkey: str) -> Flow[bool]:
        data = models.ComAtprotoSpaceDeleteRecord.Data(space=self._uri, repo=self.did, collection=collection, rkey=rkey)
        yield call(self.client.com.atproto.space.delete_record, data)

        return True

    def _apply_writes_flow(
        self, writes: t.Sequence['WriteOperation'], validate: t.Optional[bool]
    ) -> Flow['models.ComAtprotoSpaceApplyWrites.Response']:
        data = models.ComAtprotoSpaceApplyWrites.Data(
            space=self._uri, repo=self.did, writes=list(writes), validate_=validate
        )
        response: models.ComAtprotoSpaceApplyWrites.Response = yield call(
            self.client.com.atproto.space.apply_writes, data
        )

        return response

    def _clear_records_flow(self) -> Flow[bool]:
        data = models.ComAtprotoSpaceClearRecords.Data(space=self._uri, repo=self.did)
        yield call(self.client.com.atproto.space.clear_records, data)

        return True
