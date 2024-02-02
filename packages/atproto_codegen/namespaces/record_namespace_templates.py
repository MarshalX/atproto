# well, this is hardcoded by human and must be updated manually.
# rly don't want to create some kind of dynamic types.
# and even don't have time to do this.
# in original code, TypeScript Omit<> is used for args instead of coping
# this approach provides more clean usage on the user side with type hints

RECORD_CREATE_METHOD_TEMPLATE = """
    {d}def create(
        self,
        repo: str,
        record: 'models.{record_import}.Main',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoCreateRecord.Response':
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='{collection}',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate=validate,
        )
        response = {c}self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
"""

RECORD_GET_METHOD_TEMPLATE = """
    @dataclass
    class GetRecordResponse:
        \"""Get record response for `models.{record_import}.Main` record.\"""

        uri: str
        cid: str
        value: 'models.{record_import}.Main'

    {d}def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> GetRecordResponse:
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
        return self.GetRecordResponse(uri=response_model.uri, cid=response_model.cid, value=response_model.value)
"""

RECORD_LIST_METHOD_TEMPLATE = """
    @dataclass
    class ListRecordsResponse:
        \"""List records response for `models.{record_import}.Main` record.\"""

        records: t.Dict[str, 'models.{record_import}.Main']
        cursor: t.Optional[str]

    {d}def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> ListRecordsResponse:
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
            records={{record.uri: record.value for record in response_model.records}},
            cursor=response_model.cursor
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
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='{collection}',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = {c}self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)
"""
