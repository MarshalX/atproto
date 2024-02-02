from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    post = client.send_post(text='Hello World from Python!')
    print('Post reference:', post)

    print('Like reference:', client.like(uri=post.uri, cid=post.cid))


if __name__ == '__main__':
    main()
