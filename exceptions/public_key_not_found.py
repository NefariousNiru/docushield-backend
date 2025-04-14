class PublicKeyNotFoundError(Exception):
    def __init__(self, message="Failed to find public key"):
        self.message = message
        super().__init__(self.message)
