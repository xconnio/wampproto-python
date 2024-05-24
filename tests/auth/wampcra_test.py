import json
from datetime import datetime

from wampproto import messages
from wampproto.auth import wampcra

cra_challenge = (
    '{"nonce":"cdcb3b12d56e12825be99f38f55ba43f","authprovider":"provider","authid":"foo",'
    '"authrole":"admin","authmethod":"wampcra","session":123,"timestamp":"2024-05-07T09:25:13.307Z"}'
)

key = "6d9b906ad60d1f4dd796dbadcc2e2252310565ccdc6fe10b289df5684faf2a46"
valid_signature = "DIVL3bKs/Ei91eQyYznzUqEsiTmX705BNEXuicNpi8A="


def test_authenticate():
    authenticator = wampcra.WAMPCRAAuthenticator("authID", key, {})
    challenge = messages.Challenge(wampcra.WAMPCRAAuthenticator.TYPE, {"challenge": cra_challenge})

    authenticate = authenticator.authenticate(challenge)
    assert authenticate.signature == valid_signature


def test_utcnow():
    datetime_string = wampcra.utcnow()
    parsed_datetime = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%fZ")

    assert datetime_string.endswith("Z")
    assert parsed_datetime.tzinfo is None

    delta = datetime.utcnow() - parsed_datetime
    assert abs(delta.total_seconds()) < 1


def test_generate_wampcra_challenge():
    session_id = 123
    authid = "john"
    authrole = "admin"
    provider = "provider"
    challenge = wampcra.generate_wampcra_challenge(session_id, authid, authrole, provider)

    assert challenge is not None
    challenge = json.loads(challenge)

    assert challenge["nonce"] is not None
    assert challenge["authid"] == authid
    assert challenge["authrole"] == authrole
    assert challenge["authprovider"] == provider
    assert challenge["authmethod"] == wampcra.WAMPCRAAuthenticator.TYPE
    assert challenge["session"] == session_id
    assert challenge["timestamp"] is not None


def test_sign_wampcra_challenge():
    signature = wampcra.sign_wampcra_challenge(cra_challenge, key.encode())
    assert signature == valid_signature


def test_verify_wampcra_signature():
    is_valid = wampcra.verify_wampcra_signature(valid_signature, cra_challenge, key.encode())
    assert is_valid


def test_verify_invalid_wampcra_signature():
    signature = "invalid_signature"
    is_valid = wampcra.verify_wampcra_signature(signature, cra_challenge, key.encode())
    assert not is_valid
