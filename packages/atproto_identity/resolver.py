from atproto_identity.did.resolver import DidResolver
from atproto_identity.handle.resolver import HandleResolver


class IdResolver:
    def __init__(self) -> None:
        self._handle = HandleResolver()
        self._did = DidResolver()

    @property
    def handle(self) -> HandleResolver:
        return self._handle

    @property
    def did(self) -> DidResolver:
        return self._did
