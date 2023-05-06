from atproto import Client


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    post_ref = client.send_post(text='Hello World from Python!')

    # We can put likes only with reference to the post. You need to create/get post first to be able to like it
    client.like(post_ref)


if __name__ == '__main__':
    main()
