from atproto import AtUri, Client


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    # same with the like_post.py example we need to for with references of posts and likes

    post_ref = client.send_post('Test like-unlike from Python SDK')
    print('Post reference:', post_ref)

    like_ref = client.like(post_ref)
    print('Like reference:', like_ref)

    # rkey means record key. The ID of the like object
    like_rkey = AtUri.from_str(like_ref.uri).rkey
    print('Like rkey:', like_rkey)

    # this methods return True/False depends on the response. Could throw exceptions too
    print(client.unlike(like_rkey))


if __name__ == '__main__':
    main()
