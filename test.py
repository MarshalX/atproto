import asyncio
import logging
import os

from atproto import AsyncClient, Client, models
from atproto.models import com

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

# TODO(MarshalX): add record namespaces with 5 const methods? CRUDL

# client.com.atproto.identity.resolve_handle({'handle': 'test'})
# client.com.atproto.identity.resolve_handle({'handle': 123})     # expect WrongTypeError
# client.com.atproto.moderation.create_report({'reasonType1': 'test', 'subject': 1})     # expect MissingValueError
# client.com.atproto.identity.resolve_handle({'aaa': 1})     # expect UnexpectedFieldError


def sync_main():
    client = Client()
    profile = client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    print(profile)

    with open('cat.png', 'rb') as f:
        cat_data = f.read()

        upload = client.com.atproto.repo.upload_blob(cat_data)
        print(upload.blob.cid.human_readable)

        images = 1 * [models.Image(alt='img alt test', image=upload.blob)]
        # client.send_post('Test post from Python SDK with embed images', embed=models.Images(images=images))

    # resolve = client.com.atproto.identity.resolve_handle(models.ResolveHandleParams(profile.handle))
    # assert resolve.did == profile.did

    # print(client.com.atproto.server.describe_server())

    # created_post = client.send_post('Test post')
    # reply = client.send_post('reply to root test', reply_to=models.ReplyRef(created_post, created_post))
    # reply_to_reply = client.send_post('reply to reply test', reply_to=models.ReplyRef(reply, created_post))
    # reply = client.send_post('reply to root test 2', reply_to=models.ReplyRef(created_post, created_post))


async def main():
    async_client = AsyncClient()
    profile = await async_client.login(os.environ['USERNAME'], os.environ['PASSWORD'])
    print(profile)

    resolve = await async_client.com.atproto.identity.resolve_handle(models.ResolveHandleParams(profile.handle))
    assert resolve.did == profile.did


if __name__ == '__main__':
    sync_main()
    # asyncio.get_event_loop().run_until_complete(main())
