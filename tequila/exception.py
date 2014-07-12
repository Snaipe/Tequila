

class TequilaException(Exception):
    def __init__(self, message=''):
        self.message = message


class UnhandledException(Exception):
    pass