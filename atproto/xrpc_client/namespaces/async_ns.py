##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass, field
from typing import Optional, Union

from atproto.xrpc_client import models
from atproto.xrpc_client.models.utils import get_or_create_model, get_response_model
from atproto.xrpc_client.namespaces.base import DefaultNamespace, NamespaceBase


@dataclass
class ComNamespace(NamespaceBase):
    atproto: 'AtprotoNamespace' = field(default_factory=DefaultNamespace)

    def __post_init__(self):
        self.atproto = AtprotoNamespace(self._client)


@dataclass
class AtprotoNamespace(NamespaceBase):
    admin: 'AdminNamespace' = field(default_factory=DefaultNamespace)
    identity: 'IdentityNamespace' = field(default_factory=DefaultNamespace)
    label: 'LabelNamespace' = field(default_factory=DefaultNamespace)
    moderation: 'ModerationNamespace' = field(default_factory=DefaultNamespace)
    repo: 'RepoNamespace' = field(default_factory=DefaultNamespace)
    server: 'ServerNamespace' = field(default_factory=DefaultNamespace)
    sync: 'SyncNamespace' = field(default_factory=DefaultNamespace)

    def __post_init__(self):
        self.admin = AdminNamespace(self._client)
        self.identity = IdentityNamespace(self._client)
        self.label = LabelNamespace(self._client)
        self.moderation = ModerationNamespace(self._client)
        self.repo = RepoNamespace(self._client)
        self.server = ServerNamespace(self._client)
        self.sync = SyncNamespace(self._client)


