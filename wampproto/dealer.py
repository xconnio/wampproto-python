from dataclasses import dataclass

from wampproto import idgen, types, messages


@dataclass
class PendingInvocation:
    request_id: int
    caller_id: int
    callee_id: int


class Dealer:
    def __init__(self):
        self.registrations_by_procedure: dict[str, dict[int, int]] = {}
        self.registrations_by_session: dict[int, dict[int, str]] = {}
        self.pending_calls: dict[int, PendingInvocation] = {}

        self.id_gen = idgen.SessionScopeIDGenerator()

    def add_session(self, sid: int):
        if sid in self.registrations_by_session:
            raise ValueError("cannot add session twice")

        self.registrations_by_session[sid] = {}

    def remove_session(self, sid: int):
        if sid not in self.registrations_by_session:
            raise ValueError("cannot remove non-existing session")

        registrations = self.registrations_by_session.pop(sid)
        for k, v in registrations.items():
            del self.registrations_by_procedure[v][k]
            if len(self.registrations_by_procedure[v]) == 0:
                del self.registrations_by_procedure[v]

    def has_registration(self, procedure: str):
        return len(self.registrations_by_procedure[procedure]) != 0

    def receive_message(self, session_id: int, message: messages.Message) -> types.MessageWithRecipient:
        if isinstance(message, messages.Call):
            registrations = self.registrations_by_procedure.get(message.uri)
            if registrations is None or len(registrations) == 0:
                err = messages.Error(message.TYPE, message.request_id, "wamp.error.no_such_procedure")
                return types.MessageWithRecipient(err, session_id)

            callee_id: int = 0
            registration: int = 0
            for reg_id, session in registrations.items():
                registration = reg_id
                callee_id = session
                break

            request_id = self.id_gen.next()
            self.pending_calls[request_id] = PendingInvocation(message.request_id, session_id, callee_id)
            invocation = messages.Invocation(
                request_id=request_id,
                registration_id=registration,
                args=message.args,
                kwargs=message.kwargs,
            )

            return types.MessageWithRecipient(invocation, callee_id)
        elif isinstance(message, messages.Yield):
            try:
                invocation = self.pending_calls.pop(message.request_id)
            except KeyError:
                raise ValueError(f"no pending calls for session {session_id}")

            if session_id != invocation.callee_id:
                raise ValueError(f"received unexpected yield from session={session_id}")

            result = messages.Result(request_id=invocation.request_id, args=message.args, kwargs=message.kwargs)
            return types.MessageWithRecipient(result, invocation.caller_id)
        elif isinstance(message, messages.Register):
            if session_id not in self.registrations_by_session:
                raise ValueError(f"cannot register, session {session_id} doesn't exist")

            if message.uri in self.registrations_by_procedure:
                registered = messages.Error(
                    messages.Register.TYPE, message.request_id, "wamp.error.procedure_already_exists"
                )
                return types.MessageWithRecipient(registered, session_id)

            registration_id = self.id_gen.next()
            self.registrations_by_session[session_id][registration_id] = message.uri
            if message.uri not in self.registrations_by_procedure:
                self.registrations_by_procedure[message.uri] = {}

            self.registrations_by_procedure[message.uri][registration_id] = session_id

            registered = messages.Registered(message.request_id, registration_id)
            return types.MessageWithRecipient(registered, session_id)
        elif isinstance(message, messages.UnRegister):
            if session_id not in self.registrations_by_session:
                raise ValueError(f"cannot unregister, session {session_id} doesn't exist")

            registrations = self.registrations_by_session[session_id]
            procedure = registrations.get(message.registration_id)
            del self.registrations_by_session[session_id][message.registration_id]
            del self.registrations_by_procedure[procedure][message.registration_id]
            if len(self.registrations_by_procedure[procedure]) == 0:
                del self.registrations_by_procedure[procedure]

            unregistered = messages.UnRegistered(message.request_id)
            return types.MessageWithRecipient(unregistered, session_id)
        else:
            raise ValueError("message type not supported")
