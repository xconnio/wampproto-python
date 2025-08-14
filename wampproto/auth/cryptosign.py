import binascii
import random

import nacl.signing
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

from wampproto import messages, auth
from wampproto.messages.authenticate import AuthenticateFields


class CryptoSignAuthenticator(auth.IClientAuthenticator):
    TYPE = "cryptosign"

    def __init__(self, authid: str, private_key: str, auth_extra: dict | None = None):
        super().__init__(CryptoSignAuthenticator.TYPE, authid, auth_extra)
        self._private_key = nacl.signing.SigningKey(binascii.a2b_hex(private_key))

        if "pubkey" not in self._auth_extra:
            public_key = self._private_key.verify_key.encode(HexEncoder).decode()
            self._auth_extra["pubkey"] = public_key

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        challenge_hex = challenge.extra.get("challenge")
        if challenge_hex is None:
            raise ValueError("challenge string missing in extra")

        signed = sign_cryptosign_challenge(challenge_hex, self._private_key)

        return messages.Authenticate(AuthenticateFields(signed, {}))


def generate_cryptosign_challenge() -> str:
    raw_bytes = random.randbytes(32)
    return binascii.hexlify(raw_bytes).decode("ascii")


def sign_cryptosign_challenge(challenge: str, private_key: nacl.signing.SigningKey) -> str:
    raw_challenge = binascii.a2b_hex(challenge)
    return private_key.sign(raw_challenge, HexEncoder).signature.decode() + challenge


def verify_cryptosign_signature(signature: str, public_key: bytes) -> bool:
    try:
        verifying_key = nacl.signing.VerifyKey(public_key)
        verifying_key.verify(binascii.unhexlify(signature))
    except BadSignatureError:
        return False

    return True


def generate_cryptosign_keypair() -> tuple[str, str]:
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key

    private_key_hex = signing_key.encode().hex()
    public_key_hex = verify_key.encode().hex()

    return public_key_hex, private_key_hex