@dataclass
class SyncNamespace(NamespaceBase):
    async def get_blob(
        self, params: Union[dict, 'models.ComAtprotoSyncGetBlob.Params'], **kwargs
    ) -> models.ComAtprotoSyncGetBlob.Response:
        """Get a blob associated with a given repo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetBlob.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncGetBlob.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.getBlob', params=params, output_encoding='*/*', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetBlob.Response)

    async def get_blocks(
        self, params: Union[dict, 'models.ComAtprotoSyncGetBlocks.Params'], **kwargs
    ) -> models.ComAtprotoSyncGetBlocks.Response:
        """Gets blocks from a given repo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetBlocks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncGetBlocks.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.getBlocks', params=params, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetBlocks.Response)

    async def get_checkout(
        self, params: Union[dict, 'models.ComAtprotoSyncGetCheckout.Params'], **kwargs
    ) -> models.ComAtprotoSyncGetCheckout.Response:
        """Gets the repo state.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetCheckout.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncGetCheckout.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.getCheckout', params=params, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetCheckout.Response)

    async def get_commit_path(
        self, params: Union[dict, 'models.ComAtprotoSyncGetCommitPath.Params'], **kwargs
    ) -> models.ComAtprotoSyncGetCommitPath.Response:
        """Gets the path of repo commits.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetCommitPath.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncGetCommitPath.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.getCommitPath', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetCommitPath.Response)

    async def get_head(
        self, params: Union[dict, 'models.ComAtprotoSyncGetHead.Params'], **kwargs
    ) -> models.ComAtprotoSyncGetHead.Response:
        """Gets the current HEAD CID of a repo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetHead.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncGetHead.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.getHead', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetHead.Response)

    async def get_record(
        self, params: Union[dict, 'models.ComAtprotoSyncGetRecord.Params'], **kwargs
    ) -> models.ComAtprotoSyncGetRecord.Response:
        """Gets blocks needed for existence or non-existence of record.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncGetRecord.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.getRecord', params=params, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetRecord.Response)

    async def get_repo(
        self, params: Union[dict, 'models.ComAtprotoSyncGetRepo.Params'], **kwargs
    ) -> models.ComAtprotoSyncGetRepo.Response:
        """Gets the repo state.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetRepo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncGetRepo.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.getRepo', params=params, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetRepo.Response)

    async def list_blobs(
        self, params: Union[dict, 'models.ComAtprotoSyncListBlobs.Params'], **kwargs
    ) -> models.ComAtprotoSyncListBlobs.Response:
        """List blob cids for some range of commits.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncListBlobs.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncListBlobs.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.listBlobs', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncListBlobs.Response)

    async def list_repos(
        self, params: Optional[Union[dict, 'models.ComAtprotoSyncListRepos.Params']] = None, **kwargs
    ) -> models.ComAtprotoSyncListRepos.Response:
        """List dids and root cids of hosted repos.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncListRepos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncListRepos.Params)
        response = await self._client.invoke_query(
            'com.atproto.sync.listRepos', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncListRepos.Response)

    async def notify_of_update(
        self, params: Union[dict, 'models.ComAtprotoSyncNotifyOfUpdate.Params'], **kwargs
    ) -> bool:
        """Notify a crawling service of a recent update. Often when a long break between updates causes the connection with the crawling service to break.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncNotifyOfUpdate.Params)
        response = await self._client.invoke_query('com.atproto.sync.notifyOfUpdate', params=params, **kwargs)
        return get_response_model(response, bool)

    async def request_crawl(self, params: Union[dict, 'models.ComAtprotoSyncRequestCrawl.Params'], **kwargs) -> bool:
        """Request a service to persistently crawl hosted repos.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoSyncRequestCrawl.Params)
        response = await self._client.invoke_query('com.atproto.sync.requestCrawl', params=params, **kwargs)
        return get_response_model(response, bool)


@dataclass
class ServerNamespace(NamespaceBase):
    async def create_account(
        self, data: Union[dict, 'models.ComAtprotoServerCreateAccount.Data'], **kwargs
    ) -> models.ComAtprotoServerCreateAccount.Response:
        """Create an account.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateAccount.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerCreateAccount.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.createAccount',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateAccount.Response)

    async def create_app_password(
        self, data: Union[dict, 'models.ComAtprotoServerCreateAppPassword.Data'], **kwargs
    ) -> models.ComAtprotoServerCreateAppPassword.ResponseRef:
        """Create an app-specific password.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateAppPassword.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerCreateAppPassword.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.createAppPassword',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateAppPassword.ResponseRef)

    async def create_invite_code(
        self, data: Union[dict, 'models.ComAtprotoServerCreateInviteCode.Data'], **kwargs
    ) -> models.ComAtprotoServerCreateInviteCode.Response:
        """Create an invite code.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateInviteCode.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerCreateInviteCode.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.createInviteCode',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateInviteCode.Response)

    async def create_invite_codes(
        self, data: Union[dict, 'models.ComAtprotoServerCreateInviteCodes.Data'], **kwargs
    ) -> models.ComAtprotoServerCreateInviteCodes.Response:
        """Create an invite code.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerCreateInviteCodes.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.createInviteCodes',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateInviteCodes.Response)

    async def create_session(
        self, data: Union[dict, 'models.ComAtprotoServerCreateSession.Data'], **kwargs
    ) -> models.ComAtprotoServerCreateSession.Response:
        """Create an authentication session.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateSession.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerCreateSession.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.createSession',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateSession.Response)

    async def delete_account(self, data: Union[dict, 'models.ComAtprotoServerDeleteAccount.Data'], **kwargs) -> bool:
        """Delete a user account with a token and password.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerDeleteAccount.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.deleteAccount', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    async def delete_session(self, **kwargs) -> bool:
        """Delete the current session.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        response = await self._client.invoke_procedure('com.atproto.server.deleteSession', **kwargs)
        return get_response_model(response, bool)

    async def describe_server(self, **kwargs) -> models.ComAtprotoServerDescribeServer.Response:
        """Get a document describing the service's accounts configuration.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerDescribeServer.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        response = await self._client.invoke_query(
            'com.atproto.server.describeServer', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerDescribeServer.Response)

    async def get_account_invite_codes(
        self, params: Optional[Union[dict, 'models.ComAtprotoServerGetAccountInviteCodes.Params']] = None, **kwargs
    ) -> models.ComAtprotoServerGetAccountInviteCodes.Response:
        """Get all invite codes for a given account.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerGetAccountInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoServerGetAccountInviteCodes.Params)
        response = await self._client.invoke_query(
            'com.atproto.server.getAccountInviteCodes', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerGetAccountInviteCodes.Response)

    async def get_session(self, **kwargs) -> models.ComAtprotoServerGetSession.Response:
        """Get information about the current session.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerGetSession.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        response = await self._client.invoke_query(
            'com.atproto.server.getSession', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerGetSession.Response)

    async def list_app_passwords(self, **kwargs) -> models.ComAtprotoServerListAppPasswords.Response:
        """List all app-specific passwords.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerListAppPasswords.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        response = await self._client.invoke_query(
            'com.atproto.server.listAppPasswords', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerListAppPasswords.Response)

    async def refresh_session(self, **kwargs) -> models.ComAtprotoServerRefreshSession.Response:
        """Refresh an authentication session.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerRefreshSession.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        response = await self._client.invoke_procedure(
            'com.atproto.server.refreshSession', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerRefreshSession.Response)

    async def request_account_delete(self, **kwargs) -> bool:
        """Initiate a user account deletion via email.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        response = await self._client.invoke_procedure('com.atproto.server.requestAccountDelete', **kwargs)
        return get_response_model(response, bool)

    async def request_password_reset(
        self, data: Union[dict, 'models.ComAtprotoServerRequestPasswordReset.Data'], **kwargs
    ) -> bool:
        """Initiate a user account password reset via email.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerRequestPasswordReset.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.requestPasswordReset', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    async def reset_password(self, data: Union[dict, 'models.ComAtprotoServerResetPassword.Data'], **kwargs) -> bool:
        """Reset a user account password using a token.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerResetPassword.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.resetPassword', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    async def revoke_app_password(
        self, data: Union[dict, 'models.ComAtprotoServerRevokeAppPassword.Data'], **kwargs
    ) -> bool:
        """Revoke an app-specific password by name.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoServerRevokeAppPassword.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.server.revokeAppPassword', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


@dataclass
class RepoNamespace(NamespaceBase):
    async def apply_writes(self, data: Union[dict, 'models.ComAtprotoRepoApplyWrites.Data'], **kwargs) -> bool:
        """Apply a batch transaction of creates, updates, and deletes.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoRepoApplyWrites.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.repo.applyWrites', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    async def create_record(
        self, data: Union[dict, 'models.ComAtprotoRepoCreateRecord.Data'], **kwargs
    ) -> models.ComAtprotoRepoCreateRecord.Response:
        """Create a new record.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoRepoCreateRecord.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)

    async def delete_record(self, data: Union[dict, 'models.ComAtprotoRepoDeleteRecord.Data'], **kwargs) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoRepoDeleteRecord.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    async def describe_repo(
        self, params: Union[dict, 'models.ComAtprotoRepoDescribeRepo.Params'], **kwargs
    ) -> models.ComAtprotoRepoDescribeRepo.Response:
        """Get information about the repo, including the list of collections.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoDescribeRepo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoRepoDescribeRepo.Params)
        response = await self._client.invoke_query(
            'com.atproto.repo.describeRepo', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoDescribeRepo.Response)

    async def get_record(
        self, params: Union[dict, 'models.ComAtprotoRepoGetRecord.Params'], **kwargs
    ) -> models.ComAtprotoRepoGetRecord.Response:
        """Get a record.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoGetRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoRepoGetRecord.Params)
        response = await self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoGetRecord.Response)

    async def list_records(
        self, params: Union[dict, 'models.ComAtprotoRepoListRecords.Params'], **kwargs
    ) -> models.ComAtprotoRepoListRecords.Response:
        """List a range of records in a collection.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoListRecords.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoRepoListRecords.Params)
        response = await self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoListRecords.Response)

    async def put_record(
        self, data: Union[dict, 'models.ComAtprotoRepoPutRecord.Data'], **kwargs
    ) -> models.ComAtprotoRepoPutRecord.Response:
        """Write a record, creating or updating it as needed.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoPutRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoRepoPutRecord.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.repo.putRecord',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoPutRecord.Response)

    async def upload_blob(
        self, data: 'models.ComAtprotoRepoUploadBlob.Data', **kwargs
    ) -> models.ComAtprotoRepoUploadBlob.Response:
        """Upload a new blob to be added to repo in a later request.

        Args:
            data: Input data alias.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoUploadBlob.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        response = await self._client.invoke_procedure(
            'com.atproto.repo.uploadBlob', data=data, input_encoding='*/*', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoUploadBlob.Response)


