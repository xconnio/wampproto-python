from typing import Any


class ApplicationError(RuntimeError):
    def __init__(self, message: str, args: list[Any], kwargs: dict[str, Any]):
        if args is not None:
            super().__init__(*args)
        self.message = message
        self._args = args
        self.kwargs = kwargs

    def __str__(self):
        err = self.message

        if self._args:
            args = ", ".join(str(arg) for arg in self._args)
            err += f": {args}"

        if self.kwargs:
            kwargs = ", ".join(f"{key}={value}" for key, value in self.kwargs.items())
            err += f": {kwargs}"

        return err
