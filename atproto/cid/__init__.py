from pydantic import BaseModel

# TODO(MarshalX): implement with pydantic


class CID(BaseModel):
    def encode(self, *_, **__):
        ...

    def decode(self, *_, **__):
        ...
