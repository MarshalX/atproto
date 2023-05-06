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
    ]

    code = code.replace('client.raw', 'client.async_raw')
    code = code.replace('class Client', 'class AsyncClient')
    code = code.replace('ClientRaw', 'AsyncClientRaw')

    code = code.replace('def', 'async def')
    code = code.replace('async def __', 'def __')

    code = code.replace('self.com', 'await self.com')
    code = code.replace('self.bsky', 'await self.bsky')

    for method in methods:
        code = code.replace(f'self.{method}', f'await self.{method}')

    code = DISCLAIMER + code

    write_code(_CLIENT_DIR.joinpath(output_filename), code)
    format_code(_CLIENT_DIR.joinpath(output_filename))


if __name__ == '__main__':
    gen_client('client.py', 'async_client.py')
