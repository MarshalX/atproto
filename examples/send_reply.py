from atproto import Client, models


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    root_post_ref = models.create_strong_ref(client.send_post('Post from Python SDK'))

    # Reply to the root post. We need to pass ReplyRef with root and parent
    reply_to_root = models.create_strong_ref(
        client.send_post(
            text='Reply to the root post',
            reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref),
        )
    )

    # To reply on reply, we need to change the "parent" field. Let's reply to our previous reply
    client.send_post(
        text='Reply to the parent reply',
        reply_to=models.AppBskyFeedPost.ReplyRef(parent=reply_to_root, root=root_post_ref),
    )


if __name__ == '__main__':
    main()
