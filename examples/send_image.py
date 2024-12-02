from atproto import Client, models


def main() -> None:
    client = Client()
    client.login("my-handle", "my-password")

    # replace the path to your image file
    with open("cat.jpg", "rb") as f:
        img_data = f.read()

    aspect_ratio = models.AppBskyEmbedDefs.AspectRatio(height=100, width=100)

    client.send_image(
        text="Post with image from Python",
        image=img_data,
        image_alt="Text version of the image (ALT)",
        image_aspect_ratio=aspect_ratio,
    )


if __name__ == "__main__":
    main()
