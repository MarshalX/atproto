from atproto import Client, IdResolver, models

USERNAME = 'example.com'
PASSWORD = 'hunter2'  # noqa: S105 never hardcode your password in a real application


def main() -> None:
    # create resolver instance with in-memory cache
    id_resolver = IdResolver()

    # create client instance and login
    client = Client()
    client.login(USERNAME, PASSWORD)

    convo_list = client.chat.bsky.convo.list_convos()  # use limit and cursor to paginate
    print(f'Your conversations ({len(convo_list.convos)}):')
    for convo in convo_list.convos:
        members = ', '.join(member.display_name for member in convo.members)
        print(f'- ID: {convo.id} ({members})')

    # resolve DID
    chat_to = id_resolver.handle.resolve('test.marshal.dev')

    # create or get conversation with chat_to
    convo = client.chat.bsky.convo.get_convo_for_members(
        models.ChatBskyConvoGetConvoForMembers.Params(members=[chat_to]),
    )
    print(f'\nConvo ID: {convo.convo.id}')
    print('Convo members:')
    for member in convo.convo.members:
        print(f'- {member.display_name} ({member.did})')

    # send a message to the conversation
    client.chat.bsky.convo.send_message(
        models.ChatBskyConvoSendMessage.Data(
            convo_id=convo.convo.id,
            message=models.ChatBskyConvoDefs.MessageInput(
                text='Hello from Python SDK!',
            ),
        )
    )

    print('\nMessage sent!')


if __name__ == '__main__':
    main()
