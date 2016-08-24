__all__ = [
    'PTCException',
    'PTCInvalidStatusCodeException',
    'PTCInvalidNameException',
    'PTCInvalidEmailException',
    'PTCInvalidPasswordException',
    'PTCInvalidBirthdayException',
    'PTCTwocaptchaException'
]


class PTCException(Exception):
    """Base exception for all PTC Account exceptions"""
    pass


class PTCInvalidStatusCodeException(Exception):
    """Base exception for all PTC Account exceptions"""
    pass


class PTCInvalidNameException(PTCException):
    """Username already in use"""
    pass


class PTCInvalidEmailException(PTCException):
    """Email invalid or already in use"""
    pass


class PTCInvalidPasswordException(PTCException):
    """Password invalid"""
    pass


class PTCInvalidBirthdayException(PTCException):
    """Birthday invalid"""
    pass

class PTCTwocaptchaException(PTCException):
    """2captcha unable to provide service"""
    pass
