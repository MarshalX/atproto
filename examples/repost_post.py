from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    post_ref = client.send_post(text='Hello World from Python!')
    print('Post reference:', post_ref)

    print('Reposted post reference:', client.repost(uri=post_ref.uri, cid=post_ref.cid))


if __name__ == '__main__':
    main()
