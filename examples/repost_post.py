from atproto import Client


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    # As in the like_post.py example we need to keep a reference to the post to repost
    post_ref = client.send_post(text='Hello World from Python!')
    print('Post reference:', post_ref)

    # this method returns reference to created repost
    client.repost(post_ref)


if __name__ == '__main__':
    main()
