from atproto import Client, models


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    text = 'Example post with embed external resource (link card)'
    # AppBskyEmbedExternal is the same as "link card" in the app
    embed_external = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            title='Google',
            description='Google Home Page',
            uri='https://google.com',
        )
    )

    post_with_link_card = client.send_post(text=text, embed=embed_external)

    text_quote = 'Example post with embed post and quote (quote post)'
    # AppBskyEmbedRecord is the same as "quote post" in the app
    embed_post = models.AppBskyEmbedRecord.Main(record=models.create_strong_ref(post_with_link_card))

    client.send_post(text=text_quote, embed=embed_post)


if __name__ == '__main__':
    main()
