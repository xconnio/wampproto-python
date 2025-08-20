import json

import pytest

from wampproto import messages, WAMPSession, uris, serializers


@pytest.fixture
def session():
    return WAMPSession(serializer=serializers.JSONSerializer())


@pytest.fixture
def register_procedure(session: WAMPSession):
    # register a procedure
    session.send_message(messages.Register(messages.RegisterFields(1, "foo.bar")))

    # confirm registration
    session.receive_message(messages.Registered(messages.RegisteredFields(1, 1)))


def test_register(session: WAMPSession):
    # Send Register message and receive Registered message
    register = messages.Register(messages.RegisterFields(2, "io.xconn.test"))
    to_send = session.send_message(register)
    assert to_send == f'[{messages.Register.TYPE}, {register.request_id}, {dict()}, "{register.procedure}"]'

    registered = messages.Registered(messages.RegisteredFields(2, 3))
    received = session.receive_message(registered)
    assert received == registered


def test_register_error(session: WAMPSession):
    # Send Register message and receive Error for that Register
    register = messages.Register(messages.RegisterFields(2, "io.xconn.test"))
    session.send_message(register)

    register_err = messages.Error(
        messages.ErrorFields(messages.Register.TYPE, register.request_id, uris.INVALID_ARGUMENT)
    )
    received = session.receive_message(register_err)
    assert received == register_err


def test_call(session: WAMPSession, register_procedure):
    # call the newly registered procedure
    call = messages.Call(messages.CallFields(2, "foo.bar"))
    session.send_message(call)

    invocation = messages.Invocation(messages.InvocationFields(2, 1))
    assert invocation == session.receive_message(invocation)

    yield_msg = messages.Yield(messages.YieldFields(2))
    received = session.send_message(yield_msg)
    assert received == "[70, 2, {}]"

    result = messages.Result(messages.ResultFields(2))
    received = session.receive_message(result)
    assert received == result


def test_call_error(session: WAMPSession):
    # Receive error message correctly
    # Send Call message and receive Error for that Call
    call = messages.Call(messages.CallFields(1, "io.xconn.test"))
    session.send_message(call)

    call_err = messages.Error(messages.ErrorFields(messages.Call.TYPE, call.request_id, uris.INVALID_ARGUMENT))
    received = session.receive_message(call_err)
    assert received == call_err


def test_unregister(session: WAMPSession, register_procedure):
    # Send Unregister message and receive Unregistered message
    unregister = messages.Unregister(messages.UnregisterFields(1, 1))
    to_send = session.send_message(unregister)
    assert to_send == f"[{messages.Unregister.TYPE}, {unregister.request_id}, {unregister.registration_id}]"

    unregistered = messages.Unregistered(messages.UnregisteredFields(1))
    received = session.receive_message(unregistered)
    assert received == unregistered


def test_unregister_error(session: WAMPSession):
    # Send Unregister message and receive Error for that Unregister
    unregister = messages.Unregister(messages.UnregisterFields(3, 3))
    session.send_message(unregister)

    unregister_err = messages.Error(
        messages.ErrorFields(messages.Unregister.TYPE, unregister.request_id, uris.INVALID_ARGUMENT)
    )
    received = session.receive_message(unregister_err)
    assert received == unregister_err


def test_subscribe(session: WAMPSession):
    subscribe = messages.Subscribe(messages.SubscribeFields(7, "topic"))
    to_send = session.send_message(subscribe)
    assert to_send == f'[{messages.Subscribe.TYPE}, {subscribe.request_id}, {subscribe.options}, "{subscribe.topic}"]'

    subscribed = messages.Subscribed(messages.SubscribedFields(7, 8))
    received = session.receive_message(subscribed)
    assert received == subscribed

    event = messages.Event(messages.EventFields(8, 6))
    received_event = session.receive_message(event)
    assert received_event == event


def test_subscribe_error(session: WAMPSession):
    # Send Subscribe message and receive Error for that Subscribe
    subscribe = messages.Subscribe(messages.SubscribeFields(7, "topic"))
    session.send_message(subscribe)

    subscribe_error = messages.Error(
        messages.ErrorFields(messages.Subscribe.TYPE, subscribe.request_id, uris.INVALID_URI)
    )
    received = session.receive_message(subscribe_error)
    assert received == subscribe_error


def test_unsubscribe(session: WAMPSession):
    # subscribe to a topic
    session.send_message(messages.Subscribe(messages.SubscribeFields(7, "topic")))

    # confirm subscribed
    session.receive_message(messages.Subscribed(messages.SubscribedFields(7, 8)))

    unsubscribe = messages.Unsubscribe(messages.UnsubscribeFields(8, 8))
    to_send = session.send_message(unsubscribe)
    assert to_send == f"[{messages.Unsubscribe.TYPE}, {unsubscribe.request_id}, {unsubscribe.subscription_id}]"

    unsubscribed = messages.Unsubscribed(messages.UnsubscribedFields(8))
    received = session.receive_message(unsubscribed)
    assert received == unsubscribed


