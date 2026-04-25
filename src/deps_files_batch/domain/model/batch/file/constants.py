from .status import FileStatus

__all__ = ["FILE_ERROR_STATUSES"]

FILE_ERROR_STATUSES = frozenset((FileStatus.FAILED, FileStatus.ABORTED))
