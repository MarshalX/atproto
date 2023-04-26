import asyncio
import os
from typing import Tuple

import httpx

ATP_BASE_URL = 'https://bsky.social/xrpc'


async def get_token(identifier: str, password: str) -> Tuple[str, str]:
    async with httpx.AsyncClient() as client:
        url = f'{ATP_BASE_URL}/com.atproto.server.createSession'
        res = await client.post(url, json={'identifier': identifier, 'password': password})
        if res.status_code == 200:
            content = res.json()
            return content['did'], content['accessJwt']

    raise ValueError('Can\'t get access token')


async def resolve_handle(handle: str, token: str) -> str:
    async with httpx.AsyncClient() as client:
        url = f'{ATP_BASE_URL}/com.atproto.identity.resolveHandle'
        res = await client.get(url, params={'handle': handle}, headers={'Authorization': f'Bearer {token}'})
        if res.status_code == 200:
            content = res.json()
            return content['did']

    raise ValueError('Can\'t get resolve handle')


async def main():
    did_expected, token = await get_token(os.environ['USERNAME'], os.environ['PASSWORD'])
    did_actual = await resolve_handle(os.environ['HANDLE'], token)

    assert did_expected == did_actual


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
