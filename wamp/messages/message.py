class Message:
    MESSAGE_TYPE = None

    @staticmethod
    def serialize(msg: list):
        raise NotImplementedError()

    def deserialize(self):
        raise NotImplementedError()
