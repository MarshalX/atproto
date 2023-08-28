from pathlib import Path

from atproto.codegen import DISCLAIMER, format_code, write_code

_CLIENT_DIR = Path(__file__).parent.parent.parent.joinpath('xrpc_client', 'client')


def gen_client(input_filename: str, output_filename: str) -> None:
    with open(_CLIENT_DIR.joinpath(input_filename), 'r', encoding='UTF-8') as f:
        code = f.read()

    # TODO(MarshalX): Get automatically
    methods = [
        'send_post',
        'send_image',
        '_get_and_set_session',
        '_refresh_and_set_session',
        '_invoke',
    ]

    code = code.replace('from threading', 'from asyncio')
    code = code.replace('client.raw', 'client.async_raw')
    code = code.replace('class Client', 'class AsyncClient')
    code = code.replace('ClientRaw', 'AsyncClientRaw')

    code = code.replace('with self', 'async with self')

    code = code.replace('def', 'async def')
    code = code.replace('async def __', 'def __')

    code = code.replace('self.com', 'await self.com')
    code = code.replace('self.app', 'await self.app')

    for method in methods:
        code = code.replace(f'self.{method}', f'await self.{method}')
        code = code.replace(f'super().{method}', f'await super().{method}')

    code = DISCLAIMER + code

    write_code(_CLIENT_DIR.joinpath(output_filename), code)
    format_code(_CLIENT_DIR.joinpath(output_filename))
