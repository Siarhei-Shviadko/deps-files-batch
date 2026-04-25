from dataclasses import dataclass
from typing import TypeAlias

from ...shared import Event

__all__ = ["BatchCreated"]

FileId: TypeAlias = str


@dataclass
class BatchCreated(Event):
    id: str
    name: str
    group_id: str | None
    files: list[FileId]
