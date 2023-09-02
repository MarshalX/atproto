from atproto import Client
from atproto.xrpc_client.models.utils import create_strong_ref


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    response = client.send_post(text='Hello World from Python!')
    print('Post response:', response)

    # As in the like_post.py example, we need to create a reference to the post to repost
    print('Reposted post response:', client.repost(create_strong_ref(response)))


if __name__ == '__main__':
    main()