@dataclass
class AdminNamespace(NamespaceBase):
    async def disable_invite_codes(
        self, data: Optional[Union[dict, 'models.ComAtprotoAdminDisableInviteCodes.Data']] = None, **kwargs
    ) -> bool:
        """Disable some set of codes and/or all codes associated with a set of users.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoAdminDisableInviteCodes.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.admin.disableInviteCodes', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    async def get_invite_codes(
        self, params: Optional[Union[dict, 'models.ComAtprotoAdminGetInviteCodes.Params']] = None, **kwargs
    ) -> models.ComAtprotoAdminGetInviteCodes.Response:
        """Admin view of invite codes.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoAdminGetInviteCodes.Params)
        response = await self._client.invoke_query(
            'com.atproto.admin.getInviteCodes', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetInviteCodes.Response)

    async def get_moderation_action(
        self, params: Union[dict, 'models.ComAtprotoAdminGetModerationAction.Params'], **kwargs
    ) -> models.ComAtprotoAdminGetModerationAction.ResponseRef:
        """View details about a moderation action.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetModerationAction.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoAdminGetModerationAction.Params)
        response = await self._client.invoke_query(
            'com.atproto.admin.getModerationAction', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetModerationAction.ResponseRef)

    async def get_moderation_actions(
        self, params: Optional[Union[dict, 'models.ComAtprotoAdminGetModerationActions.Params']] = None, **kwargs
    ) -> models.ComAtprotoAdminGetModerationActions.Response:
        """List moderation actions related to a subject.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetModerationActions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoAdminGetModerationActions.Params)
        response = await self._client.invoke_query(
            'com.atproto.admin.getModerationActions', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetModerationActions.Response)

    async def get_moderation_report(
        self, params: Union[dict, 'models.ComAtprotoAdminGetModerationReport.Params'], **kwargs
    ) -> models.ComAtprotoAdminGetModerationReport.ResponseRef:
        """View details about a moderation report.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetModerationReport.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoAdminGetModerationReport.Params)
        response = await self._client.invoke_query(
            'com.atproto.admin.getModerationReport', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetModerationReport.ResponseRef)

    async def get_moderation_reports(
        self, params: Optional[Union[dict, 'models.ComAtprotoAdminGetModerationReports.Params']] = None, **kwargs
    ) -> models.ComAtprotoAdminGetModerationReports.Response:
        """List moderation reports related to a subject.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetModerationReports.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoAdminGetModerationReports.Params)
        response = await self._client.invoke_query(
            'com.atproto.admin.getModerationReports', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetModerationReports.Response)

    async def get_record(
        self, params: Union[dict, 'models.ComAtprotoAdminGetRecord.Params'], **kwargs
    ) -> models.ComAtprotoAdminGetRecord.ResponseRef:
        """View details about a record.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetRecord.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoAdminGetRecord.Params)
        response = await self._client.invoke_query(
            'com.atproto.admin.getRecord', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetRecord.ResponseRef)

    async def get_repo(
        self, params: Union[dict, 'models.ComAtprotoAdminGetRepo.Params'], **kwargs
    ) -> models.ComAtprotoAdminGetRepo.ResponseRef:
        """View details about a repository.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetRepo.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoAdminGetRepo.Params)
        response = await self._client.invoke_query(
            'com.atproto.admin.getRepo', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetRepo.ResponseRef)

    async def resolve_moderation_reports(
        self, data: Union[dict, 'models.ComAtprotoAdminResolveModerationReports.Data'], **kwargs
    ) -> models.ComAtprotoAdminResolveModerationReports.ResponseRef:
        """Resolve moderation reports by an action.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminResolveModerationReports.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoAdminResolveModerationReports.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.admin.resolveModerationReports',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminResolveModerationReports.ResponseRef)

    async def reverse_moderation_action(
        self, data: Union[dict, 'models.ComAtprotoAdminReverseModerationAction.Data'], **kwargs
    ) -> models.ComAtprotoAdminReverseModerationAction.ResponseRef:
        """Reverse a moderation action.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminReverseModerationAction.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoAdminReverseModerationAction.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.admin.reverseModerationAction',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminReverseModerationAction.ResponseRef)

    async def search_repos(
        self, params: Optional[Union[dict, 'models.ComAtprotoAdminSearchRepos.Params']] = None, **kwargs
    ) -> models.ComAtprotoAdminSearchRepos.Response:
        """Find repositories based on a search term.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminSearchRepos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoAdminSearchRepos.Params)
        response = await self._client.invoke_query(
            'com.atproto.admin.searchRepos', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminSearchRepos.Response)

    async def take_moderation_action(
        self, data: Union[dict, 'models.ComAtprotoAdminTakeModerationAction.Data'], **kwargs
    ) -> models.ComAtprotoAdminTakeModerationAction.ResponseRef:
        """Take a moderation action on a repo.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminTakeModerationAction.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoAdminTakeModerationAction.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.admin.takeModerationAction',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminTakeModerationAction.ResponseRef)

    async def update_account_email(
        self, data: Union[dict, 'models.ComAtprotoAdminUpdateAccountEmail.Data'], **kwargs
    ) -> bool:
        """Administrative action to update an account's email.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoAdminUpdateAccountEmail.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.admin.updateAccountEmail', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    async def update_account_handle(
        self, data: Union[dict, 'models.ComAtprotoAdminUpdateAccountHandle.Data'], **kwargs
    ) -> bool:
        """Administrative action to update an account's handle.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoAdminUpdateAccountHandle.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.admin.updateAccountHandle', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


