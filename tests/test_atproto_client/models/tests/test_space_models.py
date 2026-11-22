import inspect

import pytest
from atproto_client import AsyncClient, Client, models
from atproto_client.exceptions import ModelError
from atproto_client.models import get_model_as_dict, get_model_as_json, get_or_create, string_formats
from atproto_client.models.dot_dict import DotDict
from pydantic_core import from_json

_AUTHOR = 'did:web:author.example'
_SPACE = 'at://did:web:authority.example/space/com.example.space/skey'
_MEMBER_URI = f'{_SPACE}/{_AUTHOR}/com.atproto.memberspace.member/{_AUTHOR}'
_MEMBER_CID = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'

# Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/commit_test.go#L318-L324
_COMMIT = {
    'ver': 1,
    'repo': _AUTHOR,
    'space': _SPACE,
    'rev': '3mtwwsccuqy22',
    'data': {'$bytes': 'vKXsJ5KymUrpNSNk/CdsSpo4M5wckYJAZTYEZOR6jMM'},
}
_COMMIT_DATA = bytes.fromhex('bca5ec2792b2994ae9352364fc276c4a9a38339c1c91824065360464e47a8cc3')


def test_space_lexicons_have_ids() -> None:
    assert models.ids.ComAtprotoSpaceAuthorizeSpaceSync == 'com.atproto.space.authorizeSpaceSync'
    assert models.ids.ComAtprotoMemberspaceMember == 'com.atproto.memberspace.member'
    assert models.ids.ComAtprotoManagedspaceCheckAccess == 'com.atproto.managedspace.checkAccess'
    assert models.ids.ComAtprotoPersonalspacePolicy == 'com.atproto.personalspace.policy'


def test_space_methods_exist_on_the_sync_client() -> None:
    client = Client()

    assert callable(client.com.atproto.space.get_record)
    assert callable(client.com.atproto.memberspace.list_members)
    assert callable(client.com.atproto.managedspace.check_access)
    assert not inspect.iscoroutinefunction(client.com.atproto.space.get_record)


def test_space_methods_exist_on_the_async_client() -> None:
    client = AsyncClient()

    assert inspect.iscoroutinefunction(client.com.atproto.space.get_record)
    assert inspect.iscoroutinefunction(client.com.atproto.memberspace.list_members)
    assert inspect.iscoroutinefunction(client.com.atproto.managedspace.check_access)


def test_space_fields_are_space_refs() -> None:
    params = models.ComAtprotoSpaceGetRecord.Params
    data = {'space': _SPACE, 'repo': _AUTHOR, 'collection': 'com.atproto.memberspace.member', 'rkey': _AUTHOR}

    assert params.model_fields['space'].annotation is string_formats.SpaceRef
    assert get_or_create(data, params, strict_string_format=True).space == _SPACE
    with pytest.raises(ModelError, match='Invalid space reference'):
        get_or_create({**data, 'space': _MEMBER_URI}, params, strict_string_format=True)


def test_commit_data_is_decoded_from_json_bytes() -> None:
    response = get_or_create({'commit': _COMMIT}, models.ComAtprotoSpaceGetLatestCommit.Response)

    assert isinstance(response, models.ComAtprotoSpaceGetLatestCommit.Response)
    assert response.commit.data == _COMMIT_DATA
    assert get_model_as_dict(response.commit)['data'] == _COMMIT_DATA
    assert from_json(get_model_as_json(response.commit))['data'] == _COMMIT['data']


def test_writers_page_keeps_updates_of_an_unknown_type() -> None:
    write = {
        '$type': 'com.atproto.space.defs#repoWrite',
        'repo': _AUTHOR,
        'repoRev': '3mtwwsccuqy22',
        'data': _COMMIT['data'],
        'spaceRev': '3mtwwsccuqy23',
    }
    removed = {
        '$type': 'com.atproto.space.defs#repoRemoved',
        'repo': 'did:web:removed.example',
        'spaceRev': '3mtwwsccuqy24',
    }
    unknown = {'$type': 'com.atproto.space.defs#repoFrozen', 'repo': 'did:web:frozen.example'}

    response = get_or_create(
        {'repos': [write, removed, unknown], 'cursor': '3mtwwsccuqy24'}, models.ComAtprotoSpaceListWriters.Response
    )

    assert isinstance(response, models.ComAtprotoSpaceListWriters.Response)
    parsed_write, parsed_removed, parsed_unknown = response.get_page_items()
    assert isinstance(parsed_write, models.ComAtprotoSpaceDefs.RepoWrite)
    assert parsed_write.data == _COMMIT_DATA
    assert parsed_write.prev_space_rev is None
    assert isinstance(parsed_removed, models.ComAtprotoSpaceDefs.RepoRemoved)
    assert isinstance(parsed_unknown, DotDict)


def test_space_record_is_resolved_to_its_model() -> None:
    value = {'$type': 'com.atproto.memberspace.member', 'read': True, 'write': False}

    response = get_or_create(
        {'uri': _MEMBER_URI, 'cid': _MEMBER_CID, 'value': value},
        models.ComAtprotoSpaceGetRecord.Response,
        strict_string_format=True,
    )

    assert isinstance(response, models.ComAtprotoSpaceGetRecord.Response)
    assert isinstance(response.value, models.ComAtprotoMemberspaceMember.Record)
    assert response.value.write is False


def test_space_policy_is_an_open_union() -> None:
    policy = {'$type': 'com.atproto.memberspace.policy', 'publicRead': True}

    response = get_or_create({'space': _SPACE, 'policy': policy}, models.ComAtprotoSpaceGetSpace.Response)

    assert isinstance(response, models.ComAtprotoSpaceGetSpace.Response)
    assert isinstance(response.policy, models.ComAtprotoMemberspacePolicy.Main)
    assert response.policy.public_read is True
    assert response.policy.public_write is False


def test_repo_archive_is_raw_bytes() -> None:
    assert models.ComAtprotoSpaceGetRepo.Response is bytes
    assert models.ComAtprotoSpaceImportRepo.Data is bytes
