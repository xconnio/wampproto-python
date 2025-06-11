class ApplicationError(RuntimeError):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(*args)
        self.message = message
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        err = self.message

        if self.args:
            args = ", ".join(str(arg) for arg in self.args)
            err += f": {args}"

        if self.kwargs:
            kwargs = ", ".join(f"{key}={value}" for key, value in self.kwargs.items())
            err += f": {kwargs}"

        return err
