import binascii

import nacl.signing
from nacl.encoding import HexEncoder

from wampproto import messages, auth


class CryptoSignAuthenticator(auth.IClientAuthenticator):
    TYPE = "cryptosign"

    def __init__(self, authid: str, auth_extra: dict, private_key: str):
        self._private_key = nacl.signing.SigningKey(binascii.a2b_hex(private_key))

        if "pubkey" not in self._auth_extra:
            public_key = self._private_key.verify_key.encode(HexEncoder).decode()
            self._auth_extra["pubkey"] = public_key

        super().__init__(CryptoSignAuthenticator.TYPE, authid, auth_extra)

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        challenge_hex = challenge.extra.get("challenge")
        if challenge_hex is None:
            raise ValueError("challenge string missing in extra")

        raw_challenge = binascii.a2b_hex(challenge_hex)
        signed = self._private_key.sign(raw_challenge, HexEncoder).decode()

        return messages.Authenticate(signed + challenge_hex, {})
