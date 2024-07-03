import pytest

from tests.interoptests.helpers import run_command
from wampproto.auth import wampcra as cra_auth

TEST_SECRET = "private"


@pytest.mark.asyncio
async def test_generate_challenge():
    challenge = cra_auth.generate_wampcra_challenge(1, "anonymous", "anonymous", "static")

    sign_command = f"wampproto auth cra sign-challenge '{challenge}' {TEST_SECRET}"
    signature = await run_command(sign_command)

    verify_command = f"wampproto auth cra verify-signature '{challenge}' {signature.strip()} {TEST_SECRET}"
    await run_command(verify_command)


@pytest.mark.asyncio
async def test_sign_cryptosign_challenge():
    generate_challenge_command = "wampproto auth cra generate-challenge 1 anonymous anonymous static"
    challenge = await run_command(generate_challenge_command)

    signature = cra_auth.sign_wampcra_challenge(challenge, TEST_SECRET.encode())

    verify_command = f"wampproto auth cra verify-signature '{challenge}' {signature.strip()} {TEST_SECRET}"
    await run_command(verify_command)


@pytest.mark.asyncio
async def test_verify_cryptosign_signature():
    generate_challenge_command = "wampproto auth cra generate-challenge 1 anonymous anonymous static"
    challenge = await run_command(generate_challenge_command)

    sign_command = f"wampproto auth cra sign-challenge '{challenge}' {TEST_SECRET}"
    signature = await run_command(sign_command)

    is_verified = cra_auth.verify_wampcra_signature(signature.strip(), challenge.strip(), TEST_SECRET.encode())
    assert is_verified
