import binascii

import nacl.signing
from nacl.encoding import HexEncoder

from wampproto import messages
from wampproto.auth.auth import IClientAuthenticator, CLIENT_ROLES


class CryptoSignAuthenticator(IClientAuthenticator):
    TYPE = "cryptosign"

    def __init__(self, authid: str, auth_extra: dict, private_key: str):
        super().__init__()
        self._authid = authid
        self._auth_extra = auth_extra
        self._private_key = nacl.signing.SigningKey(binascii.a2b_hex(private_key))

        if "pubkey" not in self._auth_extra:
            public_key = self._private_key.verify_key.encode(HexEncoder).decode()
            self._auth_extra["pubkey"] = public_key

    def details(self) -> dict:
        return {
            "authmethods": [CryptoSignAuthenticator.TYPE],
            "authid": self._authid,
            "authextra": self._auth_extra,
            "roles": CLIENT_ROLES,
        }

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        challenge_hex = challenge.extra.get("challenge")
        if challenge_hex is None:
            raise ValueError("challenge string missing in extra")

        raw_challenge = binascii.a2b_hex(challenge_hex)
        signed = self._private_key.sign(raw_challenge, HexEncoder).decode()

        return messages.Authenticate(signed + challenge_hex, {})
