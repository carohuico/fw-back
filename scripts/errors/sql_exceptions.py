class FormulationToolException(Exception):
    pass


class SQLException(FormulationToolException):
    pass


class ErrorMessages:
    UNKNOWN = "Unknown Error occurred"
    ERR001 = "Configurations not available, please verify the database."
    ERR002 = "Data Not Found"
    ERR003 = "Error while reading initial parameters. Ensure Type is set with valid arguments."
    ERR004 = "Failed to add Annotation"
    CONNECTION_EXCEPTION = "Exception while closing connection: "

class SQLConnectionException(SQLException):
    pass


class SQLQueryException(SQLException):
    pass


class SQLEncryptionException(SQLException):
    pass


class SQLRecordInsertionException(SQLQueryException):
    pass


class SQLFindException(SQLQueryException):
    pass


class SQLDeleteException(SQLQueryException):
    pass


class SQLUpdateException(SQLQueryException):
    pass


class SQLUnknownDatatypeException(SQLEncryptionException):
    pass


class SQLDistictQueryException(SQLException):
    pass


class SQLFindAndReplaceException(SQLException):
    pass


class SQLObjectDeserializationException(SQLException):
    pass
