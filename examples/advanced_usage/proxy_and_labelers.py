from atproto import Client

USERNAME = 'example.com'
PASSWORD = 'hunter2'  # noqa: S105 never hardcode your password in a real application


def main() -> None:
    client = Client()
    client.login(USERNAME, PASSWORD)  # use App Password with access to Direct Messages!

    # `with_*` returns a configured clone; the original client keeps its own headers
    dm_client = client.with_bsky_chat_proxy()
    print('Proxy header:', dm_client.request.get_headers()['atproto-proxy'])
    print('Set on the original client:', 'atproto-proxy' in client.request.get_headers())

    # spelled out, this is what the convenience wrapper above does
    dm_client = client.with_proxy(Client.AtprotoServiceType.BSKY_CHAT, Client.BSKY_CHAT_DID)

    convos = dm_client.chat.bsky.convo.list_convos()
    print(f'You have {len(convos.convos)} conversations.')

    # ask the AppView to apply the labels of the Bluesky moderation service
    labeled_client = client.with_bsky_labeler()
    print('Labelers header:', labeled_client.request.get_headers()['atproto-accept-labelers'])

    # any set of labeler DIDs works
    labeled_client = client.with_labelers([Client.BSKY_LABELER_DID])

    profile = labeled_client.get_profile(USERNAME)
    for label in profile.labels or []:
        print(f'- {label.val} (from {label.src})')

    # clones share the session, so a token refresh on one is visible to all of them
    print('Same session:', client.export_session_string() == dm_client.export_session_string())


if __name__ == '__main__':
    main()
