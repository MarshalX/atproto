# from multiformats import CID as _CID
from pydantic import BaseModel


# CID = _CID


class CID(BaseModel):
    def encode(self, *_, **__):
        ...

    def decode(self, *_, **__):
        ...
