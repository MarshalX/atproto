import json
import typing as t

import httpx
import pytest
from atproto_client import Client, models
from atproto_client.exceptions import BadRequestError, LoginRequiredError
from atproto_client.models.dot_dict import DotDict
from atproto_client.request import Request
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import SpaceRef
from atproto_space import SpaceClient, SpaceManager

from tests.test_atproto_space.fake_space import (
    ALICE_DID,
    AUTHORITY_DID,
    AUTHORITY_PDS,
    BOB_DID,
    SPACE,
    FakeSpaceNetwork,
    build_network,
    fake_client,
    fake_id_resolver,
)

_GET_SPACE = 'com.atproto.space.getSpace'
_UPDATE_SPACE = 'com.atproto.space.updateSpace'
_DELETE_SPACE = 'com.atproto.space.deleteSpace'
_REMOVE_WRITER = 'com.atproto.space.removeWriter'
_LIST_MEMBERS = 'com.atproto.memberspace.listMembers'
_PUT_MEMBERS = 'com.atproto.memberspace.putMembers'
_REMOVE_MEMBERS = 'com.atproto.memberspace.removeMembers'

_MEMBERSPACE_POLICY = 'com.atproto.memberspace.policy'
_PERSONALSPACE_POLICY = 'com.atproto.personalspace.policy'
_MANAGEDSPACE_POLICY = 'com.atproto.managedspace.policy'
_MANAGING_APP = 'did:web:app.example#forum'
_CLIENT_ID = 'https://app.example/client.json'

_NOTE = 'com.example.note'
_CAROL_DID = 'did:plc:carolcarolcarolcarolcaro'


def make_manager(network: FakeSpaceNetwork) -> SpaceManager:
    return SpaceManager(fake_client(network, network.accounts[AUTHORITY_DID]), SPACE)


@pytest.fixture
def network() -> FakeSpaceNetwork:
    return build_network()


def _member(did: str, read: bool = True, write: bool = True) -> 'models.ComAtprotoMemberspaceDefs.Member':
    return models.ComAtprotoMemberspaceDefs.Member(did=did, read=read, write=write)


def _page(dids: t.List[str], cursor: t.Optional[str] = None) -> httpx.Response:
    body: t.Dict[str, t.Any] = {'members': [{'did': did, 'read': True, 'write': True} for did in dids]}
    if cursor is not None:
        body['cursor'] = cursor

    return httpx.Response(200, json=body)


def _body(network: FakeSpaceNetwork, nsid: str) -> t.Dict[str, t.Any]:
    body: t.Dict[str, t.Any] = json.loads(network.requests_to(nsid)[-1].content)
    return body


def _cursors(network: FakeSpaceNetwork, nsid: str) -> t.List[t.Optional[str]]:
    return [request.url.params.get('cursor') for request in network.requests_to(nsid)]


def test_manager_of_a_space_uri(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[AUTHORITY_DID])

    manager = SpaceManager(client, SPACE)

    assert manager.client is client
    assert manager.ref == SpaceRef(AUTHORITY_DID, 'com.example.group', 'main')
    assert manager.uri == SPACE
    assert network.requests == []


def test_manager_of_a_space_ref(network: FakeSpaceNetwork) -> None:
    ref = SpaceRef.from_str(SPACE)

    manager = SpaceManager(fake_client(network, network.accounts[AUTHORITY_DID]), ref)

    assert manager.ref is ref
    assert manager.uri == SPACE


def test_manager_refuses_a_uri_that_is_not_a_space_reference(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[AUTHORITY_DID])

    with pytest.raises(InvalidAtUriError):
        SpaceManager(client, f'{SPACE}/{ALICE_DID}/{_NOTE}/a')


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-manager.test.ts#L116-L120
def test_only_the_authority_manages_a_space(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])

    with pytest.raises(ValueError, match=rf'Only the space authority \({AUTHORITY_DID}\) can manage {SPACE}'):
        SpaceManager(client, SPACE)
    with pytest.raises(LoginRequiredError):
        SpaceManager(Client(), SPACE)

    assert network.requests == []


