from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    post = client.send_post('Test like-unlike from Python SDK')
    print('Post reference:', post)

    like = client.like(uri=post.uri, cid=post.cid)
    print('Like reference:', like)

    # this method return True/False depends on the response. could throw exceptions too
    print(client.unlike(like.uri))


if __name__ == '__main__':
    main()
