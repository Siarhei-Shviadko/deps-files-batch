from dataclasses import dataclass

from ...shared import Event

__all__ = ["BatchFileStatusUpdated"]


@dataclass
class BatchFileStatusUpdated(Event):
    file_id: str
    status: str
    batch_id: str | None = None