def test_requests_go_to_the_pds_of_the_authority_with_its_session(network: FakeSpaceNetwork) -> None:
    manager = make_manager(network)

    manager.get_space()
    manager.list_members()
    manager.put_members([_member(_CAROL_DID)])
    manager.remove_members([_CAROL_DID])
    manager.remove_writer(BOB_DID)
    manager.update_space(models.ComAtprotoPersonalspacePolicy.Main())
    manager.delete_space()

    bearer = f'Bearer {network.accounts[AUTHORITY_DID].access_token}'
    assert network.log == [
        (AUTHORITY_PDS, _GET_SPACE, 200),
        (AUTHORITY_PDS, _LIST_MEMBERS, 200),
        (AUTHORITY_PDS, _PUT_MEMBERS, 200),
        (AUTHORITY_PDS, _REMOVE_MEMBERS, 200),
        (AUTHORITY_PDS, _REMOVE_WRITER, 200),
        (AUTHORITY_PDS, _UPDATE_SPACE, 200),
        (AUTHORITY_PDS, _DELETE_SPACE, 200),
    ]
    assert {request.headers['authorization'] for request in network.requests} == {bearer}
    assert [request.url.params['space'] for request in network.requests[:2]] == [SPACE, SPACE]
    assert [json.loads(request.content)['space'] for request in network.requests[2:]] == [SPACE] * 5


def test_space_is_returned_with_its_policy(network: FakeSpaceNetwork) -> None:
    network.spaces[SPACE].policy = {'$type': _MEMBERSPACE_POLICY, 'publicRead': True, 'allowedApps': [_CLIENT_ID]}
    manager = make_manager(network)

    space = manager.get_space()

    assert space.space == SPACE
    assert isinstance(space.policy, models.ComAtprotoMemberspacePolicy.Main)
    assert (space.policy.public_read, space.policy.allowed_apps) == (True, [_CLIENT_ID])


def test_policy_that_only_the_host_knows_is_returned_and_sent_as_it_is(network: FakeSpaceNetwork) -> None:
    policy = {'$type': 'com.example.policy', 'level': 3}
    network.spaces[SPACE].policy = policy
    manager = make_manager(network)

    returned = manager.get_space().policy
    with pytest.raises(BadRequestError, match='UnsupportedPolicy'):
        manager.update_space(returned)

    assert isinstance(returned, DotDict)
    assert returned == policy
    assert _body(network, _UPDATE_SPACE) == {'space': SPACE, 'policy': policy}


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-manager.test.ts#L203-L211
def test_space_is_migrated_to_another_policy(network: FakeSpaceNetwork) -> None:
    manager = make_manager(network)

    assert manager.update_space(models.ComAtprotoManagedspacePolicy.Main(managing_app=_MANAGING_APP)) is True

    policy = manager.get_space().policy
    assert isinstance(policy, models.ComAtprotoManagedspacePolicy.Main)
    assert policy.managing_app == _MANAGING_APP
    assert _body(network, _UPDATE_SPACE) == {
        'space': SPACE,
        'policy': {'$type': _MANAGEDSPACE_POLICY, 'managingApp': _MANAGING_APP, 'publishPolicy': False},
    }
    assert network.spaces[SPACE].members == set()
    with pytest.raises(BadRequestError, match='PolicyMismatch'):
        manager.list_members()


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-manager.test.ts#L140-L160
def test_policy_is_changed_from_the_one_that_the_host_returned(network: FakeSpaceNetwork) -> None:
    network.spaces[SPACE].policy = {'$type': _MEMBERSPACE_POLICY, 'allowedApps': [_CLIENT_ID]}
    manager = make_manager(network)

    policy = manager.get_space().policy
    assert isinstance(policy, models.ComAtprotoMemberspacePolicy.Main)
    policy.public_read = True
    manager.update_space(policy)

    assert network.spaces[SPACE].policy == {
        '$type': _MEMBERSPACE_POLICY,
        'allowedApps': [_CLIENT_ID],
        'publicRead': True,
        'publicWrite': False,
        'publishMembers': False,
        'publishPolicy': False,
    }
    assert network.spaces[SPACE].members == {ALICE_DID, BOB_DID}


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-manager.test.ts#L235-L240
def test_space_is_deleted(network: FakeSpaceNetwork) -> None:
    network.put_record(SPACE, AUTHORITY_DID, _NOTE, 'a', {'$type': _NOTE})
    network.put_record(SPACE, BOB_DID, _NOTE, 'b', {'$type': _NOTE})
    manager = make_manager(network)

    assert manager.delete_space() is True
    assert manager.delete_space() is True

    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        manager.get_space()
    assert _body(network, _DELETE_SPACE) == {'space': SPACE}
    assert list(network.repos) == [(SPACE, BOB_DID)]


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-manager.test.ts#L213-L233
def test_writer_is_removed_from_the_writer_set(network: FakeSpaceNetwork) -> None:
    network.put_record(SPACE, BOB_DID, _NOTE, 'b', {'$type': _NOTE})
    manager = make_manager(network)

    assert manager.remove_writer(BOB_DID) is True
    assert manager.remove_writer(ALICE_DID) is True

    space = SpaceClient(
        manager.client, SPACE, id_resolver=fake_id_resolver(network), request=Request(transport=network.transport)
    )
    assert [(writer.py_type, writer.repo) for writer in space.writers()] == [
        ('com.atproto.space.defs#repoRemoved', BOB_DID)
    ]
    assert _body(network, _REMOVE_WRITER) == {'space': SPACE, 'repo': ALICE_DID}


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-manager.test.ts#L123-L137
def test_members_are_put_listed_and_removed(network: FakeSpaceNetwork) -> None:
    network.spaces[SPACE].members.clear()
    manager = make_manager(network)
    member = _member(BOB_DID, write=False)

    assert manager.put_members([member]) is True
    assert manager.list_members().members == [member]
    assert list(manager.members()) == [member]

    assert manager.remove_members([BOB_DID, _CAROL_DID]) is True
    assert list(manager.members()) == []

    assert _body(network, _PUT_MEMBERS) == {
        'space': SPACE,
        'members': [{'$type': 'com.atproto.memberspace.defs#member', 'did': BOB_DID, 'read': True, 'write': False}],
    }
    assert _body(network, _REMOVE_MEMBERS) == {'space': SPACE, 'dids': [BOB_DID, _CAROL_DID]}


