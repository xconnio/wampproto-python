from typing import Callable


class ValidationSpec:
    def __init__(self, min_length: int, max_length: int, spec: dict[int, Callable]) -> None:
        self.min_length = min_length
        self.max_length = max_length
        self.spec = spec