@dataclass
class IdentityNamespace(NamespaceBase):
    async def resolve_handle(
        self, params: Optional[Union[dict, 'models.ComAtprotoIdentityResolveHandle.Params']] = None, **kwargs
    ) -> models.ComAtprotoIdentityResolveHandle.Response:
        """Provides the DID of a repo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoIdentityResolveHandle.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoIdentityResolveHandle.Params)
        response = await self._client.invoke_query(
            'com.atproto.identity.resolveHandle', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoIdentityResolveHandle.Response)

    async def update_handle(self, data: Union[dict, 'models.ComAtprotoIdentityUpdateHandle.Data'], **kwargs) -> bool:
        """Updates the handle of the account.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoIdentityUpdateHandle.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.identity.updateHandle', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


@dataclass
class ModerationNamespace(NamespaceBase):
    async def create_report(
        self, data: Union[dict, 'models.ComAtprotoModerationCreateReport.Data'], **kwargs
    ) -> models.ComAtprotoModerationCreateReport.Response:
        """Report a repo or a record.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoModerationCreateReport.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.ComAtprotoModerationCreateReport.Data)
        response = await self._client.invoke_procedure(
            'com.atproto.moderation.createReport',
            data=data,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoModerationCreateReport.Response)


@dataclass
class LabelNamespace(NamespaceBase):
    async def query_labels(
        self, params: Union[dict, 'models.ComAtprotoLabelQueryLabels.Params'], **kwargs
    ) -> models.ComAtprotoLabelQueryLabels.Response:
        """Find labels relevant to the provided URI patterns.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoLabelQueryLabels.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.ComAtprotoLabelQueryLabels.Params)
        response = await self._client.invoke_query(
            'com.atproto.label.queryLabels', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoLabelQueryLabels.Response)


