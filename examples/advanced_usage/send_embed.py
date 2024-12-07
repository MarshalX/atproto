import httpx
from atproto import Client, models

DEFAULT_IMAGE_URL = 'https://cdn.bsky.app/img/avatar/plain/did:plc:kvwvcn5iqfooopmyzvb4qzba/bafkreicwqcugdgubtawr6xv6jjifoju67eigwx2xgz4zs73nkzzn36oucy@jpeg'


def main(handle: str, password: str) -> None:
    client = Client()
    client.login(handle, password)

    # Example 1: Link card embed
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

    # Example 2: Simple quote post
    text_quote = 'Example post with embed post and quote (quote post)'
    # AppBskyEmbedRecord is the same as "quote post" in the app
    embed_post = models.AppBskyEmbedRecord.Main(record=models.create_strong_ref(post_with_link_card))
    client.send_post(text=text_quote, embed=embed_post)

    # Example 3: Quote post with image
    img_data = httpx.get(DEFAULT_IMAGE_URL).content
    uploaded_blob = client.upload_blob(img_data).blob

    embed_post_with_image = models.AppBskyEmbedRecordWithMedia.Main(
        record=models.AppBskyEmbedRecord.Main(record=models.create_strong_ref(post_with_link_card)),
        media=models.AppBskyEmbedImages.Main(
            images=[
                models.AppBskyEmbedImages.Image(
                    image=uploaded_blob,
                    alt='Example image with quote',
                    aspect_ratio=models.AppBskyEmbedDefs.AspectRatio(width=1, height=1),
                )
            ]
        ),
    )

    client.send_post(text='Example post with both quote and image', embed=embed_post_with_image)


if __name__ == '__main__':
    main(handle='my-handle', password='my-password')  # noqa: S106
