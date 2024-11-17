from time import sleep

from atproto_client import Client, models
from atproto_core.uri import AtUri
from atproto_identity.resolver import IdResolver


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # https://bsky.app/profile/test.marshal.dev/lists/3k5z5k4k6qw2r
    mod_list_uri = 'at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.graph.list/3k5z5k4k6qw2r'
    user_handle_to_add = 'test.marshal.dev'

    mod_list_owner = AtUri.from_str(mod_list_uri).host
    user_to_add = IdResolver().handle.resolve(user_handle_to_add)

    print(f'Adding {user_to_add} to the list {mod_list_uri} (owned by {mod_list_owner})')

    created_list_item = client.app.bsky.graph.listitem.create(
        mod_list_owner,
        models.AppBskyGraphListitem.Record(
            list=mod_list_uri,
            subject=user_to_add,
            created_at=client.get_current_time_iso(),
        ),
    )

    print(f'Created list item: CID={created_list_item.cid}; URI={created_list_item.uri}')

    sleep(3)  # sleep for 3 sec because it takes some time to update the list for the backend

    mod_list = client.app.bsky.graph.get_list(models.AppBskyGraphGetList.Params(list=mod_list_uri))
    mod_list_users = [item.subject.did for item in mod_list.items]
    print(f'List users: {mod_list_users}')
    assert user_to_add in mod_list_users, f'User {user_to_add} not found in the list {mod_list_uri}'  # noqa: S101

    deleted_success = client.app.bsky.graph.listitem.delete(mod_list_owner, AtUri.from_str(created_list_item.uri).rkey)
    print(f'Deleted list item: {deleted_success}')


if __name__ == '__main__':
    main()
