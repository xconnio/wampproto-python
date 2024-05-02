from wampproto import idgen, types, messages


class Dealer:
    def __init__(self):
        self.registrations_by_procedure: dict[str, dict[int, int]] = {}
        self.registrations_by_session: dict[int, dict[int, str]] = {}
        self.pending_calls: dict[int, dict[int, int]] = {}

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

            callee: int = 0
            registration: int = 0
            for reg_id, session in registrations.items():
                registration = reg_id
                callee = session
                break

            if callee not in self.pending_calls:
                self.pending_calls[callee] = {}

            self.pending_calls[callee][message.request_id] = session_id
            invocation = messages.Invocation(
                request_id=message.request_id,
                registration_id=registration,
                args=message.args,
                kwargs=message.kwargs,
            )

            return types.MessageWithRecipient(invocation, callee)
        elif isinstance(message, messages.Yield):
            calls = self.pending_calls[session_id]
            if calls is None or len(calls) == 0:
                raise ValueError(f"no pending calls for session {session_id}")

            caller = calls[message.request_id]
            del self.pending_calls[session_id][message.request_id]

            result = messages.Result(request_id=message.request_id, args=message.args, kwargs=message.kwargs)
            return types.MessageWithRecipient(result, caller)
        elif isinstance(message, messages.Register):
            if session_id not in self.registrations_by_session:
                raise ValueError(f"cannot register, session {session_id} doesn't exist")

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

            unregistered = messages.UnRegistered(message.request_id)
            return types.MessageWithRecipient(unregistered, session_id)
        else:
            raise ValueError("message type not supported")
