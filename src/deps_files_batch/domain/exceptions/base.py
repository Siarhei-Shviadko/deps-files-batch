__all__ = ["BatchException", "NotFoundError", "IllegalArgument", "LimitExceeded", "BusinessException"]


class BatchException(Exception):
    code = "files_batch_exception"


class BusinessException(BatchException):
    code = "business_exception"


class NotFoundError(BusinessException):
    code = "not_found_error"


class IllegalArgument(BatchException):
    code = "illegal_argument"


class LimitExceeded(BatchException):
    code = "limit_exceeded"
