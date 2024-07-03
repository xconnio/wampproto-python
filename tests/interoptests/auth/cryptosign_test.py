import binascii
import pytest
import nacl.signing

from tests.interoptests.helpers import run_command
from wampproto.auth import cryptosign as cryptosign_auth

TEST_PUBLIC_KEY = "2b7ec216daa877c7f4c9439db8a722ea2340eacad506988db2564e258284f895"
TEST_PRIVATE_KEY = "022b089bed5ab78808365e82dd12c796c835aeb98b4a5a9e099d3e72cb719516"


@pytest.mark.asyncio
async def test_generate_challenge():
    challenge = cryptosign_auth.generate_cryptosign_challenge()

    signature = await run_command(
        f"wampproto auth cryptosign sign-challenge {challenge} {TEST_PRIVATE_KEY}"
    )

    await run_command(
        f"wampproto auth cryptosign verify-signature {signature.strip()} {TEST_PUBLIC_KEY}"
    )


@pytest.mark.asyncio
async def test_sign_cryptosign_challenge():
    challenge = await run_command("wampproto auth cryptosign generate-challenge")
    challenge = challenge.strip()

    private_key = nacl.signing.SigningKey(binascii.a2b_hex(TEST_PRIVATE_KEY))

    signature = cryptosign_auth.sign_cryptosign_challenge(challenge, private_key)

    # Combine the signature and the challenge as a single hex string
    full_signature = signature + challenge

    await run_command(
        f"wampproto auth cryptosign verify-signature {full_signature} {TEST_PUBLIC_KEY}"
    )


@pytest.mark.asyncio
async def test_verify_cryptosign_signature():
    challenge = await run_command("wampproto auth cryptosign generate-challenge")

    signature = await run_command(
        f"wampproto auth cryptosign sign-challenge {challenge.strip()} {TEST_PRIVATE_KEY}"
    )

    public_key_bytes = binascii.unhexlify(TEST_PUBLIC_KEY)

    is_verified = cryptosign_auth.verify_cryptosign_signature(signature.strip(), public_key_bytes)
    assert is_verified
