from dataclasses import dataclass

from wampproto import messages, types, idgen


@dataclass
class Subscription:
    id: int
    topic: str
    subscribers: dict[int, int]


class Broker:
    def __init__(self):
        super().__init__()
        self.subscriptions_by_topic: dict[str, Subscription] = {}
        self.subscriptions_by_session: dict[int, dict[int, Subscription]] = {}
        self.sessions: dict[int, types.SessionDetails] = {}
        self.idgen = idgen.SessionScopeIDGenerator()

    def add_session(self, details: types.SessionDetails):
        if details.session_id in self.subscriptions_by_session:
            raise ValueError("cannot add session twice")

        self.subscriptions_by_session[details.session_id] = {}
        self.sessions[details.session_id] = details

    def remove_session(self, sid: int):
        if sid not in self.subscriptions_by_session:
            raise ValueError("cannot remove non-existing session")

        subscriptions = self.subscriptions_by_session.pop(sid)
        for subscription_id, sub in subscriptions.items():
            subscription = self.subscriptions_by_topic[sub.topic]
            if sid in subscription.subscribers:
                del subscription.subscribers[sid]

            if len(subscription.subscribers) == 0:
                del self.subscriptions_by_topic[subscription.topic]

        del self.sessions[sid]

    def has_subscription(self, topic: str):
        return topic in self.subscriptions_by_topic

    def receive_message(self, session_id: int, message: messages.Message) -> types.MessageWithRecipient:
        if isinstance(message, messages.Subscribe):
            if session_id not in self.subscriptions_by_session:
                raise ValueError(f"cannot subscribe, session {session_id} doesn't exist")

            subscription = self.subscriptions_by_topic.get(message.topic)
            if subscription is None:
                subscription = Subscription(self.idgen.next(), message.topic, {session_id: session_id})
                self.subscriptions_by_topic[message.topic] = subscription
            else:
                subscription.subscribers[session_id] = session_id

            self.subscriptions_by_session[session_id][subscription.id] = subscription

            subscribed = messages.Subscribed(messages.SubscribedFields(message.request_id, subscription.id))
            return types.MessageWithRecipient(subscribed, session_id)
        elif isinstance(message, messages.Unsubscribe):
            if session_id not in self.subscriptions_by_session:
                raise ValueError(f"cannot unsubscribe, session {session_id} doesn't exist")

            subscriptions = self.subscriptions_by_session[session_id]
            subscription = subscriptions.get(message.subscription_id)
            if subscription is None:
                raise ValueError(f"cannot unsubscribe, subscription {message.subscription_id} doesn't exist")

            del subscription.subscribers[session_id]
            if len(subscription.subscribers) == 0:
                del self.subscriptions_by_topic[subscription.topic]

            del self.subscriptions_by_session[session_id][message.subscription_id]

            unsubscribed = messages.Unsubscribed(messages.UnsubscribedFields(message.request_id))
            return types.MessageWithRecipient(unsubscribed, session_id)
        else:
            raise ValueError("message type not supported")

    def receive_publish(self, session_id: int, message: messages.Publish) -> types.Publication:
        if session_id not in self.subscriptions_by_session:
            raise ValueError(f"cannot publish, session {session_id} doesn't exist")

        result = types.Publication(recipients=[])
        publication_id = self.idgen.next()

        subscription = self.subscriptions_by_topic.get(message.topic)
        if subscription is not None:
            event = messages.Event(messages.EventFields(subscription.id, publication_id, message.args, message.kwargs))
            result.event = event
            for subscriber_id in subscription.subscribers.keys():
                result.recipients.append(subscriber_id)

        ack = message.options.get("acknowledge", False)
        if ack:
            published = messages.Published(messages.PublishedFields(message.request_id, publication_id))
            result.ack = types.MessageWithRecipient(published, session_id)

        return result
