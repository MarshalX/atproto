from atproto import Client, models


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    root_post_ref = client.send_post('Post from Python SDK')

    # reply to the root post. We need to pass ReplyRef with root and parent
    reply_to_root = client.send_post(
        text='Reply to the root post', reply_to=models.AppBskyFeedPost.ReplyRef(root_post_ref, root_post_ref)
    )

    # to reply on reply we need to change the "parent" field. let's reply to our previous reply
    client.send_post(
        text='Reply to the parent reply', reply_to=models.AppBskyFeedPost.ReplyRef(reply_to_root, reply_to_root)
    )


if __name__ == '__main__':
    main()
