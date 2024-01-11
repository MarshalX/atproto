from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1

from atproto_crypto.algs.base_alg import AlgBase
from atproto_crypto.consts import P256_JWT_ALG


class P256(AlgBase):
    NAME = P256_JWT_ALG

    def __init__(self) -> None:
        super().__init__(SECP256R1())