@dataclass
class AppNamespace(NamespaceBase):
    bsky: 'BskyNamespace' = field(default_factory=DefaultNamespace)

    def __post_init__(self):
        self.bsky = BskyNamespace(self._client)


@dataclass
class BskyNamespace(NamespaceBase):
    actor: 'ActorNamespace' = field(default_factory=DefaultNamespace)
    feed: 'FeedNamespace' = field(default_factory=DefaultNamespace)
    graph: 'GraphNamespace' = field(default_factory=DefaultNamespace)
    notification: 'NotificationNamespace' = field(default_factory=DefaultNamespace)
    unspecced: 'UnspeccedNamespace' = field(default_factory=DefaultNamespace)

    def __post_init__(self):
        self.actor = ActorNamespace(self._client)
        self.feed = FeedNamespace(self._client)
        self.graph = GraphNamespace(self._client)
        self.notification = NotificationNamespace(self._client)
        self.unspecced = UnspeccedNamespace(self._client)


@dataclass
class FeedNamespace(NamespaceBase):
    async def get_author_feed(
        self, params: Union[dict, 'models.AppBskyFeedGetAuthorFeed.Params'], **kwargs
    ) -> models.AppBskyFeedGetAuthorFeed.Response:
        """A view of an actor's feed.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetAuthorFeed.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyFeedGetAuthorFeed.Params)
        response = await self._client.invoke_query(
            'app.bsky.feed.getAuthorFeed', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetAuthorFeed.Response)

    async def get_likes(
        self, params: Union[dict, 'models.AppBskyFeedGetLikes.Params'], **kwargs
    ) -> models.AppBskyFeedGetLikes.Response:
        """Get likes.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetLikes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyFeedGetLikes.Params)
        response = await self._client.invoke_query(
            'app.bsky.feed.getLikes', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetLikes.Response)

    async def get_post_thread(
        self, params: Union[dict, 'models.AppBskyFeedGetPostThread.Params'], **kwargs
    ) -> models.AppBskyFeedGetPostThread.Response:
        """Get post thread.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetPostThread.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyFeedGetPostThread.Params)
        response = await self._client.invoke_query(
            'app.bsky.feed.getPostThread', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetPostThread.Response)

    async def get_posts(
        self, params: Union[dict, 'models.AppBskyFeedGetPosts.Params'], **kwargs
    ) -> models.AppBskyFeedGetPosts.Response:
        """A view of an actor's feed.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetPosts.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyFeedGetPosts.Params)
        response = await self._client.invoke_query(
            'app.bsky.feed.getPosts', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetPosts.Response)

    async def get_reposted_by(
        self, params: Union[dict, 'models.AppBskyFeedGetRepostedBy.Params'], **kwargs
    ) -> models.AppBskyFeedGetRepostedBy.Response:
        """Get reposted by.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetRepostedBy.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyFeedGetRepostedBy.Params)
        response = await self._client.invoke_query(
            'app.bsky.feed.getRepostedBy', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetRepostedBy.Response)

    async def get_timeline(
        self, params: Optional[Union[dict, 'models.AppBskyFeedGetTimeline.Params']] = None, **kwargs
    ) -> models.AppBskyFeedGetTimeline.Response:
        """A view of the user's home timeline.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetTimeline.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyFeedGetTimeline.Params)
        response = await self._client.invoke_query(
            'app.bsky.feed.getTimeline', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetTimeline.Response)


