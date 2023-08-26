import asyncio
import logging
import os
import threading
import typing as t

from atproto import CAR, AsyncClient, AtUri, Client, exceptions, models
from atproto.firehose import (
    AsyncFirehoseSubscribeReposClient,
    FirehoseSubscribeReposClient,
    parse_subscribe_repos_message,
)
from atproto.xrpc_client.models import get_model_as_dict, ids, is_record_type, get_model_as_json

if t.TYPE_CHECKING:
    from atproto.firehose import MessageFrame

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


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
    h = client.com.atproto.identity.resolve_handle({'handle': 'bsky.app'})
    s = client.bsky.actor.search_actors_typeahead({'term': 'bsky'})

    # post_ref = client.send_post(text='Hello World from Python!')

    # We can put likes only with reference to the post. You need to create/get post first to be able to like it
    # cid='bafyreidaszwnbzl65oqryswowxzrexlqfeoh47zhtvo65yv5wblosgdrkq' uri='at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.like/3k5u5ammyg72r'
    # r = client.like(models.ComAtprotoRepoStrongRef.Main(cid=post_ref.cid, uri=post_ref.uri))
    # print(r)

    feed = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.generator', 'repo': 'did:plc:2wqb5jjkxli4rcswpyb624xj', 'rkey': 'Filecoin'}
    )
    post = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.post', 'repo': 'test.marshal.dev', 'rkey': '3k2yihcrp6f2c'}
    )
    custom_post = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.post', 'repo': 'test.marshal.dev', 'rkey': '3k2yinh52ne2x'}
    )
    custom_like = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.like', 'repo': 'test.marshal.dev', 'rkey': '3k5u5ammyg72r'}
    )
    like = client.com.atproto.repo.get_record(
        {'collection': 'app.bsky.feed.like', 'repo': 'test.marshal.dev', 'rkey': '3k5u7c7j7a52v'}
    )
    print(type(feed.value))
    print(get_model_as_json(feed.value))
    print(get_model_as_json(feed.value.avatar))

    print(type(like.value))
    print(type(post.value))
    print(type(custom_like.value))
    print(type(custom_post.value))
    print(custom_post.value)
    print(custom_like.value)

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

    did_doc = client.com.atproto.repo.describe_repo({'repo': 'did:plc:ze3uieyyns7prike7itbdjiy'}).didDoc
    print(type(did_doc))
    print(did_doc)
    print(did_doc.service)
    print(did_doc['service'])
    print(did_doc['@context'])

    atproto_feed = client.com.atproto.repo.get_record(
        {'collection': ids.AppBskyFeedGenerator, 'repo': 'marshal.dev', 'rkey': 'atproto'}
    ).value
    print(atproto_feed)
    print(atproto_feed.createdAt)
    print(atproto_feed['createdAt'])
    print(type(atproto_feed))

    assert is_record_type(lexicon_correct_record.value, ids.AppBskyFeedPost) is True
    assert is_record_type(lexicon_correct_record.value, ids.AppBskyFeedGenerator) is False

    assert is_record_type(extended_record.value, ids.AppBskyFeedPost) is True
    assert is_record_type(extended_record.value, ids.AppBskyFeedGenerator) is False
    assert is_record_type(extended_record.value, models.AppBskyFeedPost) is True
    assert is_record_type(extended_record.value, models.AppBskyFeedGenerator) is False
    dict_model = get_model_as_dict(extended_record.value)
    assert isinstance(dict_model, dict) is True

    post_uri = 'at://did:plc:hbtuqflamm5j2i7yahtzsnue/app.bsky.feed.post/3k3ic43ucbq2f'
    response = client.bsky.feed.get_post_thread({'uri': post_uri, 'depth': 1, 'parentHeight': 0})
    assert response.thread.post.embed.py_type == 'app.bsky.embed.recordWithMedia#view'

    exit(0)

    # client.com.atproto.admin.get_moderation_actions()

    # repo = client.com.atproto.sync.get_repo({'did': client.me.did})
    did = client.com.atproto.identity.resolve_handle({'handle': 'bsky.app'}).did
    repo = client.com.atproto.sync.get_repo({'did': did})
    car_file = CAR.from_bytes(repo)
    print(car_file.root)
    print(car_file.blocks)

    search_result = client.bsky.actor.search_actors_typeahead()
    # search_result = client.bsky.actor.search_actors_typeahead({'term': 'marshal'})
    for actor in search_result.actors:
        print(actor.handle, actor.displayName)

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

    # await async_client.send_image('Cat looking for an Async Python', cat_data, 'async cat alt')

    # resolve = await async_client.com.atproto.identity.resolve_handle(
    #     models.ComAtprotoIdentityResolveHandle.Params(profile.handle)
    # )
    # assert resolve.did == profile.did


def _main_firehose_test():
    client = FirehoseSubscribeReposClient()

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

    threading.Thread(target=_stop_after_n_sec).start()
    client.start(on_message_handler, on_callback_error_handler)
    print('stopped. start again')
    # client.start(on_message_handler, on_callback_error_handler)


async def _main_async_firehose_test():
    client = AsyncFirehoseSubscribeReposClient()

    async def on_message_handler(message: 'MessageFrame') -> None:
        print('Message', message.header, parse_subscribe_repos_message(message))
        # raise RuntimeError('kek')

    def on_callback_error_handler(e: BaseException) -> None:
        print('got error', e)
        # raise RuntimeError('rofl')

    async def _stop_after_n_sec():
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
