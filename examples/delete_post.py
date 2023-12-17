from atproto import AtUri, Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # same with the like_post.py example we need to keep a reference to the post
    post_ref = client.send_post('Test send-delete from Python SDK')
    print('Post reference:', post_ref)

    # rkey means record key. The ID of the post object
    post_rkey = AtUri.from_str(post_ref.uri).rkey
    print('Post rkey:', post_rkey)

    # this method returns True/False depends on the response
    print('Deleted successfully:', client.delete_post(post_rkey))


if __name__ == '__main__':
    main()
