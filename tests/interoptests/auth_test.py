import asyncio
import binascii
import subprocess
import pytest
import nacl.signing

from wampproto.auth import cryptosign as cryptosign_auth


TEST_PUBLIC_KEY = "2b7ec216daa877c7f4c9439db8a722ea2340eacad506988db2564e258284f895"
TEST_PRIVATE_KEY = "022b089bed5ab78808365e82dd12c796c835aeb98b4a5a9e099d3e72cb719516"


async def run_command(command: str):
    process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    assert process.returncode == 0, stderr.decode()

    return stdout.decode().strip()


@pytest.mark.asyncio
async def test_generate_challenge():
    challenge = cryptosign_auth.generate_cryptosign_challenge()

    signature = await run_command(
        f"wampproto auth cryptosign sign-challenge --challenge {challenge} --private-key {TEST_PRIVATE_KEY}"
    )

    await run_command(
        f"wampproto auth cryptosign verify-signature --signature {signature.strip()} --public-key {TEST_PUBLIC_KEY}"
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
        f"wampproto auth cryptosign verify-signature --signature {full_signature} --public-key {TEST_PUBLIC_KEY}"
    )


@pytest.mark.asyncio
async def test_verify_cryptosign_signature():
    challenge = await run_command("wampproto auth cryptosign generate-challenge")

    signature = await run_command(
        f"wampproto auth cryptosign sign-challenge --challenge {challenge.strip()} --private-key {TEST_PRIVATE_KEY}"
    )

    public_key_bytes = binascii.unhexlify(TEST_PUBLIC_KEY)

    is_verified = cryptosign_auth.verify_cryptosign_signature(signature.strip(), public_key_bytes)
    assert is_verified
