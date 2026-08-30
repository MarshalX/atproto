import httpx
from atproto import Client, Request, models

USERNAME = 'example.com'
PASSWORD = 'hunter2'  # noqa: S105 never hardcode your password in a real application


def main() -> None:
    # retry connection failures, and give slow uploads more than the default 5 seconds
    transport = httpx.HTTPTransport(retries=3)
    request = Request(timeout=httpx.Timeout(30.0), transport=transport)

    client = Client(base_url='https://bsky.social', request=request)
    client.login(USERNAME, PASSWORD)

    # low-level invoke: returns the raw Response dataclass instead of a parsed model
    response = client.invoke_query(
        'com.atproto.identity.resolveHandle',
        params=models.ComAtprotoIdentityResolveHandle.Params(handle='marshal.dev'),
        output_encoding='application/json',
    )

    print('Success:', response.success)
    print('Status code:', response.status_code)
    print('Content type:', response.headers.get('content-type'))
    print('Content:', response.content)

    # point the client at another PDS; "/xrpc" is appended for you
    client.update_base_url('https://pds.example.com')

    client.request.close()


if __name__ == '__main__':
    main()
