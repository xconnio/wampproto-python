from dataclasses import dataclass

from wampproto import idgen, types, messages

OPTION_RECEIVE_PROGRESS = "receive_progress"
OPTION_PROGRESS = "progress"


@dataclass
class PendingInvocation:
    request_id: int
    caller_id: int
    callee_id: int
    progress: bool
    receive_progress: bool


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
        self.call_to_invocation_id: dict[tuple[int, int], int] = {}
        self.sessions: dict[int, types.SessionDetails] = {}

        self.idgen = idgen.SessionScopeIDGenerator()

    def add_session(self, details: types.SessionDetails):
        if details.session_id in self.registrations_by_session:
            raise ValueError("cannot add session twice")

        self.registrations_by_session[details.session_id] = {}
        self.sessions[details.session_id] = details

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

        del self.sessions[sid]

    def has_registration(self, procedure: str) -> bool:
        return procedure in self.registrations_by_procedure

    def _add_call(
        self, call_id: int, invocation_id: int, caller_id: int, callee_id: int, progress: bool, receive_progress: bool
    ) -> None:
        self.pending_calls[invocation_id] = PendingInvocation(call_id, caller_id, callee_id, progress, receive_progress)
        self.call_to_invocation_id[(caller_id, call_id)] = invocation_id

    def receive_message(self, session_id: int, message: messages.Message) -> types.MessageWithRecipient:
        if isinstance(message, messages.Call):
            registration = self.registrations_by_procedure.get(message.procedure)
            if registration is None:
                err = messages.Error(
                    messages.ErrorFields(message.TYPE, message.request_id, "wamp.error.no_such_procedure")
                )
                return types.MessageWithRecipient(err, session_id)

            callee_id: int = 0
            for session in registration.registrants.keys():
                callee_id = session
                break

            receive_progress = message.options.get(OPTION_RECEIVE_PROGRESS, False)
            progress = message.options.get(OPTION_PROGRESS, False)
            if progress:
                invocation_id = self.call_to_invocation_id.get((session_id, message.request_id))
                if invocation_id is None:
                    invocation_id = self.idgen.next()
                    self._add_call(message.request_id, invocation_id, session_id, callee_id, progress, receive_progress)
            else:
                invocation_id = self.idgen.next()
                self._add_call(message.request_id, invocation_id, session_id, callee_id, progress, receive_progress)

            details = {}
            if receive_progress:
                details[OPTION_RECEIVE_PROGRESS] = True

            if progress:
                details[OPTION_PROGRESS] = True

            invocation = messages.Invocation(
                messages.InvocationFields(
                    request_id=invocation_id,
                    registration_id=registration.id,
                    args=message.args,
                    kwargs=message.kwargs,
                    details=details,
                    payload=message.payload,
                    serializer=message.payload_serializer,
                )
            )

            return types.MessageWithRecipient(invocation, callee_id)
        elif isinstance(message, messages.Yield):
            try:
                invocation = self.pending_calls[message.request_id]
            except KeyError:
                raise ValueError(f"no pending calls for session {session_id}")

            if session_id != invocation.callee_id:
                raise ValueError(f"received unexpected yield from session={session_id}")

            details = {}
            receive_progress = message.options.get(OPTION_PROGRESS, False)
            if receive_progress and invocation.receive_progress:
                details.update({OPTION_PROGRESS: receive_progress})
            else:
                del self.pending_calls[message.request_id]
                del self.call_to_invocation_id[(invocation.caller_id, invocation.request_id)]

            result = messages.Result(
                messages.ResultFields(
                    request_id=invocation.request_id, args=message.args, kwargs=message.kwargs, details=details
                )
            )
            return types.MessageWithRecipient(result, invocation.caller_id)
        elif isinstance(message, messages.Register):
            if session_id not in self.registrations_by_session:
                raise ValueError(f"cannot register, session {session_id} doesn't exist")

            registration = self.registrations_by_procedure.get(message.procedure)
            if registration is None:
                registration = Registration(self.idgen.next(), message.procedure, {session_id: session_id})
                self.registrations_by_procedure[message.procedure] = registration
                self.registrations_by_session[session_id][registration.id] = registration
            else:
                # TODO: implement shared registrations.
                registered = messages.Error(
                    messages.ErrorFields(
                        messages.Register.TYPE, message.request_id, "wamp.error.procedure_already_exists"
                    )
                )
                return types.MessageWithRecipient(registered, session_id)

            registered = messages.Registered(messages.RegisteredFields(message.request_id, registration.id))
            return types.MessageWithRecipient(registered, session_id)
        elif isinstance(message, messages.Unregister):
            registrations = self.registrations_by_session.get(session_id)
            if registrations is None:
                raise ValueError(f"cannot unregister, session {session_id} doesn't exist")

            registration = registrations.get(message.registration_id)
            if registration is None:
                raise ValueError(
                    f"cannot unregister, session {session_id} haven't registered for {message.registration_id}"
                )

            try:
                registration.registrants.pop(session_id)
            except KeyError:
                raise ValueError(f"cannot unregister, session {session_id} haven't registered for {registration.id}")

            if len(registration.registrants) == 0:
                del registrations[message.registration_id]
                del self.registrations_by_procedure[registration.procedure]

            self.registrations_by_session[session_id] = registrations

            unregistered = messages.Unregistered(messages.UnregisteredFields(message.request_id))
            return types.MessageWithRecipient(unregistered, session_id)
        elif isinstance(message, messages.Error):
            if message.message_type != messages.Invocation.TYPE:
                raise ValueError("dealer: only expected to receive error in response to invocation")

            pending = self.pending_calls.pop(message.request_id, None)
            if pending is None:
                raise ValueError(f"dealer: no pending invocation for {message.request_id}")

            err_msg = messages.Error(
                messages.ErrorFields(
                    messages.Call.TYPE, pending.request_id, message.uri, message.args, message.kwargs, message.details
                )
            )
            return types.MessageWithRecipient(err_msg, pending.caller_id)
        else:
            raise ValueError("message type not supported")