@dataclass
class ActorNamespace(NamespaceBase):
    async def get_profile(
        self, params: Union[dict, 'models.AppBskyActorGetProfile.Params'], **kwargs
    ) -> models.AppBskyActorGetProfile.ResponseRef:
        """Get profile.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetProfile.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyActorGetProfile.Params)
        response = await self._client.invoke_query(
            'app.bsky.actor.getProfile', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetProfile.ResponseRef)

    async def get_profiles(
        self, params: Union[dict, 'models.AppBskyActorGetProfiles.Params'], **kwargs
    ) -> models.AppBskyActorGetProfiles.Response:
        """Get profiles.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetProfiles.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyActorGetProfiles.Params)
        response = await self._client.invoke_query(
            'app.bsky.actor.getProfiles', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetProfiles.Response)

    async def get_suggestions(
        self, params: Optional[Union[dict, 'models.AppBskyActorGetSuggestions.Params']] = None, **kwargs
    ) -> models.AppBskyActorGetSuggestions.Response:
        """Get a list of actors suggested for following. Used in discovery UIs.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetSuggestions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyActorGetSuggestions.Params)
        response = await self._client.invoke_query(
            'app.bsky.actor.getSuggestions', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetSuggestions.Response)

    async def search_actors(
        self, params: Optional[Union[dict, 'models.AppBskyActorSearchActors.Params']] = None, **kwargs
    ) -> models.AppBskyActorSearchActors.Response:
        """Find actors matching search criteria.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorSearchActors.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyActorSearchActors.Params)
        response = await self._client.invoke_query(
            'app.bsky.actor.searchActors', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorSearchActors.Response)

    async def search_actors_typeahead(
        self, params: Optional[Union[dict, 'models.AppBskyActorSearchActorsTypeahead.Params']] = None, **kwargs
    ) -> models.AppBskyActorSearchActorsTypeahead.Response:
        """Find actor suggestions for a search term.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorSearchActorsTypeahead.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyActorSearchActorsTypeahead.Params)
        response = await self._client.invoke_query(
            'app.bsky.actor.searchActorsTypeahead', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorSearchActorsTypeahead.Response)


@dataclass
class GraphNamespace(NamespaceBase):
    async def get_blocks(
        self, params: Optional[Union[dict, 'models.AppBskyGraphGetBlocks.Params']] = None, **kwargs
    ) -> models.AppBskyGraphGetBlocks.Response:
        """Who is the requester's account blocking?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetBlocks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyGraphGetBlocks.Params)
        response = await self._client.invoke_query(
            'app.bsky.graph.getBlocks', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetBlocks.Response)

    async def get_followers(
        self, params: Union[dict, 'models.AppBskyGraphGetFollowers.Params'], **kwargs
    ) -> models.AppBskyGraphGetFollowers.Response:
        """Who is following an actor?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetFollowers.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyGraphGetFollowers.Params)
        response = await self._client.invoke_query(
            'app.bsky.graph.getFollowers', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetFollowers.Response)

    async def get_follows(
        self, params: Union[dict, 'models.AppBskyGraphGetFollows.Params'], **kwargs
    ) -> models.AppBskyGraphGetFollows.Response:
        """Who is an actor following?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetFollows.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyGraphGetFollows.Params)
        response = await self._client.invoke_query(
            'app.bsky.graph.getFollows', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetFollows.Response)

    async def get_mutes(
        self, params: Optional[Union[dict, 'models.AppBskyGraphGetMutes.Params']] = None, **kwargs
    ) -> models.AppBskyGraphGetMutes.Response:
        """Who does the viewer mute?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetMutes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyGraphGetMutes.Params)
        response = await self._client.invoke_query(
            'app.bsky.graph.getMutes', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetMutes.Response)

    async def mute_actor(self, data: Union[dict, 'models.AppBskyGraphMuteActor.Data'], **kwargs) -> bool:
        """Mute an actor by did or handle.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.AppBskyGraphMuteActor.Data)
        response = await self._client.invoke_procedure(
            'app.bsky.graph.muteActor', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    async def unmute_actor(self, data: Union[dict, 'models.AppBskyGraphUnmuteActor.Data'], **kwargs) -> bool:
        """Unmute an actor by did or handle.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.AppBskyGraphUnmuteActor.Data)
        response = await self._client.invoke_procedure(
            'app.bsky.graph.unmuteActor', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


@dataclass
class UnspeccedNamespace(NamespaceBase):
    async def get_popular(
        self, params: Optional[Union[dict, 'models.AppBskyUnspeccedGetPopular.Params']] = None, **kwargs
    ) -> models.AppBskyUnspeccedGetPopular.Response:
        """An unspecced view of globally popular items.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedGetPopular.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyUnspeccedGetPopular.Params)
        response = await self._client.invoke_query(
            'app.bsky.unspecced.getPopular', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyUnspeccedGetPopular.Response)


