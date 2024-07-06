import pytest

from wampproto import messages
from wampproto.dealer import Dealer, OPTION_RECEIVE_PROGRESS, OPTION_PROGRESS
from wampproto.types import SessionDetails


def test_add_and_remove_session():
    dealer = Dealer()
    details = SessionDetails(1, "realm1", "authid", "authrole")

    dealer.add_session(details)

    # Adding duplicate session should raise an exception
    with pytest.raises(ValueError) as exc:
        dealer.add_session(details)

    assert str(exc.value) == "cannot add session twice"

    dealer.remove_session(details.session_id)

    # Removing non-existing session should raise an exception
    with pytest.raises(ValueError) as exc:
        dealer.remove_session(3)

    assert str(exc.value) == "cannot remove non-existing session"


def test_register_procedure():
    dealer = Dealer()
    details = SessionDetails(1, "realm1", "authid", "authrole")
    procedure_name = "io.xconn.test"

    dealer.add_session(details)

    register = messages.Register(messages.RegisterFields(1, procedure_name))
    message_with_recipient = dealer.receive_message(details.session_id, register)

    assert message_with_recipient.recipient == details.session_id
    assert isinstance(message_with_recipient.message, messages.Registered)

    # Check registration by procedure
    has_registration = dealer.has_registration(procedure_name)
    assert has_registration

    # Register with invalid sessionID
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(2, register)

    assert str(exc.value) == "cannot register, session 2 doesn't exist"

    # Register again with same procedure
    err_with_recipient = dealer.receive_message(details.session_id, register)
    assert err_with_recipient.recipient == details.session_id

    err_message: messages.Error = err_with_recipient.message
    assert err_message.request_id == register.request_id
    assert err_message.message_type == messages.Register.TYPE
    assert err_message.uri == "wamp.error.procedure_already_exists"


def test_call_procedure_and_receive_yield():
    dealer = Dealer()
    details = SessionDetails(1, "realm1", "authid", "authrole")
    procedure_name = "io.xconn.test"
    dealer.add_session(details)

    # Register a procedure
    register = messages.Register(messages.RegisterFields(1, procedure_name))
    dealer.receive_message(details.session_id, register)

    call = messages.Call(messages.CallFields(2, procedure_name))
    message_with_recipient = dealer.receive_message(details.session_id, call)

    assert message_with_recipient.recipient == details.session_id
    assert isinstance(message_with_recipient.message, messages.Invocation)

    # Call a non-existing procedure
    invalid_call_message = messages.Call(messages.CallFields(3, "invalid"))
    error_msg_with_recipient = dealer.receive_message(details.session_id, invalid_call_message)

    assert error_msg_with_recipient.recipient == details.session_id
    assert isinstance(error_msg_with_recipient.message, messages.Error)

    # Process yield message correctly
    invocation = message_with_recipient.message
    yield_message = messages.Yield(messages.YieldFields(invocation.request_id))
    result_msg_with_recipient = dealer.receive_message(details.session_id, yield_message)

    assert result_msg_with_recipient.recipient == details.session_id
    assert isinstance(result_msg_with_recipient.message, messages.Result)

    # Receive yield for non-pending invocations
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(details.session_id, yield_message)

    assert str(exc.value) == f"no pending calls for session {details.session_id}"

    # Receive yield with invalid sessionID
    msg = dealer.receive_message(details.session_id, call).message
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(3, messages.Yield(messages.YieldFields(msg.request_id)))

    assert str(exc.value) == "received unexpected yield from session=3"


def test_unregister_procedure_not_registered():
    dealer = Dealer()
    details = SessionDetails(1, "realm1", "authid", "authrole")
    dealer.add_session(details)

    unregister = messages.Unregister(messages.UnregisterFields(details.session_id, 1))
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(details.session_id, unregister)

    assert str(exc.value) == f"cannot unregister, session {details.session_id} haven't registered for 1"


