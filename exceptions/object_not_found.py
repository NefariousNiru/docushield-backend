class ObjectNotFoundError(Exception):
    def __init__(self, message=f"Not Found"):
        self.message = message
        super().__init__(self.message)
