import typing as t

from atproto_core.exceptions import AtProtocolError

from atproto_client.models.common import XrpcError

if t.TYPE_CHECKING:
    from atproto_client.request import Response


_DEFAULT_LOGING_REQUIRED_ERROR_MESSAGE = 'To perform this action, you must be logged in. Use the `login` method first.'
_MAX_ERROR_CONTENT_LENGTH = 200


def _get_error_details(content: t.Optional[t.Union[t.Dict[str, t.Any], bytes, XrpcError]]) -> str:
    """Build a human-readable summary of the error content of a response.

    Args:
        content: Content of the error response.

    Returns:
        Summary of the error content. Empty string if there is no content.
    """
    if content is None:
        return ''

    if isinstance(content, XrpcError):
        return f'{content.error}: {content.message}' if content.message else content.error

    details = repr(content)
    if len(details) > _MAX_ERROR_CONTENT_LENGTH:
        return f'{details[:_MAX_ERROR_CONTENT_LENGTH]}...'

    return details


class ModelError(AtProtocolError): ...


class ModelFieldNotFoundError(ModelError): ...


class RequestErrorBase(AtProtocolError):
    def __init__(self, response: t.Optional['Response'] = None) -> None:
        self.response: t.Optional[Response] = response

    def __str__(self) -> str:
        """Summarize the error response. The full response is available in the :attr:`response` attribute."""
        if self.response is None:
            return super().__str__()

        details = _get_error_details(self.response.content)

        return f'{self.response.status_code} {details}' if details else str(self.response.status_code)


class NetworkError(RequestErrorBase): ...


class InvokeTimeoutError(NetworkError): ...


class UnauthorizedError(RequestErrorBase): ...


class RequestException(RequestErrorBase): ...


class BadRequestError(RequestErrorBase): ...


class LoginRequiredError(AtProtocolError):
    def __init__(self, message: t.Optional[str] = _DEFAULT_LOGING_REQUIRED_ERROR_MESSAGE) -> None:
        super().__init__(message)
