from typing import Optional

from wampproto import messages, types, idgen


class Broker:
    def __init__(self):
        super().__init__()
        self.subscriptions_by_topic: dict[str, dict[int, int]] = {}
        self.subscriptions_by_session: dict[int, dict[int, str]] = {}
        self.id_gen = idgen.SessionScopeIDGenerator()

    def add_session(self, sid: int):
        if sid in self.subscriptions_by_session:
            raise ValueError("cannot add session twice")

        self.subscriptions_by_session[sid] = {}

    def remove_session(self, sid: int):
        if sid not in self.subscriptions_by_session:
            raise ValueError("cannot remove non-existing session")

        subscription = self.subscriptions_by_session.pop(sid)
        for k, v in subscription.items():
            del self.subscriptions_by_topic[v][k]
            if len(self.subscriptions_by_topic[v]) == 0:
                del self.subscriptions_by_topic[v]

    def has_subscription(self, topic: str):
        return len(self.subscriptions_by_topic[topic]) != 0

    def receive_message(self, session_id: int, message: messages.Message) -> Optional[list[types.MessageWithRecipient]]:
        if isinstance(message, messages.Subscribe):
            if session_id not in self.subscriptions_by_session:
                raise ValueError(f"cannot subscribe, session {session_id} doesn't exist")

            subscription_id = self.id_gen.next()
            self.subscriptions_by_session[session_id][subscription_id] = message.topic
            if message.topic not in self.subscriptions_by_topic:
                self.subscriptions_by_topic[message.topic] = {}

            self.subscriptions_by_topic[message.topic][subscription_id] = session_id

            subscribed = messages.Subscribed(message.request_id, subscription_id)
            return [types.MessageWithRecipient(subscribed, session_id)]
        elif isinstance(message, messages.UnSubscribe):
            if session_id not in self.subscriptions_by_session:
                raise ValueError(f"cannot unsubscribe, session {session_id} doesn't exist")

            subscriptions = self.subscriptions_by_session[session_id]
            topic = subscriptions.get(message.subscription_id)
            if topic is None:
                raise ValueError(f"cannot unsubscribe, subscription {message.subscription_id} doesn't exist")

            del self.subscriptions_by_session[session_id][message.subscription_id]
            del self.subscriptions_by_topic[topic][message.subscription_id]

            unsubscribed = messages.UnSubscribed(message.request_id)
            return [types.MessageWithRecipient(unsubscribed, session_id)]
        elif isinstance(message, messages.Publish):
            if session_id not in self.subscriptions_by_session:
                raise ValueError(f"cannot publish, session {session_id} doesn't exist")

            subscriptions = self.subscriptions_by_topic.get(message.uri, [])
            if len(subscriptions) == 0:
                return None

            publication_id = self.id_gen.next()
            result: list[types.MessageWithRecipient] = []
            for subscription_id, recipient_id in subscriptions.items():
                event = messages.Event(subscription_id, publication_id, message.args, message.kwargs)
                result.append(types.MessageWithRecipient(event, recipient_id))

            return result
        else:
            raise ValueError("message type not supported")
