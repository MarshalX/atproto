import typing as t


class HandleResolver:
    def resolve(self, handle: str) -> t.Optional[dict]:
        raise NotImplementedError

    async def resolve_async(self, handle: str) -> t.Optional[dict]:
        raise NotImplementedError
