from dataclasses import dataclass

from ...shared import Event

__all__ = ["BatchStatusUpdated"]


@dataclass
class BatchStatusUpdated(Event):
    id: str
    status: str
