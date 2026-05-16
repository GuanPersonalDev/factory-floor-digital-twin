class DebugLogger:
    def __init__(self) -> None:
        self.enable = True

    def log(self, msg: str):
        if self._enable:
            print(msg)