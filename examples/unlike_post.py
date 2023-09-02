from atproto import AtUri, Client
from atproto.xrpc_client.models.utils import create_strong_ref


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    response = client.send_post('Test like-unlike from Python SDK')
    print('Post response:', response)

    # same with the like_post.py example, we need to work with references of posts and likes
    like_ref = client.like(create_strong_ref(response))
    print('Like reference:', like_ref)

    # rkey means a record key. the ID of the like object
    like_rkey = AtUri.from_str(like_ref.uri).rkey
    print('Like rkey:', like_rkey)

    # this method return True/False depends on the response. could throw exceptions too
    print(client.unlike(like_rkey))


if __name__ == '__main__':
    main()
