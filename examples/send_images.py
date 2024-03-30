from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # replace the path to your image file
    paths = ['cat.jpg', 'dog.jpg', 'bird.jpg']
    image_alts = ['Text version', 'of the image (ALT)', 'This parameter is optional']

    images = []
    for path in paths:
        with open(path, 'rb') as f:
            images.append(f.read())

    client.send_images(text='Post with image from Python', images=images, image_alts=image_alts)


if __name__ == '__main__':
    main()
