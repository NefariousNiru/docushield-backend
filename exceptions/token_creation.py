class TokenCreationError(Exception):
    def __init__(self, message="Failed to create auth token"):
        self.message = message
        super().__init__(self.message)
