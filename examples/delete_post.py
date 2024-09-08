from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # same with the like_post.py example we need to keep a reference to the post
    post_ref = client.send_post('Test send-delete from Python SDK')
    print('Post reference:', post_ref)

    # this method returns True/False depends on the response
    print('Deleted successfully:', client.delete_post(post_ref.uri))


if __name__ == '__main__':
    main()
