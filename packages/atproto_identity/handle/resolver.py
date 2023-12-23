import typing as t


class HandleResolver:
    def __init__(
        self,
        timeout: t.Optional[float] = None,
        backup_nameservers: t.Optional[t.List[str]] = None,
    ) -> None:
        self._timeout = timeout
        self._backup_nameservers = backup_nameservers

    def resolve(self, handle: str) -> t.Optional[dict]:
        raise NotImplementedError

    async def resolve_async(self, handle: str) -> t.Optional[dict]:
        raise NotImplementedError
