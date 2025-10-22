import random
import threading

ID_MAX = 1 << 53


def generate_session_id():
    return random.randint(1, ID_MAX)


class SessionScopeIDGenerator:
    def __init__(self, use_lock: bool = False):
        super().__init__()
        self.id: int = 0
        self._use_lock: bool = use_lock
        self._lock = threading.Lock()

    def _next(self) -> int:
        if self.id >= ID_MAX:
            self.id = 0

        self.id += 1
        return self.id


    def next(self) -> int:
        if self._use_lock:
            with self._lock:
                return self._next()
        else:
            return self._next()
