import typing as t

from atproto_identity.did.resolver import DidResolver
from atproto_identity.handle.resolver import HandleResolver

if t.TYPE_CHECKING:
    from atproto_identity.cache.base_cache import DidBaseCache


class IdResolver:
    """Identity Resolver.

    This resolver is used to resolve identities.
    DID and Handle identifies are supported.
    """

    def __init__(
        self,
        plc_url: t.Optional[str] = None,
        timeout: t.Optional[float] = None,
        cache: t.Optional['DidBaseCache'] = None,
        backup_nameservers: t.Optional[t.List[str]] = None,
    ) -> None:
        self._handle = HandleResolver(timeout, backup_nameservers)
        self._did = DidResolver(plc_url, timeout, cache)

    @property
    def handle(self) -> HandleResolver:
        """Handle Resolver.

        This resolver is used to resolve handles.
        """
        return self._handle

    @property
    def did(self) -> DidResolver:
        """DID Resolver.

        This resolver is used to resolve DIDs.
        PLC and Web DID methods are supported.
        """
        return self._did