def test_unregister_procedure():
    dealer = Dealer()
    details = SessionDetails(1, "realm1", "authid", "authrole")
    procedure_name = "io.xconn.test"
    dealer.add_session(details)

    # Register a procedure
    register = messages.Register(messages.RegisterFields(1, procedure_name))
    dealer.receive_message(details.session_id, register)

    unregister = messages.Unregister(messages.UnregisterFields(2, 1))
    messages_with_recipient = dealer.receive_message(details.session_id, unregister)
    assert messages_with_recipient.recipient == details.session_id
    assert isinstance(messages_with_recipient.message, messages.Unregistered)

    # Check registration by procedure
    has_registration = dealer.has_registration(procedure_name)
    assert not has_registration

    # Unregister with invalid sessionID
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(2, unregister)

    assert str(exc.value) == "cannot unregister, session 2 doesn't exist"

    # Unregister with invalid registrationID
    invalid_unregister = messages.Unregister(messages.UnregisterFields(3, 3))
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(details.session_id, invalid_unregister)

    assert str(exc.value) == f"cannot unregister, session {details.session_id} haven't registered for 3"


def test_receive_invalid_message():
    dealer = Dealer()
    session_id = 1
    procedure_name = "io.xconn.test"
    subscribe = messages.Subscribe(messages.SubscribeFields(session_id, procedure_name))
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(session_id, subscribe)

    assert str(exc.value) == "message type not supported"


def test_progressive_call_results():
    dealer = Dealer()
    callee_details = SessionDetails(1, "realm1", "authid", "authrole")
    caller_details = SessionDetails(2, "realm1", "authid", "authrole")
    dealer.add_session(callee_details)
    dealer.add_session(caller_details)

    register = messages.Register(messages.RegisterFields(1, "foo.bar"))
    dealer.receive_message(callee_details.session_id, register)

    call = messages.Call(messages.CallFields(2, "foo.bar", options={OPTION_RECEIVE_PROGRESS: True}))
    msg = dealer.receive_message(caller_details.session_id, call)
    assert isinstance(msg.message, messages.Invocation)
    assert msg.message.details.get(OPTION_RECEIVE_PROGRESS)

    for _ in range(10):
        yield_ = messages.Yield(messages.YieldFields(msg.message.request_id, options={OPTION_PROGRESS: True}))
        msg = dealer.receive_message(callee_details.session_id, yield_)
        assert isinstance(msg.message, messages.Result)
        assert msg.message.request_id == call.request_id
        assert msg.message.options.get(OPTION_PROGRESS)

    yield_ = messages.Yield(messages.YieldFields(msg.message.request_id))
    msg = dealer.receive_message(callee_details.session_id, yield_)
    assert isinstance(msg.message, messages.Result)
    assert msg.message.request_id == call.request_id
    assert msg.message.options.get(OPTION_PROGRESS, False) is False

    yield_ = messages.Yield(messages.YieldFields(msg.message.request_id))
    with pytest.raises(ValueError) as exc:
        dealer.receive_message(callee_details.session_id, yield_)

    assert str(exc.value).startswith("no pending calls for session")


def test_progressive_call_invocations():
    dealer = Dealer()
    callee_details = SessionDetails(1, "realm1", "authid", "authrole")
    caller_details = SessionDetails(2, "realm1", "authid", "authrole")
    dealer.add_session(callee_details)
    dealer.add_session(caller_details)

    register = messages.Register(messages.RegisterFields(1, "foo.bar"))
    dealer.receive_message(callee_details.session_id, register)

    call = messages.Call(messages.CallFields(2, "foo.bar", options={OPTION_PROGRESS: True}))
    msg = dealer.receive_message(caller_details.session_id, call)
    assert isinstance(msg.message, messages.Invocation)
    assert msg.message.details.get(OPTION_PROGRESS)
    invocation_request_id = msg.message.request_id

    for _ in range(10):
        call = messages.Call(messages.CallFields(2, "foo.bar", options={OPTION_PROGRESS: True}))
        msg = dealer.receive_message(caller_details.session_id, call)
        assert isinstance(msg.message, messages.Invocation)
        assert msg.message.details.get(OPTION_PROGRESS)
        assert msg.message.request_id == invocation_request_id

    call = messages.Call(messages.CallFields(2, "foo.bar"))
    msg = dealer.receive_message(caller_details.session_id, call)
    assert isinstance(msg.message, messages.Invocation)
    assert OPTION_PROGRESS not in msg.message.details
