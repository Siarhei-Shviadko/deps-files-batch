from ...file import FileStatus
from ...status import BatchStatus
from .protocol import Status

__all__ = ["Failed"]


class Failed(Status):
    file_status: FileStatus = FileStatus.FAILED
    batch_status: BatchStatus = BatchStatus.FAILED

    def can_be_applied(self, files_statuses: set[FileStatus]) -> bool:
        return self.file_status in files_statuses
