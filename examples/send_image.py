from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # replace the path to your image file
    with open('cat.jpg', 'rb') as f:
        img_data = f.read()

    client.send_image(text='Post with image from Python', image=img_data, image_alt='Text version of the image (ALT)')


if __name__ == '__main__':
    main()
