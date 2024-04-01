from wampproto import messages, WAMPSession


def test_call():
    caller = WAMPSession()
    callee = WAMPSession()

    # send register message
    register = messages.Register(1, "foo.bar")
    callee.send_message(register)

    # confirm registration
    registered = messages.Registered(1, 1)
    assert registered == callee.receive_message(registered)

    # call the newly registered procedure
    call = messages.Call(2, "foo.bar")
    caller.send_message(call)

    invocation = messages.Invocation(2, 1)
    assert invocation == callee.receive_message(invocation)
