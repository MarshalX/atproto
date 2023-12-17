from atproto import Client, models


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    response = client.send_post('Test like-unlike from Python SDK')
    print('Post response:', response)

    # same with the like_post.py example, we need to work with references of posts and likes
    like_ref = client.like(models.create_strong_ref(response))
    print('Like reference:', like_ref)

    # this method return True/False depends on the response. could throw exceptions too
    print(client.unlike(like_ref.uri))


if __name__ == '__main__':
    main()
