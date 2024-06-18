from atproto import Client, IdResolver, models

USERNAME = 'example.com'
PASSWORD = 'hunter2'  # noqa: S105 never hardcode your password in a real application


def main() -> None:
    # create client instance and login
    client = Client()
    client.login(USERNAME, PASSWORD)  # use App Password with access to Direct Messages!

    # create client proxied to Bluesky Chat service
    dm_client = client.with_bsky_chat_proxy()
    # create shortcut to convo methods
    dm = dm_client.chat.bsky.convo

    convo_list = dm.list_convos()  # use limit and cursor to paginate
    print(f'Your conversations ({len(convo_list.convos)}):')
    for convo in convo_list.convos:
        members = ', '.join(member.display_name for member in convo.members)
        print(f'- ID: {convo.id} ({members})')

    # create resolver instance with in-memory cache
    id_resolver = IdResolver()
    # resolve DID
    chat_to = id_resolver.handle.resolve('test.marshal.dev')

    # create or get conversation with chat_to
    convo = dm.get_convo_for_members(
        models.ChatBskyConvoGetConvoForMembers.Params(members=[chat_to]),
    ).convo

    print(f'\nConvo ID: {convo.id}')
    print('Convo members:')
    for member in convo.members:
        print(f'- {member.display_name} ({member.did})')

    # send a message to the conversation
    dm.send_message(
        models.ChatBskyConvoSendMessage.Data(
            convo_id=convo.id,
            message=models.ChatBskyConvoDefs.MessageInput(
                text='Hello from Python SDK!',
            ),
        )
    )

    print('\nMessage sent!')


if __name__ == '__main__':
    main()
