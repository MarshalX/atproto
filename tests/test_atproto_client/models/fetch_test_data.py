import logging
import os
import typing as t

from atproto_client import Client
from atproto_client.request import Request, Response
from pydantic_core import to_json

if t.TYPE_CHECKING:
    from atproto_client.models.common import XrpcError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'test_data')


class LatestResponse:
    def __init__(self, response: Response = None) -> None:
        self._response = response

    def set(self, response: Response) -> None:
        self._response = response

    @property
    def content(self) -> t.Optional[t.Union[dict, bytes, 'XrpcError']]:
        return self._response.content

    @property
    def status_code(self) -> int:
        return self._response.status_code


LATEST_RESPONSE = LatestResponse()


class ProxyRequest(Request):
    def get(self, *args, **kwargs: t.Any) -> Response:
        response = super().get(*args, **kwargs)
        LATEST_RESPONSE.set(response)
        return response

    def post(self, *args, **kwargs: t.Any) -> Response:
        response = super().post(*args, **kwargs)
        LATEST_RESPONSE.set(response)
        return response


class Call(t.NamedTuple):
    name: str
    method: str
    params: t.Optional[dict]


def get_method_by_path(obj: object, path: str) -> callable:
    for part in path.split('.'):
        obj = getattr(obj, part)
    return obj


def get_unique_filename(name: str) -> str:
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if os.path.exists(os.path.join(OUTPUT_DIR, name)):
        i = 1
        while os.path.exists(os.path.join(OUTPUT_DIR, f'{name}_{i}.json')):
            i += 1

        return f'{name}_{i}.json'

    return f'{name}.json'


def get_pretty_json(data: dict) -> str:
    return to_json(data, indent=4).decode('UTF-8')


def save_response(name: str) -> None:
    filename = get_unique_filename(name)
    with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='UTF-8') as f:
        if isinstance(LATEST_RESPONSE.content, dict):
            f.write(get_pretty_json(LATEST_RESPONSE.content))
        else:
            logger.error('Response is not dict. We are not saving it as test data for now.')


def process_latest_response(name: str) -> None:
    save_response(name)


def run_methods(client: Client, methods: t.List[Call]) -> None:
    for call in methods:
        get_method_by_path(client, call.method)(call.params)
        process_latest_response(call.name)


def main() -> None:
    client = Client(request=ProxyRequest())
    client.login(os.environ['USERNAME'], os.environ['PASSWORD'])

    methods_to_run: t.List[Call] = [
        Call(name='resolve_handle', method='com.atproto.identity.resolve_handle', params={'handle': 'bsky.app'}),
        Call(
            name='feed_record',
            method='com.atproto.repo.get_record',
            params={
                'collection': 'app.bsky.feed.generator',
                'repo': 'marshal.dev',
                'rkey': 'atproto',
            },
        ),
        Call(
            name='post_record',
            method='com.atproto.repo.get_record',
            params={'collection': 'app.bsky.feed.post', 'repo': 'test.marshal.dev', 'rkey': '3k2yihcrp6f2c'},
        ),
        Call(
            name='extended_post_record',
            method='com.atproto.repo.get_record',
            params={'collection': 'app.bsky.feed.post', 'repo': 'test.marshal.dev', 'rkey': '3k2yinh52ne2x'},
        ),
        Call(
            name='like_record',
            method='com.atproto.repo.get_record',
            params={'collection': 'app.bsky.feed.like', 'repo': 'test.marshal.dev', 'rkey': '3k5u7c7j7a52v'},
        ),
        Call(
            name='extended_like_record',
            method='com.atproto.repo.get_record',
            params={'collection': 'app.bsky.feed.like', 'repo': 'test.marshal.dev', 'rkey': '3k5u5ammyg72r'},
        ),
        Call(
            name='did_doc', method='com.atproto.repo.describe_repo', params={'repo': 'did:plc:kvwvcn5iqfooopmyzvb4qzba'}
        ),
        Call(
            name='thread_view_post_with_embed_media',
            method='app.bsky.feed.get_post_thread',
            params={
                'uri': 'at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3kaheyt6vpc22',
                'depth': 1,
                'parentHeight': 0,
            },
        ),
        Call(
            name='get_follows',
            method='app.bsky.graph.get_follows',
            params={'actor': 'test.marshal.dev', 'limit': 10},
        ),
    ]

    run_methods(client, methods_to_run)


if __name__ == '__main__':
    main()