def test_unsubscribe_error(session: WAMPSession):
    # Send Unsubscribe message and receive Error for that Unsubscribe
    unsubscribe = messages.Unsubscribe(messages.UnsubscribeFields(8, 8))
    session.send_message(unsubscribe)

    unsubscribe_error = messages.Error(
        messages.ErrorFields(messages.Unsubscribe.TYPE, unsubscribe.request_id, uris.INVALID_URI)
    )
    received = session.receive_message(unsubscribe_error)
    assert received == unsubscribe_error


def test_publish(session: WAMPSession):
    # Send Publish message with acknowledge true and receive Published message
    publish = messages.Publish(messages.PublishFields(6, "topic", options={"acknowledge": True}))
    to_send = session.send_message(publish)
    assert (
        to_send == f'[{messages.Publish.TYPE}, {publish.request_id}, {json.dumps(publish.options)}, "{publish.topic}"]'
    )

    published = messages.Published(messages.PublishedFields(6, 6))
    received = session.receive_message(published)
    assert received == published


def test_publish_error(session: WAMPSession):
    # Send Publish message and receive Error for that Publish
    publish = messages.Publish(messages.PublishFields(6, "topic", options={"acknowledge": True}))
    session.send_message(publish)

    publish_err = messages.Error(messages.ErrorFields(messages.Publish.TYPE, publish.request_id, uris.INVALID_URI))
    received = session.receive_message(publish_err)
    assert received == publish_err


def test_error(session: WAMPSession):
    # Send error message correctly
    error = messages.Error(messages.ErrorFields(messages.Invocation.TYPE, 10, uris.PROCEDURE_ALREADY_EXISTS))
    to_send = session.send_message(error)
    assert (
        to_send
        == f'[{messages.Error.TYPE}, {messages.Invocation.TYPE}, {error.request_id}, {error.details}, "{error.uri}"]'
    )


def test_exceptions():
    session = WAMPSession(serializer=serializers.JSONSerializer())

    # Send Yield for unknown invocation
    invalid_yield = messages.Yield(messages.YieldFields(5))
    with pytest.raises(ValueError) as exc:
        session.send_message(invalid_yield)

    assert str(exc.value) == "cannot yield for unknown invocation request"

    # Send error for invalid message
    invalid_error = messages.Error(messages.ErrorFields(messages.Register.TYPE, 10, "uris.PROCEDURE_ALREADY_EXISTS"))
    with pytest.raises(ValueError) as exc:
        session.send_message(invalid_error)

    assert str(exc.value) == "send only supported for invocation error"

    # Send invalid message
    invalid_message = messages.Registered(messages.RegisteredFields(11, 12))
    with pytest.raises(ValueError) as exc:
        session.send_message(invalid_message)

    assert str(exc.value) == f"unknown message type {type(invalid_message)}"

    # Receive invalid message
    with pytest.raises(ValueError) as exc:
        msg = messages.Register(messages.RegisterFields(100, "io.xconn.test"))
        session.receive_message(msg)

    assert str(exc.value) == f"unknown message {type(msg)}"

    # Receive error for invalid message
    with pytest.raises(ValueError) as exc:
        msg = messages.Error(messages.ErrorFields(messages.Registered.TYPE, 100, uris.INVALID_ARGUMENT))
        session.receive_message(msg)

    assert str(exc.value) == f"unknown error message type {type(msg)}"

    # Receive error invalid Call id
    with pytest.raises(ValueError) as exc:
        session.receive_message(messages.Error(messages.ErrorFields(messages.Call.TYPE, 100, uris.INVALID_ARGUMENT)))

    assert str(exc.value) == f"received {messages.Error.TEXT} for invalid call request"

    # Receive error Register id
    with pytest.raises(ValueError) as exc:
        session.receive_message(
            messages.Error(messages.ErrorFields(messages.Register.TYPE, 100, uris.INVALID_ARGUMENT))
        )

    assert str(exc.value) == f"received {messages.Error.TEXT} for invalid register request"

    # Receive error invalid Unregister id
    with pytest.raises(ValueError) as exc:
        session.receive_message(
            messages.Error(messages.ErrorFields(messages.Unregister.TYPE, 100, uris.INVALID_ARGUMENT))
        )

    assert str(exc.value) == f"received {messages.Error.TEXT} for invalid unregister request"

    # Receive error invalid Subscribe id
    with pytest.raises(ValueError) as exc:
        session.receive_message(
            messages.Error(messages.ErrorFields(messages.Subscribe.TYPE, 100, uris.INVALID_ARGUMENT))
        )

    assert str(exc.value) == f"received {messages.Error.TEXT} for invalid subscribe request"

    # Receive error invalid Unsubscribe id
    with pytest.raises(ValueError) as exc:
        session.receive_message(
            messages.Error(messages.ErrorFields(messages.Unsubscribe.TYPE, 100, uris.INVALID_ARGUMENT))
        )

    assert str(exc.value) == f"received {messages.Error.TEXT} for invalid unsubscribe request"

    # Receive error invalid Publish id
    with pytest.raises(ValueError) as exc:
        session.receive_message(messages.Error(messages.ErrorFields(messages.Publish.TYPE, 100, uris.INVALID_ARGUMENT)))

    assert str(exc.value) == f"received {messages.Error.TEXT} for invalid publish request"
