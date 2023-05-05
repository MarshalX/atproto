import asyncio
import logging
import os

from atproto import AsyncClient, AtUri, Client, models

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

# TODO(MarshalX): add record namespaces with 5 const methods? CRUDL


def sync_main():
    client = Client()
    # client = Client('http://localhost:8000')
    profile = client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    print(profile)

    # with open('cat2.jpg', 'rb') as f:
    #     cat_data = f.read()
    #
    #     client.send_image('Cat looking for a Python', cat_data, 'cat alt')
    #
    # resolve = client.com.atproto.identity.resolve_handle(models.ComAtprotoIdentityResolveHandle.Params(profile.handle))
    # assert resolve.did == profile.did

    print(client.com.atproto.server.describe_server())

    # post_ref = client.send_post('Test like-unlike')
    # print('post ref', post_ref)
    # like_ref = client.like(post_ref)
    # print('like ref', like_ref)
    # like_rkey = AtUri.from_str(like_ref.uri).rkey
    # print('like rkey', like_rkey)
    # print(client.unlike(like_rkey))

    # reply = client.send_post('reply to root test', reply_to=models.AppBskyFeedPost.ReplyRef(created_post, created_post))
    # reply_to_reply = client.send_post('reply to reply test', reply_to=models.ReplyRef(reply, created_post))
    # reply = client.send_post('reply to root test 2', reply_to=models.ReplyRef(created_post, created_post))


async def main():
    async_client = AsyncClient()
    profile = await async_client.login(os.environ['USERNAME'], os.environ['PASSWORD'])
    print(profile)

    # should be async open
    # with open('cat2.png', 'rb') as f:
    #     cat_data = f.read()

    # await async_client.send_image('Cat looking for a Async Python', cat_data, 'async cat alt')

    # resolve = await async_client.com.atproto.identity.resolve_handle(
    #     models.ComAtprotoIdentityResolveHandle.Params(profile.handle)
    # )
    # assert resolve.did == profile.did


if __name__ == '__main__':
    sync_main()
    # asyncio.get_event_loop().run_until_complete(main())
