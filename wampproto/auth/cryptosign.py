import binascii
import random

import nacl.signing
from nacl.encoding import HexEncoder

from wampproto import messages, auth


class CryptoSignAuthenticator(auth.IClientAuthenticator):
    TYPE = "cryptosign"

    def __init__(self, authid: str, private_key: str, auth_extra: dict | None = None):
        self._private_key = nacl.signing.SigningKey(binascii.a2b_hex(private_key))
        self._auth_extra = auth_extra

        if "pubkey" not in self._auth_extra:
            public_key = self._private_key.verify_key.encode(HexEncoder).decode()
            self._auth_extra["pubkey"] = public_key

        super().__init__(CryptoSignAuthenticator.TYPE, authid, auth_extra)

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        challenge_hex = challenge.extra.get("challenge")
        if challenge_hex is None:
            raise ValueError("challenge string missing in extra")

        signed = sign_cryptosign_challenge(challenge_hex, self._private_key)

        return messages.Authenticate(signed + challenge_hex, {})


def generate_cryptosign_challenge() -> str:
    raw_bytes = random.randbytes(32)
    return binascii.hexlify(raw_bytes).decode("ascii")


def sign_cryptosign_challenge(challenge: str, private_key: nacl.signing.SigningKey) -> str:
    raw_challenge = binascii.a2b_hex(challenge)
    return private_key.sign(raw_challenge, HexEncoder).decode()


def verify_cryptosign_signature(signature: str, public_key: bytes) -> bool:
    verifying_key = nacl.signing.VerifyKey(public_key)
    verifying_key.verify(binascii.unhexlify(signature[:-64]))
    return True
