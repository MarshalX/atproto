import asyncio
import logging
import os

from atproto import AsyncClient, AtUri, Client, models

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

    # with open('cat2.jpg', 'rb') as f:
    #     cat_data = f.read()
    #
    #     client.send_image('Cat looking for a Python', cat_data, 'cat alt')
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


if __name__ == '__main__':
    # test_strange_embed_images_type()
    sync_main()
    # asyncio.get_event_loop().run_until_complete(main())
