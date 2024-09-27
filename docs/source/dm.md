# Direct Messages (Chats)

Bluesky Direct Messages were launched on May 22, 2024. It began as a simple chat system for Bluesky users to communicate with one another. Currently, only text messages are supported. 

The Python SDK has supported the Bluesky Direct Messages API since day one. You can use the SDK to send messages to other users, create new conversations, list existing conversations, and perform all other functions available in the mobile app and web client.

**You need to grant access to direct messages when creating App Password!** Otherwise, you will get "Bad token scope" error.

## Example

This example demonstrates how to list conversations, create a new conversation, and send a message to it.

```python
from atproto import Client, IdResolver, models

USERNAME = 'example.com'
PASSWORD = 'hunter2'  # never hardcode your password in a real application


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

```
