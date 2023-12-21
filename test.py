import asyncio
import logging
import os
import threading
import typing as t

from atproto import (
    CAR,
    AsyncClient,
    AsyncFirehoseSubscribeReposClient,
    AtUri,
    Client,
    FirehoseSubscribeReposClient,
    client_utils,
    exceptions,
    models,
    parse_subscribe_repos_message,
)
from atproto_client.models import get_model_as_dict, get_model_as_json, get_or_create, ids, is_record_type

if t.TYPE_CHECKING:
    from atproto_firehose.models import MessageFrame

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


def convert_uri_to_url() -> None:
    client = Client()
    client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    at = AtUri.from_str('at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3juce2ym7dt2g')
    path_type = None
    if at.collection == 'app.bsky.feed.post':
        path_type = 'post'
    # add more collections here...

    handle = client.app.bsky.actor.get_profile({'actor': at.hostname}).handle

    web_app_url = f'https://staging.bsky.app/profile/{handle}/{path_type}/{at.rkey}'
    print(web_app_url)
    # https://staging.bsky.app/profile/test.marshal.dev/post/3juce2ym7dt2g


def sync_main() -> None:
    client = Client()
    client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    post = client.get_post('3k2yihcrp6f2c')
    print(post)


    # with open('cat2.jpg', 'rb') as f:
    #     cat_data = f.read()
    #
    # upload = client.upload_blob(cat_data)
    # embed_external = models.AppBskyEmbedExternal.Main(
    #     external=models.AppBskyEmbedExternal.External(
    #         title='Test title',
    #         description='Test description',
    #         uri='https://atproto.blue',
    #         thumb=upload.blob,
    #     )
    # )
    #
    # client.send_post('test external with thumb', embed=embed_external)
    #
    # exit(0)

    post = client.get_post('3k2yihcrp6f2c')
    # print(client.get_posts(['at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3k2yihcrp6f2c']))
    # print(client.get_post_thread('at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3k2yihcrp6f2c'))
    # print(client.get_likes('at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3k2yihcrp6f2c'))
    # print(client.get_reposted_by('at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3k2yihcrp6f2c'))
    # print(client.get_timeline())
    # print(client.get_author_feed('test.marshal.dev'))
    # repost = client.repost(models.create_strong_ref(post))
    # print(client.unrepost(repost.uri))
    # print(client.follow('did:plc:kvwvcn5iqfooopmyzvb4qzba'))
    # print(client.unfollow('at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.graph.follow/3kgqtrsry3u2y'))

    params = models.AppBskyGraphGetSuggestedFollowsByActor.Params(actor='test.marshal.dev')
    result = client.app.bsky.graph.get_suggested_follows_by_actor(params)
    print(result)
    # print(client.get_follows('test.marshal.dev'))
    # print(client.get_followers('test.marshal.dev'))
    # print(client.get_profile('test.marshal.dev'))
    # print(client.get_profiles(['test.marshal.dev', 'marshal.dev']))
    # client.mute('test.marshal.dev')
    # client.unmute('test.marshal.dev'))
    # print(client.resolve_handle('bsky.app'))
    # print(client.upload_blob(b'lol'))
    # exit(0)

    # client.send_post(client_utils.TextBuilder().text('Test msg using ').link('Python SDK', 'https://atproto.blue/'))
    # text = client_utils.TextBuilder().text('Hello World from ').link('atpoto SDK', 'https://atproto.blue')
    # post = client.send_post(text)
    # print(post)

    text_builder = client_utils.TextBuilder()
    text_builder.tag('This is a rich message. ', 'atproto')
    text_builder.text('I can mention ')
    text_builder.mention('account', 'did:plc:kvwvcn5iqfooopmyzvb4qzba')
    text_builder.text(' and add clickable ')
    text_builder.link('link', 'https://atproto.blue/')

    text_builder = client_utils.TextBuilder().text('Test msg using ').link('Python SDK', 'https://atproto.blue/')

    client.send_post(text_builder)

    # with open('cat.png', 'rb') as f:
    #     cat_data = f.read()
    #     client.send_image(text_builder, cat_data, 'cat alt')

    # client.send_post(text_builder)

    # client.send_post('test timestamp')

    # session_string = client.export_session_string()
    # print(session_string)

    # client = Client()
    # client.login(session_string=os.environ['SESSION_STRING'])

    params = models.AppBskyGraphGetFollows.Params(actor='test.marshal.dev')
    # followers = client.app.bsky.graph.get_followers(params=params)
    followers = client.app.bsky.graph.get_follows(params=params)

    print(type(followers))
    print(followers)

    post = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.post', 'repo': 'test.marshal.dev', 'rkey': '3k2yihcrp6f2c'}
    )
    custom_post = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.post', 'repo': 'test.marshal.dev', 'rkey': '3k2yinh52ne2x'}
    )
    like = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.like', 'repo': 'test.marshal.dev', 'rkey': '3k5u7c7j7a52v'}
    )

    print(type(like.value))
    print(type(post.value))
    print(type(custom_post.value))
    print(custom_post.value)

    lexicon_correct_record = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.post', 'repo': 'test.marshal.dev', 'rkey': '3k2yihcrp6f2c'}
    )
    print(lexicon_correct_record.value.text)
    print(type(lexicon_correct_record.value))
    extended_record = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.post', 'repo': 'test.marshal.dev', 'rkey': '3k2yinh52ne2x'}
    )
    print(extended_record.value.text)
    print(extended_record.value.lol)  # custom (out of lexicon) attribute
    print(type(extended_record.value))

    exit(0)

    # client.com.atproto.admin.get_moderation_actions()

    # repo = client.com.atproto.sync.get_repo({'did': client.me.did})
    did = client.com.atproto.identity.resolve_handle({'handle': 'bsky.app'}).did
    repo = client.com.atproto.sync.get_repo({'did': did})
    car_file = CAR.from_bytes(repo)
    print(car_file.root)
    print(car_file.blocks)

    search_result = client.app.bsky.actor.search_actors_typeahead({'term': 'marshal'})
    for actor in search_result.actors:
        print(actor.handle, actor.display_name)

    # client.com.atproto.repo.get_record({'collection': 'app.bsky.feed.post', 'repo': 'arta.bsky.social'})

    with open('cat_big.png', 'rb') as f:
        cat_data = f.read()
        try:
            client.send_image('Cat looking for a Python', cat_data, 'cat alt')
        except exceptions.BadRequestError as e:
            print('Status code:', e.response.status_code)
            print('Error code:', e.response.content.error)
            print('Error message:', e.response.content.message)