@dataclass
class NotificationNamespace(NamespaceBase):
    async def get_unread_count(
        self, params: Optional[Union[dict, 'models.AppBskyNotificationGetUnreadCount.Params']] = None, **kwargs
    ) -> models.AppBskyNotificationGetUnreadCount.Response:
        """Get unread count.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyNotificationGetUnreadCount.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyNotificationGetUnreadCount.Params)
        response = await self._client.invoke_query(
            'app.bsky.notification.getUnreadCount', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyNotificationGetUnreadCount.Response)

    async def list_notifications(
        self, params: Optional[Union[dict, 'models.AppBskyNotificationListNotifications.Params']] = None, **kwargs
    ) -> models.AppBskyNotificationListNotifications.Response:
        """List notifications.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyNotificationListNotifications.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params = get_or_create_model(params, models.AppBskyNotificationListNotifications.Params)
        response = await self._client.invoke_query(
            'app.bsky.notification.listNotifications', params=params, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyNotificationListNotifications.Response)

    async def update_seen(self, data: Union[dict, 'models.AppBskyNotificationUpdateSeen.Data'], **kwargs) -> bool:
        """Notify server that the user has seen notifications.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data = get_or_create_model(data, models.AppBskyNotificationUpdateSeen.Data)
        response = await self._client.invoke_procedure(
            'app.bsky.notification.updateSeen', data=data, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)
