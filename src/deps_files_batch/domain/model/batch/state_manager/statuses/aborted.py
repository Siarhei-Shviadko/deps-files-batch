from ...file import FileStatus
from ...status import BatchStatus
from .protocol import Status

__all__ = ["Aborted"]


class Aborted(Status):
    file_status: FileStatus = FileStatus.ABORTED
    batch_status: BatchStatus = BatchStatus.ABORTED

    def can_be_applied(self, files_statuses: set[FileStatus]) -> bool:
        return self.file_status in files_statuses
