from atproto import Client
from atproto.xrpc_client.models.utils import create_strong_ref


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    response = client.send_post(text='Hello World from Python!')

    # We can put likes only with reference to the post. You need to create/get post first to be able to like it
    client.like(create_strong_ref(response))


if __name__ == '__main__':
    main()
