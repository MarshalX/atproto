from dataclasses import dataclass


@dataclass
class AtprotoData:
    did: str
    signing_key: str
    handle: str
    pds: str
