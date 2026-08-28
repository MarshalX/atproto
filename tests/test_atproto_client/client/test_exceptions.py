from atproto_client import exceptions
from atproto_client.models.common import XrpcError
from atproto_client.request import Response


def _response(content: object, status_code: int = 400) -> Response:
    return Response(success=False, status_code=status_code, content=content, headers={'content-type': 'text/plain'})


def test_error_message_from_xrpc_error() -> None:
    content = XrpcError(error='InvalidRequest', message='grapheme too big (maximum 300, got 1000)')

    assert str(exceptions.BadRequestError(_response(content))) == (
        '400 InvalidRequest: grapheme too big (maximum 300, got 1000)'
    )


def test_error_message_from_xrpc_error_without_message() -> None:
    assert str(exceptions.UnauthorizedError(_response(XrpcError(error='ExpiredToken', message=None), 401))) == (
        '401 ExpiredToken'
    )


def test_error_message_from_raw_content() -> None:
    assert str(exceptions.NetworkError(_response(b'Bad Gateway', 502))) == "502 b'Bad Gateway'"


def test_error_message_from_too_long_raw_content() -> None:
    message = str(exceptions.RequestException(_response(b'x' * 500, 500)))

    assert message.startswith('500 ')
    assert message.endswith('...')
    assert len(message) < 500


def test_error_message_without_content() -> None:
    assert str(exceptions.RequestException(_response(None, 500))) == '500'


def test_error_message_without_response() -> None:
    assert str(exceptions.NetworkError()) == ''


def test_error_keeps_response() -> None:
    response = _response(XrpcError(error='InvalidRequest', message='oops'))
    exception = exceptions.BadRequestError(response)

    assert exception.response is response
    assert exception.args == (response,)
