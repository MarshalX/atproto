import asyncio
import logging
import os
import threading

from atproto import CAR, AsyncClient, AtUri, Client, exceptions, models
from atproto.firehose import (
    AsyncFirehoseSubscribeLabelsClient,
    AsyncFirehoseSubscribeReposClient,
    FirehoseSubscribeLabelsClient,
    FirehoseSubscribeReposClient,
    parse_subscribe_repos_message,
)

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

# TODO(MarshalX): add record namespaces with 5 const methods? CRUDL


def convert_uri_to_url():
    client = Client()
    client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    at = AtUri.from_str('at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3juce2ym7dt2g')
    path_type = None
    if at.collection == 'app.bsky.feed.post':
        path_type = 'post'
    # add more collections here...

    handle = client.bsky.actor.get_profile({'actor': at.hostname}).handle

    web_app_url = f'https://staging.bsky.app/profile/{handle}/{path_type}/{at.rkey}'
    print(web_app_url)
    # https://staging.bsky.app/profile/test.marshal.dev/post/3juce2ym7dt2g


def sync_main():
    client = Client()
    client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    # repo = client.com.atproto.sync.get_repo({'did': client.me.did})
    # did = client.com.atproto.identity.resolve_handle({'handle': 'bsky.app'}).did
    # repo = client.com.atproto.sync.get_repo({'did': did})
    # car_file = CAR.from_bytes(repo)
    # print(car_file.root)
    # print(car_file.nodes)

    # res = client.com.atproto.repo.get_record(...)     # implement by yourself
    # also you need to parse "res.value" as profile record using  get_or_create_model method

    # search_result = client.bsky.actor.search_actors_typeahead({'term': 'marshal'})
    # for actor in search_result.actors:
    #     print(actor.handle, actor.displayName)

    # session = client.com.atproto.server.create_session({'identifier': 'my-handle', 'password': 'my-pass'})
    # token = session.accessJwt
    # refresh_token = session.refreshJwt
    #
    # refreshed_session = client.com.atproto.server.refresh_session(headers={'Authorization': f'Bearer {refresh_token}'})
    # new_token = refreshed_session.accessJwt

    # client.com.atproto.repo.get_record({'collection': 'app.bsky.feed.post', 'repo': 'arta.bsky.social'})

    with open('cat_big.png', 'rb') as f:
        cat_data = f.read()
        try:
            client.send_image('Cat looking for a Python', cat_data, 'cat alt')
        except exceptions.BadRequestError as e:
            print('Status code:', e.response.status_code)
            print('Error code:', e.response.content.error)
            print('Error message:', e.response.content.message)
    #
    # resolve = client.com.atproto.identity.resolve_handle(models.ComAtprotoIdentityResolveHandle.Params(profile.handle))
    # assert resolve.did == profile.did

    # print(client.com.atproto.server.describe_server())

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


def test_strange_embed_images_type():
    d = {
        'text': 'Jack will save us from Elon I hope he doesn’t sell us out again @jack.bsky.social here’s to the future in the present moment #bluesky',
        'embed': {
            '$type': 'app.bsky.embed.images',
            'images': [
                {
                    'alt': '',
                    'image': {
                        'cid': 'bafkreib66ejhcuiomfqusm52xriallilizk6uqppymyaz7dmz7yargpwhi',
                        'mimeType': 'image/jpeg',
                    },
                }
            ],
        },
        'entities': [
            {'type': 'mention', 'index': {'end': 81, 'start': 64}, 'value': 'did:plc:6fktaamhhxdqb2ypum33kbkj'}
        ],
        'createdAt': '2023-03-26T15:36:13.302Z',
    }
    from atproto.xrpc_client.models.utils import get_or_create_model

    m = get_or_create_model(d, models.AppBskyFeedPost.Main)
    print(m)


def _main_firehose_test():
    client = FirehoseSubscribeReposClient()
    # client = FirehoseSubscribeLabelsClient()

    def on_message_handler(message: 'MessageFrame') -> None:
        print('Message', message.header, parse_subscribe_repos_message(message))
        # raise RuntimeError('kek')

    def on_callback_error_handler(e: BaseException) -> None:
        print('got error', e)
        # raise RuntimeError('rofl')

    def _stop_after_n_sec():
        from time import sleep

        sleep(3)
        client.stop()

    # threading.Thread(target=_stop_after_n_sec).start()
    client.start(on_message_handler)
    # client.start(on_message_handler, on_callback_error_handler)
    print('stopped. start again')
    # client.start(on_message_handler, on_callback_error_handler)


async def _main_async_firehose_test():
    client = AsyncFirehoseSubscribeReposClient()
    # client = AsyncFirehoseSubscribeLabelsClient()

    async def on_message_handler(message: 'MessageFrame') -> None:
        print('Message', message.header, parse_subscribe_repos_message(message, decode_inner_cbor=False))
        # raise RuntimeError('kek')
        await asyncio.sleep(0.1)

    def on_callback_error_handler(e: BaseException) -> None:
        print('got error', e)
        # raise RuntimeError('rofl')

    async def _stop_after_n_sec():
        await asyncio.sleep(3)
        await client.stop()

    asyncio.create_task(_stop_after_n_sec())
    await client.start(on_message_handler)
    # await client.start(on_message_handler, on_callback_error_handler)
    print('stopped. start again')
    # await client.start(on_message_handler, on_callback_error_handler)


if __name__ == '__main__':
    # test_strange_embed_images_type()

    sync_main()
    # asyncio.get_event_loop().run_until_complete(main())

    # _main_firehose_test()
    # asyncio.get_event_loop().run_until_complete(_main_async_firehose_test())
