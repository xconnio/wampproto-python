class Message:
    MESSAGE_TYPE = None

    @staticmethod
    def parse(msg: list):
        raise NotImplementedError()

    def marshal(self):
        raise NotImplementedError()
