from ...file import FileStatus
from ...status import BatchStatus
from .protocol import Status

__all__ = ["New"]


class New(Status):
    file_status: FileStatus = FileStatus.NEW
    batch_status: BatchStatus = BatchStatus.NEW

    def can_be_applied(self, files_statuses: set[FileStatus]) -> bool:
        return len(files_statuses) == 1 and self.file_status in files_statuses
