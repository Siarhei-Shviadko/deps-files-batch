from asyncio import Protocol

from ...file import FileStatus
from ...status import BatchStatus

__all__ = ["Status"]


class Status(Protocol):
    file_status: FileStatus
    batch_status: BatchStatus

    def can_be_applied(self, files_statuses: set[FileStatus]) -> bool:
        pass
