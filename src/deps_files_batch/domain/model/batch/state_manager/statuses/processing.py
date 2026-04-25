from ...file import FileStatus
from ...status import BatchStatus
from .protocol import Status

__all__ = ["Processing"]


class Processing(Status):
    batch_status: BatchStatus = BatchStatus.PROCESSING

    def can_be_applied(self, files_statuses: set[FileStatus]) -> bool:
        return True
