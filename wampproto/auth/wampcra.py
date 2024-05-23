import base64
import binascii
import datetime
import hashlib
import hmac
import json
import random

from wampproto import messages, auth


class WAMPCRAAuthenticator(auth.IClientAuthenticator):
    TYPE = "wampcra"

    def __init__(self, authid: str, secret: str, auth_extra: dict = None):
        super().__init__(WAMPCRAAuthenticator.TYPE, authid, auth_extra)
        self._secret = secret

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        signed = sign_wampcra_challenge(challenge.extra["challenge"], self._secret.encode())
        return messages.Authenticate(signed, {})


def utcnow() -> str:
    ts = datetime.datetime.utcnow()
    return f"{ts.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"


def generate_wampcra_challenge(session_id: int, authid: str, authrole: str, provider: str) -> str:
    nonce = binascii.hexlify(random.randbytes(16)).decode()

    data = {
        "nonce": nonce,
        "authprovider": provider,
        "authid": authid,
        "authrole": authrole,
        "authmethod": "wampcra",
        "session": session_id,
        "timestamp": utcnow(),
    }

    return json.dumps(data)


def sign_wampcra_challenge(challenge: str, key: bytes) -> str:
    signature = hmac.new(key, challenge.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def verify_wampcra_signature(signature: str, challenge: str, key: bytes) -> bool:
    try:
        sig_bytes = base64.b64decode(signature)
        local_signature = sign_wampcra_challenge(challenge, key)
    except binascii.Error:
        return False

    return hmac.compare_digest(sig_bytes, base64.b64decode(local_signature))
