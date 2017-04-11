class Error(Exception):
    pass

class Unavailable(Error):
    pass

class QubeError(Error):
    def __init__(self, code, message):
        self.code = code
        self.message = message

class InvalidTokenError(QubeError):
    pass
