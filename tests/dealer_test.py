import pytest

from wampproto import messages
from wampproto.dealer import Dealer


def test_add_and_remove_session():
    dealer = Dealer()
    session_id = 2

    dealer.add_session(session_id)

    # Adding duplicate session should raise an exception
    with pytest.raises(ValueError) as exc:
        dealer.add_session(session_id)

    assert str(exc.value) == "cannot add session twice"

    dealer.remove_session(session_id)

    # Removing non-existing session should raise an exception
    with pytest.raises(ValueError) as exc:
        dealer.remove_session(3)

    assert str(exc.value) == "cannot remove non-existing session"


def test_register_procedure():
    dealer = Dealer()
    session_id = 1
    procedure_name = "io.xconn.test"

    dealer.add_session(session_id)

    register = messages.Register(session_id, procedure_name)
    message_with_recipient = dealer.receive_message(session_id, register)

    assert message_with_recipient.recipient == session_id
    assert isinstance(message_with_recipient.message, messages.Registered)

    # Check registration by procedure
    has_registration = dealer.has_registration(procedure_name)
    assert has_registration

    # Register with invalid sessionID
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(2, register)

    assert str(exc.value) == "cannot register, session 2 doesn't exist"

    # Register again with same procedure
    err_with_recipient = dealer.receive_message(session_id, register)
    assert err_with_recipient.recipient == session_id

    err_message: messages.Error = err_with_recipient.message
    assert err_message.request_id == register.request_id
    assert err_message.message_type == messages.Register.TYPE
    assert err_message.uri == "wamp.error.procedure_already_exists"


def test_call_procedure_and_receive_yield():
    dealer = Dealer()
    session_id = 1
    procedure_name = "io.xconn.test"
    dealer.add_session(1)

    # Register a procedure
    register = messages.Register(session_id, procedure_name)
    dealer.receive_message(session_id, register)

    call = messages.Call(session_id, procedure_name)
    message_with_recipient = dealer.receive_message(session_id, call)

    assert message_with_recipient.recipient == session_id
    assert isinstance(message_with_recipient.message, messages.Invocation)

    # Call a non-existing procedure
    invalid_call_message = messages.Call(session_id, "invalid")
    error_msg_with_recipient = dealer.receive_message(session_id, invalid_call_message)

    assert error_msg_with_recipient.recipient == session_id
    assert isinstance(error_msg_with_recipient.message, messages.Error)

    # Process yield message correctly
    invocation = message_with_recipient.message
    yield_message = messages.Yield(invocation.request_id)
    result_msg_with_recipient = dealer.receive_message(session_id, yield_message)

    assert result_msg_with_recipient.recipient == session_id
    assert isinstance(result_msg_with_recipient.message, messages.Result)

    # Receive yield for non-pending invocations
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(session_id, yield_message)

    assert str(exc.value) == f"no pending calls for session {session_id}"

    # Receive yield with invalid sessionID
    msg = dealer.receive_message(session_id, call).message
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(3, messages.Yield(msg.request_id))

    assert str(exc.value) == "received unexpected yield from session=3"


def test_unregister_procedure_not_registered():
    dealer = Dealer()
    session_id = 1
    dealer.add_session(session_id)

    unregister = messages.UnRegister(session_id, 1)
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(session_id, unregister)

    assert str(exc.value) == f"cannot unregister, session {session_id} haven't registered for 1"


def test_unregister_procedure():
    dealer = Dealer()
    session_id = 1
    procedure_name = "io.xconn.test"
    dealer.add_session(session_id)

    # Register a procedure
    register = messages.Register(session_id, procedure_name)
    dealer.receive_message(session_id, register)

    unregister = messages.UnRegister(session_id, 1)
    messages_with_recipient = dealer.receive_message(session_id, unregister)
    assert messages_with_recipient.recipient == session_id
    assert isinstance(messages_with_recipient.message, messages.UnRegistered)

    # Check registration by procedure
    has_registration = dealer.has_registration(procedure_name)
    assert not has_registration

    # Unregister with invalid sessionID
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(2, unregister)

    assert str(exc.value) == f"cannot unregister, session 2 doesn't exist"

    # Unregister with invalid registrationID
    invalid_unregister = messages.UnRegister(session_id, 3)
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(session_id, invalid_unregister)

    assert str(exc.value) == f"cannot unregister, session {session_id} haven't registered for 3"


def test_receive_invalid_message():
    dealer = Dealer()
    session_id = 1
    procedure_name = "io.xconn.test"
    subscribe = messages.Subscribe(session_id, procedure_name)
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(session_id, subscribe)

    assert str(exc.value) == "message type not supported"
