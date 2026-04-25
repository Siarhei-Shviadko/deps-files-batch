from typing import TYPE_CHECKING, Callable, Sequence

from ..status import BatchStatus
from .statuses import (
    Aborted,
    Completed,
    Exported,
    Failed,
    New,
    Processing,
    Review,
    Status,
)

if TYPE_CHECKING:
    from ..batch import Batch

__all__ = ["StateManager"]


class StateManager:
    statuses_by_priority: Sequence[Status] = (
        New(),
        Completed(),
        Exported(),
        Aborted(),
        Failed(),
        Review(),
        Processing(),
    )

    def __init__(self, batch: "Batch", new_status_setter: Callable[[BatchStatus], None]) -> None:
        self._batch = batch
        self.set_new_status = new_status_setter

    def analyze(self) -> None:
        files_statuses = {file.status for file in self._batch}

        for status in self.statuses_by_priority:
            if status.can_be_applied(files_statuses):
                if self._batch.status == status.batch_status:
                    return

                self.set_new_status(status.batch_status)

                return
