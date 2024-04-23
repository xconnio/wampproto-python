import random

ID_MAX = 1 << 53


def generate_session_id():
    return random.randint(1, ID_MAX)


class SessionScopeIDGenerator:
    def __init__(self):
        super().__init__()
        self.id: int = 0

    def next(self):
        if self.id == ID_MAX:
            self.id = 0

        self.id += 1
        return self.id
