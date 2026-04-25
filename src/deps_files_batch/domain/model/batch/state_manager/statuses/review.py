from ...file import FileStatus
from ...status import BatchStatus
from .protocol import Status

__all__ = ["Review"]


class Review(Status):
    file_status: FileStatus = FileStatus.REVIEW
    batch_status: BatchStatus = BatchStatus.REVIEW

    def can_be_applied(self, files_statuses: set[FileStatus]) -> bool:
        return self.file_status in files_statuses
