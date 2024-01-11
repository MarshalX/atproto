from cryptography.hazmat.primitives.asymmetric.ec import SECP256K1

from atproto_crypto.algs.base_alg import AlgBase


class Secp256k1(AlgBase):
    def __init__(self) -> None:
        super().__init__(SECP256K1())
