from atproto import Client
from atproto.exceptions import (
    BadRequestError,
    InvokeTimeoutError,
    RateLimitExceededError,
    RequestErrorBase,
    UnauthorizedError,
)
from atproto_client.models.common import XrpcError

USERNAME = 'example.com'
PASSWORD = 'hunter2'  # noqa: S105 never hardcode your password in a real application


def describe(error: RequestErrorBase) -> str:
    """Summarize what the server said about a failed request."""
    content = error.response.content if error.response else None
    if isinstance(content, XrpcError):
        return f'{content.error}: {content.message}'

    # a non-JSON body (an HTML error page from a proxy, for example) arrives as raw bytes
    return repr(content)


def main() -> None:
    client = Client()

    try:
        client.login(USERNAME, PASSWORD)
    except UnauthorizedError as e:
        print('Login rejected:', describe(e))
        return
    except RateLimitExceededError as e:
        # createSession is rate limited by handle: 30/5 min, 300/day
        print('Too many logins. Retry at:', e.reset_at)
        return
    except InvokeTimeoutError:
        print('The PDS did not answer in time.')
        return

    try:
        client.com.atproto.identity.resolve_handle({'handle': 'not a handle'})
    except BadRequestError as e:
        print('Status code:', e.response.status_code)
        print('Server said:', describe(e))


if __name__ == '__main__':
    main()
