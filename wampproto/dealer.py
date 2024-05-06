from dataclasses import dataclass

from wampproto import idgen, types, messages


@dataclass
class PendingInvocation:
    request_id: int
    caller_id: int
    callee_id: int


@dataclass
class Registration:
    id: int
    procedure: str
    registrants: dict[int, int]
    invocation_policy: str | None = None


class Dealer:
    def __init__(self):
        self.registrations_by_procedure: dict[str, Registration] = {}
        self.registrations_by_session: dict[int, dict[int, Registration]] = {}
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
        for registration_id, registration in registrations.items():
            registration = self.registrations_by_procedure[registration.procedure]
            if sid in registration.registrants:
                del registration.registrants[sid]

            if len(registration.registrants) == 0:
                del self.registrations_by_procedure[registration.procedure]

    def has_registration(self, procedure: str) -> bool:
        return procedure in self.registrations_by_procedure

    def receive_message(self, session_id: int, message: messages.Message) -> types.MessageWithRecipient:
        if isinstance(message, messages.Call):
            registration = self.registrations_by_procedure.get(message.uri)
            if registration is None:
                err = messages.Error(message.TYPE, message.request_id, "wamp.error.no_such_procedure")
                return types.MessageWithRecipient(err, session_id)

            callee_id: int = 0
            for session in registration.registrants.keys():
                callee_id = session
                break

            request_id = self.id_gen.next()
            self.pending_calls[request_id] = PendingInvocation(message.request_id, session_id, callee_id)
            invocation = messages.Invocation(
                request_id=request_id,
                registration_id=registration.id,
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

            registration = self.registrations_by_procedure.get(message.uri)
            if registration is None:
                registration = Registration(self.id_gen.next(), message.uri, {session_id: session_id})
                self.registrations_by_procedure[message.uri] = registration
                self.registrations_by_session[session_id][registration.id] = registration
            else:
                # TODO: implement shared registrations.
                registered = messages.Error(
                    messages.Register.TYPE, message.request_id, "wamp.error.procedure_already_exists"
                )
                return types.MessageWithRecipient(registered, session_id)

            registered = messages.Registered(message.request_id, registration.id)
            return types.MessageWithRecipient(registered, session_id)
        elif isinstance(message, messages.UnRegister):
            registrations = self.registrations_by_session.get(session_id)
            if registrations is None:
                raise ValueError(f"cannot unregister, session {session_id} doesn't exist")

            registration = registrations.get(message.registration_id)
            try:
                registration.registrants.pop(session_id)
            except KeyError:
                raise ValueError(f"cannot unregister, session {session_id} haven't registered for {registration.id}")

            if len(registration.registrants) == 0:
                del registrations[message.registration_id]
                del self.registrations_by_procedure[registration.procedure]

            self.registrations_by_session[session_id] = registrations

            unregistered = messages.UnRegistered(message.request_id)
            return types.MessageWithRecipient(unregistered, session_id)
        else:
            raise ValueError("message type not supported")
