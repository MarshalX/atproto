from atproto import AtUri, Client


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    # As in the like_post.py example we need to keep a reference to the post to repost
    post_ref = client.send_post(text='Hello World from Python!')
    print('Post reference:', post_ref)

    # this methods return True/False depends on the response. Could throw exceptions too
    client.repost(post_ref)


if __name__ == '__main__':
    main()
