import binascii

import nacl.signing

from wampproto import messages
from wampproto.auth import cryptosign
from wampproto.messages.challenge import ChallengeFields

private_key_hex = "c7e8c1f8f16ec37f53ed153f8afb7f18469b051f1d24dbea2097a2a104b2e9db"
public_key_hex = "c53e4f2756a52ca1ed5cd00da108b3ed7bcffe6294e78283521e5102824f52d3"
challenge = "a1d483092ec08960fedbaed2bc1d411568a59077b794210e251bd3abb1563f7c"
signature = (
    "01d4b7a515b1023196e2bbb57c5202da72088f99a17eaeed62ba97ebf93381b92"
    "a3e8430154667e194d971fb41b090a9338b92021c39271e910a8ea072fe950c"
)


def test_authenticate():
    authenticator = cryptosign.CryptoSignAuthenticator("authID", private_key_hex)
    assert authenticator.authid == "authID"
    assert authenticator.auth_extra["pubkey"] == public_key_hex

    challenge_obj = messages.Challenge(ChallengeFields("cryptosign", {"challenge": challenge}))
    authenticate = authenticator.authenticate(challenge_obj)
    expected_signature = signature + challenge
    assert authenticate.signature == expected_signature


def test_generate_cryptosign_challenge():
    challenge = cryptosign.generate_cryptosign_challenge()
    assert isinstance(challenge, str)
    assert len(challenge) == 64


def test_sign_cryptosign_challenge():
    signed = cryptosign.sign_cryptosign_challenge(challenge, nacl.signing.SigningKey(binascii.a2b_hex(private_key_hex)))
    assert signed == signature


def test_verify_cryptosign_signature():
    is_valid = cryptosign.verify_cryptosign_signature(signature + challenge, binascii.unhexlify(public_key_hex))
    assert is_valid
