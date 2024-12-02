from atproto import Client, models


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # replace the path to your image file
    paths = ['cat.jpg', 'dog.jpg', 'bird.jpg']
    image_alts = [
        'Text version',
        'of the image (ALT)',
        'This parameter is optional',
    ]
    image_aspect_ratios = [
        models.AppBskyEmbedDefs.AspectRatio(height=1, width=1),
        models.AppBskyEmbedDefs.AspectRatio(height=4, width=3),
        models.AppBskyEmbedDefs.AspectRatio(height=16, width=9),
    ]

    images = []
    for path in paths:
        with open(path, 'rb') as f:
            images.append(f.read())

    client.send_images(
        text='Post with image from Python',
        images=images,
        image_alts=image_alts,
        image_aspect_ratios=image_aspect_ratios,
    )


if __name__ == '__main__':
    main()
