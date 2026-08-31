import math
import typing as t
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

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
    """Base of every error that comes out of an HTTP request.

    Note:
        :attr:`response` is :obj:`None` when the failure happened before a response arrived,
        which is the case for every transport-level error (:class:`NetworkError` and
        :class:`InvokeTimeoutError` raised from an underlying HTTPX exception).
    """

    def __init__(self, response: t.Optional['Response'] = None) -> None:
        #: Response that carried the error, when one arrived.
        self.response: t.Optional[Response] = response

    def __str__(self) -> str:
        """Summarize the error response. The full response is available in the :attr:`response` attribute."""
        if self.response is None:
            return super().__str__()

        details = _get_error_details(self.response.content)

        return f'{self.response.status_code} {details}' if details else str(self.response.status_code)


class NetworkError(RequestErrorBase):
    """Transport failure, or a status code that is worth retrying the same way (409, 413, 502).

    Note:
        :attr:`~RequestErrorBase.response` is :obj:`None` when raised from a transport failure.
    """


class InvokeTimeoutError(NetworkError):
    """The request did not complete within the timeout of the underlying HTTP client.

    Note:
        :attr:`~RequestErrorBase.response` is always :obj:`None`.
    """


class UnauthorizedError(RequestErrorBase): ...


class RequestException(RequestErrorBase): ...


class BadRequestError(RequestErrorBase): ...


class RateLimitExceededError(RequestException):
    """The server answered with 429. The remaining budget is exposed as attributes.

    Note:
        Inherits :class:`RequestException`, which is what a 429 used to be raised as.

    Example:
        >>> from atproto.exceptions import RateLimitExceededError
        >>>
        >>> try:
        >>>     client.send_post(text='Hello')
        >>> except RateLimitExceededError as e:
        >>>     print('Retry at:', e.reset_at)
    """

    @property
    def limit(self) -> t.Optional[int]:
        """Number of requests the policy allows in the current window (``ratelimit-limit``)."""
        return self._get_int_header('ratelimit-limit')

    @property
    def remaining(self) -> t.Optional[int]:
        """Number of requests left in the current window (``ratelimit-remaining``)."""
        return self._get_int_header('ratelimit-remaining')

    @property
    def reset_at(self) -> t.Optional[datetime]:
        """UTC time at which the current window resets (``ratelimit-reset``)."""
        timestamp = self._get_int_header('ratelimit-reset')
        if timestamp is None:
            return None

        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    @property
    def policy(self) -> t.Optional[str]:
        """Policy the limit comes from, e.g. ``100;w=300`` (``ratelimit-policy``)."""
        return self._get_header('ratelimit-policy')

    @property
    def retry_after(self) -> t.Optional[float]:
        """Seconds to wait before retrying (``retry-after``), or :obj:`None` when not usable.

        Note:
            The header carries either a number of seconds or an HTTP-date. Both are returned as
            seconds from now, never negative. Not every service sends it; prefer :attr:`reset_at`
            when it is absent.
        """
        value = self._get_header('retry-after')
        if value is None:
            return None

        try:
            delay = float(value)
        except ValueError:
            return self._seconds_until_http_date(value)

        return max(delay, 0.0) if math.isfinite(delay) else None

    @staticmethod
    def _seconds_until_http_date(value: str) -> t.Optional[float]:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError):  # 3.9 raises TypeError where later versions raise ValueError
            return None

        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)

        return max((retry_at - datetime.now(timezone.utc)).total_seconds(), 0.0)

    def _get_header(self, name: str) -> t.Optional[str]:
        if self.response is None:
            return None

        return self.response.headers.get(name)

    def _get_int_header(self, name: str) -> t.Optional[int]:
        value = self._get_header(name)
        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            return None


class LoginRequiredError(AtProtocolError):
    def __init__(self, message: t.Optional[str] = _DEFAULT_LOGING_REQUIRED_ERROR_MESSAGE) -> None:
        super().__init__(message)
