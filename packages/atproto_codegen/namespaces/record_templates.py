# well, this is hardcoded by human and must be updated manually.
# rly don't want to create some kind of dynamic types.
# and even don't have time to do this.
# in original code, TypeScript Omit<> is used for args instead of coping
# this approach provides more clean usage on the user side with type hints

RECORD_CREATE_METHOD_TEMPLATE = """
    @dataclass
    class CreateRecordResponse:
        \"""Create record response for :obj:`models.{record_import}.Record`.\"""

        uri: str  #: The URI of the record.
        cid: str  #: The CID of the record.

    {d}def create(
        self,
        repo: str,
        record: 'models.{record_import}.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> CreateRecordResponse:
        \"""Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        \"""
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='{collection}',
            repo=repo,
            record=record,
            rkey=rkey,
            swapCommit=swap_commit,
            validate=validate,
        )
        response = {c}self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return self.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)
"""

RECORD_GET_METHOD_TEMPLATE = """
    @dataclass
    class GetRecordResponse:
        \"""Get record response for :obj:`models.{record_import}.Record`.\"""

        uri: str  #: The URI of the record.
        value: 'models.{record_import}.Record'  #: The record.
        cid: t.Optional[str] = None  #: The CID of the record.

    {d}def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> GetRecordResponse:
        \"""Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        \"""
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='{collection}',
            repo=repo,
            rkey=rkey,
            cid=cid
        )
        response = {c}self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return self.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.{record_import}.Record', response_model.value),
        )
"""

RECORD_LIST_METHOD_TEMPLATE = """
    @dataclass
    class ListRecordsResponse:
        \"""List records response for :obj:`models.{record_import}.Record`.\"""

        records: t.Dict[str, 'models.{record_import}.Record']  #: Map of URIs to records.
        cursor: t.Optional[str] = None  #: Next page cursor.

    {d}def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> ListRecordsResponse:
        \"""List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        \"""
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='{collection}',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = {c}self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return self.ListRecordsResponse(
            records={{
                record.uri: t.cast('models.{record_import}.Record', record.value)
                for record in response_model.records
            }},
            cursor=response_model.cursor,
        )
"""

RECORD_DELETE_METHOD_TEMPLATE = """
    {d}def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        \"""Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        \"""
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='{collection}',
            repo=repo,
            rkey=rkey,
            swapCommit=swap_commit,
            swapRecord=swap_record,
        )
        response = {c}self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)
"""
