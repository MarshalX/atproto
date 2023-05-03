import asyncio
import logging
import os

from atproto import AsyncClient, Client, models

logging.basicConfig(level=logging.DEBUG)

# TODO(MarshalX): add support of records? namespaces with 5 const methods? CRUDL

# client.com.atproto.identity.resolve_handle({'handle': 'test'})
# client.com.atproto.identity.resolve_handle({'handle': 123})     # expect WrongTypeError
# client.com.atproto.moderation.create_report({'reasonType1': 'test', 'subject': 1})     # expect MissingValueError
# client.com.atproto.identity.resolve_handle({'aaa': 1})     # expect UnexpectedFieldError

# m = get_or_create_model({'handle': None}, ResolveHandleParams)
# import dataclasses, json
# print(json.dumps(dataclasses.asdict(m)))  # TODO(MarshalX): exclude null values?


def sync_main():
    client = Client()

    profile = client.login(os.environ['USERNAME'], os.environ['PASSWORD'])
    print(profile)

    resolve = client.com.atproto.identity.resolve_handle(models.ResolveHandleParams(profile.handle))
    assert resolve.did == profile.did


async def main():
    async_client = AsyncClient()
    profile = await async_client.login(os.environ['USERNAME'], os.environ['PASSWORD'])
    print(profile)

    resolve = await async_client.com.atproto.identity.resolve_handle(models.ResolveHandleParams(profile.handle))
    assert resolve.did == profile.did


if __name__ == '__main__':
    sync_main()
    asyncio.get_event_loop().run_until_complete(main())