async def main() -> None:
    async_client = AsyncClient()
    profile = await async_client.login(os.environ['USERNAME'], os.environ['PASSWORD'])
    print(profile)

    # text = client_utils.TextBuilder().text('Hello World from ').link('Python SDK', 'https://atproto.blue')
    # await async_client.send_post(text)

    # should be async open
    # with open('cat.png', 'rb') as f:
    #     cat_data = f.read()

    # await async_client.send_image('Cat', cat_data, 'async cat alt')

    resolve = await async_client.com.atproto.identity.resolve_handle(
        models.ComAtprotoIdentityResolveHandle.Params(handle=profile.handle)
    )
    assert resolve.did == profile.did


def _main_firehose_test() -> None:
    client = FirehoseSubscribeReposClient()

    def on_message_handler(message: 'MessageFrame') -> None:
        msg = parse_subscribe_repos_message(message)
        print('Message', message.header, msg)

        recreated_model = get_or_create(get_model_as_dict(msg), models.ComAtprotoSyncSubscribeRepos.Commit)
        assert msg.prev == recreated_model.prev
        # raise RuntimeError('kek')

    def on_callback_error_handler(e: BaseException) -> None:
        print('got error', e)
        # raise RuntimeError('rofl')

    def _stop_after_n_sec() -> None:
        from time import sleep

        sleep(3)
        client.stop()

    threading.Thread(target=_stop_after_n_sec).start()
    client.start(on_message_handler)
    # client.start(on_message_handler, on_callback_error_handler)
    print('stopped. start again')
    # client.start(on_message_handler, on_callback_error_handler)


async def _main_async_firehose_test() -> None:
    client = AsyncFirehoseSubscribeReposClient()

    async def on_message_handler(message: 'MessageFrame') -> None:
        print('Message', message.header, parse_subscribe_repos_message(message))
        # raise RuntimeError('kek')

    def on_callback_error_handler(e: BaseException) -> None:
        print('got error', e)
        # raise RuntimeError('rofl')

    async def _stop_after_n_sec() -> None:
        await asyncio.sleep(3)
        await client.stop()

    _ = asyncio.create_task(_stop_after_n_sec())
    await client.start(on_message_handler, on_callback_error_handler)

    # print('stopped. start again')
    # await client.start(on_message_handler, on_callback_error_handler)


if __name__ == '__main__':
    sync_main()
    # asyncio.get_event_loop().run_until_complete(main())

    # _main_firehose_test()
    # asyncio.get_event_loop().run_until_complete(_main_async_firehose_test())
