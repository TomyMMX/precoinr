class ErrorWithMessage(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class CouldNotCommitPayment(ErrorWithMessage):
    pass

class NonExistingCryptoCurency(ErrorWithMessage):
    pass

class NonExistingFiatCurency(ErrorWithMessage):
    pass

class UnsuportedCurrency(ErrorWithMessage):
    pass

class UnsuportedCurrency(ErrorWithMessage):
    pass

class DifferenceBetweenCCandFiatTooLarge(ErrorWithMessage):
    pass

class InsufficientFunds(ErrorWithMessage):
    pass