def test_members_are_listed_in_pages(network: FakeSpaceNetwork) -> None:
    manager = make_manager(network)
    manager.put_members((_member(_CAROL_DID, read=False), _member(BOB_DID, write=False)))

    first = manager.list_members(limit=2)
    second = manager.list_members(2, first.cursor)

    assert first.members == [_member(ALICE_DID), _member(BOB_DID, write=False)]
    assert first.cursor == BOB_DID
    assert second.members == [_member(_CAROL_DID, read=False)]
    assert [request.url.params['limit'] for request in network.requests_to(_LIST_MEMBERS)] == ['2', '2']
    assert _cursors(network, _LIST_MEMBERS) == [None, BOB_DID]


def test_members_follow_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_MEMBERS] = [
        _page([ALICE_DID], 'first'),
        _page([], 'second'),
        _page([BOB_DID], 'third'),
        _page([]),
    ]
    manager = make_manager(network)

    members = list(manager.members())

    assert [member.did for member in members] == [ALICE_DID, BOB_DID]
    assert _cursors(network, _LIST_MEMBERS) == [None, 'first', 'second', 'third']
    assert all('limit' not in request.url.params for request in network.requests_to(_LIST_MEMBERS))


def test_members_stop_when_the_host_repeats_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_MEMBERS] = [
        _page([ALICE_DID], 'first'),
        _page([BOB_DID], 'first'),
        _page([_CAROL_DID]),
    ]
    manager = make_manager(network)

    members = list(manager.members())

    assert [member.did for member in members] == [ALICE_DID, BOB_DID]
    assert _cursors(network, _LIST_MEMBERS) == [None, 'first']


def test_members_are_not_fetched_before_the_iteration(network: FakeSpaceNetwork) -> None:
    manager = make_manager(network)

    members = manager.members()
    assert network.requests == []

    assert next(members).did == ALICE_DID
    assert network.count(_LIST_MEMBERS) == 1


def test_space_that_no_member_list_governs_has_no_members(network: FakeSpaceNetwork) -> None:
    network.spaces[SPACE].policy = {'$type': _PERSONALSPACE_POLICY}
    manager = make_manager(network)

    with pytest.raises(BadRequestError, match='PolicyMismatch'):
        list(manager.members())
    with pytest.raises(BadRequestError, match='PolicyMismatch'):
        manager.put_members([_member(BOB_DID)])
    with pytest.raises(BadRequestError, match='PolicyMismatch'):
        manager.remove_members([BOB_DID])
