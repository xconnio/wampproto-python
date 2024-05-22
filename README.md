# wampproto-python
Sans-IO implementation of the WAMP protocol in Python

This is a library that could be used to build a [WAMP](https://wamp-proto.org/index.html) client or server. It operates
on strings and bytes. A WAMP client can be split into two parts.

* Session establishment
* Session management.

Assuming we have a websocket connection established to a WAMP server using sub protocol `wamp.2.json`. The first
"message" is going to be sent by the client as HELLO
```python
from wampproto.joiner import Joiner

j = Joiner("realm1")
# this doesn't actually send the message, it just returns the
# payload that needs to be sent over websocket.
hello = j.send_hello()

ws.send_str(hello)
response = ws.receive_str()

to_send = j.receive(response)
if to_send is None:
    # if there is nothing to send, this means
    # the server returned WELCOME.
    print(j.get_session_details())
```

Now that the session is established, we could instantiate a `WAMPSession` instance
to handle further messages.
```python
from wampproto.session import WAMPSession
from wampproto.messages import Call
from wampproto.idgen import SessionScopeIDGenerator

session = WAMPSession()
idgen = SessionScopeIDGenerator()

call = Call(idgen.next(), "foo.bar")
to_send = session.send_message(call)

ws.send_str(to_send)

incoming_payload = ws.receive_str()
result = session.receive(incoming_payload)
print(result)
```
