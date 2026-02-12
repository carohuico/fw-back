import traceback

from scripts.errors.exception_codes import (
    ValidationExceptions,
)


class FormulationToolErrors(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        print(traceback.format_exc())

    """
    Base Error Class
    """


class ErrorCodes:
    ERR001 = "ERR001 - Operating Time is greater than Planned Time"
    ERR002 = "ERR002 - Zero Values are not allowed"
    ERR003 = "ERR003 - Operating Time is less than Productive Time"
    ERR004 = "ERR004 - Rejected Units is greater than Total Units"



class Exceptions(ValidationExceptions):
    pass


class AuthenticationError(FormulationToolErrors):
    """
    JWT Authentication Error
    """


class ErrorMessages:
    ERROR001 = "Authentication Failed. Please verify token"
    ERROR002 = "Signature Expired"
    ERROR003 = "Signature Not Valid"


class FailedAttemptsExceeded(FormulationToolErrors):
    pass


class AzureActiveDirectoryAuthenticationError(Exception):
    pass


class InvalidAuthorizationToken(Exception):
    pass


class AzureSAMLAuthenticationError(Exception):
    pass


class AzureSAMLConfigurationError(Exception):
    pass


class AzureADUserDoesNotExists(Exception):
    pass


class UserNotFound(FormulationToolErrors):
    pass


class IllegalToken(FormulationToolErrors):
    pass


class InvalidPasswordError(FormulationToolErrors):
    pass


class PasswordExpiredError(Exception):
    pass


class NotAuthenticatedError(FormulationToolErrors):
    pass

class UnauthorizedError(Exception):
    pass


class NameExistsError(Exception):
    pass


class CustomError(Exception):
    pass


class ExistingDataError(Exception):
    pass


class FileExtensionError(Exception):
    pass


class ProjectDataError(Exception):
    pass


class CustomerIdError(Exception):
    pass


class ColumnNameError(Exception):
    pass
