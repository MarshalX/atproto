from atproto import Client, models

# To send links as "link card" or "quote post" look at the send_embed.py example.
# There is a helper class TextBuilder
# that helps construct rich text: https://atproto.blue/en/latest/atproto_client/utils/text_builder.html


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    text = 'example link'
    url = 'https://google.com'

    facets = [
        models.AppBskyRichtextFacet.Main(
            features=[models.AppBskyRichtextFacet.Link(uri=url)],
            # we should pass when our link starts and ends in the text
            # the example below selects all the text
            index=models.AppBskyRichtextFacet.ByteSlice(byte_start=0, byte_end=len(text.encode('UTF-8'))),
        )
    ]

    client.send_post(text=text, facets=facets)


if __name__ == '__main__':
    main()
