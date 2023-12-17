from atproto import Client, models


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    response = client.send_post(text='Hello World from Python!')

    # We can put likes only with reference to the post. You need to create/get post first to be able to like it
    client.like(models.create_strong_ref(response))


if __name__ == '__main__':
    main()
