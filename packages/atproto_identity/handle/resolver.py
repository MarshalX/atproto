import typing as t

import dns.asyncresolver
import dns.resolver
import httpx
from dns.exception import DNSException

from atproto_identity.exceptions import DidNotFoundError

_ATPROTO_SUBDOMAIN = '_atproto'
_ATPROTO_RECORD_TYPE = 'TXT'
_ATPROTO_TXT_PREFIX = 'did='
_ATPROTO_TXT_PREFIX_LEN = len(_ATPROTO_TXT_PREFIX)
_ATPROTO_WELL_KNOWN_PATH = '/.well-known/atproto-did'
_ATPROTO_DID_PREFIX = 'did:'


class _HandleResolverBase:
    @staticmethod
    def _find_text_record(answers: dns.resolver.Answer) -> t.Optional[str]:
        for answer in answers:
            for item in answer.strings:
                value = item.decode('UTF-8')
                if value.startswith(_ATPROTO_TXT_PREFIX):
                    return value[_ATPROTO_TXT_PREFIX_LEN:]

        return None

    @staticmethod
    def _get_qname(handle: str) -> str:
        return f'{_ATPROTO_SUBDOMAIN}.{handle}'

    @staticmethod
    def _get_did_from_text_response(text: str) -> t.Optional[str]:
        lines = text.splitlines()
        if not lines:
            return None

        first_line = lines[0].strip()
        if first_line.startswith(_ATPROTO_DID_PREFIX):
            return first_line

        return None


class HandleResolver(_HandleResolverBase):
    def __init__(
        self,
        timeout: t.Optional[float] = None,
        backup_nameservers: t.Optional[t.List[str]] = None,
    ) -> None:
        self._timeout = timeout
        self._backup_nameservers = backup_nameservers  # TODO(MarshalX): implement

        self._dns_resolver = dns.resolver
        self._http_client = httpx.Client()

    def resolve(self, handle: str) -> t.Optional[str]:
        dns_resolve = self.resolve_dns(handle)
        if dns_resolve:
            return dns_resolve

        http_resolve = self.resolve_http(handle)
        if http_resolve:
            return http_resolve

        # TODO(MarshalX): add resolve DNS backup nameservers
        return None

    def ensure_resolve(self, handle: str) -> str:
        did = self.resolve(handle)
        if not did:
            raise DidNotFoundError(f'Unable to resolve handle: {handle}')

        return did

    def resolve_dns(self, handle: str) -> t.Optional[str]:
        try:
            answers = self._dns_resolver.resolve(self._get_qname(handle), _ATPROTO_RECORD_TYPE, lifetime=self._timeout)
        except DNSException:
            return None

        return self._find_text_record(answers)

    def resolve_http(self, handle: str) -> t.Optional[str]:
        try:
            response = self._http_client.get(f'https://{handle}{_ATPROTO_WELL_KNOWN_PATH}', timeout=self._timeout)
            response.raise_for_status()
            return self._get_did_from_text_response(response.text)
        except httpx.HTTPError:
            return None


class AsyncHandleResolver(_HandleResolverBase):
    def __init__(
        self,
        timeout: t.Optional[float] = None,
        backup_nameservers: t.Optional[t.List[str]] = None,
    ) -> None:
        self._timeout = timeout
        self._backup_nameservers = backup_nameservers  # TODO(MarshalX): implement

        self._dns_resolver = dns.asyncresolver
        self._http_client = httpx.AsyncClient()

    async def resolve(self, handle: str) -> t.Optional[str]:
        dns_resolve = await self.resolve_dns(handle)
        if dns_resolve:
            return dns_resolve

        http_resolve = await self.resolve_http(handle)
        if http_resolve:
            return http_resolve

        # TODO(MarshalX): add resolve DNS backup nameservers
        return None

    async def ensure_resolve(self, handle: str) -> str:
        did = await self.resolve(handle)
        if not did:
            raise DidNotFoundError(f'Unable to resolve handle: {handle}')

        return did

    async def resolve_dns(self, handle: str) -> t.Optional[str]:
        try:
            answers = await self._dns_resolver.resolve(
                self._get_qname(handle), _ATPROTO_RECORD_TYPE, lifetime=self._timeout
            )
        except DNSException:
            return None

        return self._find_text_record(answers)

    async def resolve_http(self, handle: str) -> t.Optional[str]:
        try:
            response = await self._http_client.get(f'https://{handle}{_ATPROTO_WELL_KNOWN_PATH}', timeout=self._timeout)
            response.raise_for_status()
            return self._get_did_from_text_response(response.text)
        except httpx.HTTPError:
            return None
